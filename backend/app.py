import ast
import collections
import os
import pandas as pd
import pdfplumber
import re
from datetime import datetime as dt
from datetime import timedelta
from flask import Flask
from openai import OpenAI

app = Flask(__name__)
# CORS(app)

def main():

    calendar = collections.defaultdict(dict)
    path, _, files = list(os.walk(os.path.join("syllabus")))[0]
    
    # loop for every pdf file in folder
    for tail in files:
        if tail.lower().endswith('.pdf'):
            pdf = pdfplumber.open(os.path.join(path, tail))

            # get name of class
            name = get_class_name(pdf.pages[0].extract_text())

            # extract table from every page
            tables = []
            for page in pdf.pages:
                table = page.extract_tables()
                
                # if table isn't empty, append table
                if len(table) != 0:
                    tables.append(table)
            
            # if table contains due date, add to list
            due_dates = []
            for table in tables:
                if contains_due_dates(str(table)) == "Yes":
                    due_dates.append(table)
            
            # if responses contain calendar
            if due_dates:
                for table in due_dates:
                    dates = get_dates(table)
                    for pair in dates:
                        date, assignment = pair[0], pair[1]
                        calendar[date][name] = assignment
            else:
            # if response is a list of assignments
                due_dates = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if contains_due_dates(text) == "Yes":
                        due_dates.append(text)

                # if text contains date, parse data and add to calendar
                if due_dates:
                    for text in due_dates:
                        response = text_to_dates(text)
                        data = ast.literal_eval(response)
                        
                for pair in data:
                    date, assignment = pair[0], pair[1]
                    calendar[date][name] = assignment
                    
        elif tail.lower().endswith('.txt'):
            with open(os.path.join(path, tail)) as syllabus:
                txt = syllabus.read()
                # if text contains date, parse data and add to calendar
                if contains_due_dates(txt) == "Yes":
                    # get name of class
                    name = get_class_name(txt)

                    response = text_to_dates(txt)
                    data = ast.literal_eval(response)
                        
                for pair in data:
                    date, assignment = pair[0], pair[1]
                    calendar[date][name] = assignment
    
    # sort calendar by date
    sorted_cal = collections.OrderedDict(sorted(calendar.items(), key=lambda x: dt.strptime(x[0], "%m/%d")))
    
    calendar_to_excel(sorted_cal)


# Members API route
@app.route("/members")
def members():
    return {"members": ["Member 1", "Member 2", "Member3"]} 


# export calendar to excel file
def calendar_to_excel(cal):
    # convert calendar to dataframe, use keys as index  
    df = pd.DataFrame.from_dict(cal, orient="index")

    # sort dates properly using datetime objects
    df.index = pd.to_datetime(df.index, format="%m/%d")
    df = df.sort_index()
    
    # convert the index back to m/d format
    df.index = df.index.strftime("%m/%d")

    # export the datafram to an excel file
    df.to_excel(os.path.join('output', 'output.xlsx'), sheet_name='sheet1', index=True)


# get assingment due dates from a calendar
def get_dates(table) -> list: 
    dates = []

    for i in table:
        for line in i:
            temp_line = []
            for content in line:
                if content is not None:
                    temp_line.append(content)   
            dates.append(temp_line)
    
    calendar = []
    for line in dates:
        start_date = None
        
        for content in line:
            # search to see if content contains a date
            match = re.search(r'[0-9]{1,2}\/[0-9]{1,2}', content)
            
            # if match, initialize start date
            if match:
                if match.group() and start_date:
                    if start_date > dt.strptime(match.group(), "%m/%d"):
                        continue
                start_date = match.group()
                start_date = dt.strptime(start_date, "%m/%d")
                if line.index(content) == 0 and re.search(r'([0-9]{1,2}\/[0-9]{1,2})$', content):
                    start_date -= timedelta(days=1)
            else:
                # if not match, add a day to the date
                if start_date:
                    start_date += timedelta(days=1)

            # check if content is an assignment and not just date
            if content != '' and not re.search(r'([0-9]{1,2}\/[0-9]{1,2})$', content) and start_date:
                contains_date = re.search(r'([0-9]{1,2}\/[0-9]{1,2})', content)
                # remove date from assignment if content contains date
                if contains_date:
                    content = re.sub(r'[0-9]{1,2}\/[0-9]{1,2}', '', content)

                content = ' '.join(content.split("\n"))
                calendar.append((start_date.strftime("%m/%d"), content.strip()))
    # for i in calendar:
    #     print(i)

    return calendar


def text_to_dates(text) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
         messages=[
            {"role": "user", 
             "content": "If the text includes assignment due dates"
             "Do not include topics or classes"
             "return a ONLY a list containing assignments, quizzes, exams, discussions, and their due dates, formated as:"
             "[('m/d', 'assignments'), ('m/d', 'assignments'), ('m/d', 'assignments'), (etc.)]" + text}
        ],
    )
    return response.choices[0].message.content


# check if table contains due dates for assignments
def contains_due_dates(text) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
         messages=[
            {"role": "user", 
             "content": "Does this text contain assignment due dates? Return 'Yes' or 'No'" + text}
        ],
    )
    return response.choices[0].message.content


def get_class_name(text) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
         messages=[
            {"role": "user", 
             "content": "Return only the name of the class" 
             "If there is an abbrieviation, keep the abbrieviation in all caps"
             "If there is the full title of the class, keep the title in title case"+ text}
        ],
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)
    client = OpenAI(api_key="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")
    # main()
    print('done')
