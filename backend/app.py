import ast
import collections
import os
import pandas as pd
import pdfplumber
import re
from datetime import datetime as dt
from datetime import timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './syllabus'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File upload API route
@app.route('/files', methods=['POST'])
def upload_files():
    print("files received")
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            return jsonify({"error": "One or more files have no name"}), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        uploaded_files.append(file.filename)

    return jsonify({"message": "Files uploaded successfully", "files": uploaded_files}), 200

# Text upload API route
@app.route('/text', methods=["POST"])
def upload_text():
    data = request.json
    title = data.get('title', '')
    text = data.get('text', '')

    # directory = "./syllabus"
    # file_path = os.path.join(directory, f'{file_path} Syllabus.txt')
    with open(os.path.join("./syllabus", f'{title} Syllabus.txt'), "w") as f:
        f.write(text)

    return jsonify({"message": "Text received", "title": title, "text": text}), 200

# API route for sending file information to frontend
@app.route('/return-files', methods=["GET"])
def return_files():
    file_path = './syllabus'
    files_list = []

    # add all files in syllabus folder to file_list
    for file_name in os.listdir(file_path):
        files_list.append({
            "name": file_name,
            "type": "pdf" if file_name.endswith("pdf") else "txt"
        })

    return jsonify(files_list)

# API route for clearing syllabus folder
@app.route('/clear-folder', methods=["POST"])
def clear_folder():
    folder = './syllabus'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error clearing folder: {e}")
    
    return jsonify({"message": "Folder Cleared"}), 200

# API route for generating excel file
@app.route('/download', methods=["GET"])
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
                    name = tail.split("Syllabus")[0].strip()
                    
                    response = text_to_dates(txt)
                    data = ast.literal_eval(response)
                        
                for pair in data:
                    date, assignment = pair[0], pair[1]
                    calendar[date][name] = assignment
    
    # sort calendar by date
    sorted_cal = collections.OrderedDict(sorted(calendar.items(), key=lambda x: dt.strptime(x[0], "%m/%d")))
    calendar_to_excel(sorted_cal)
    
    # send file to user
    return send_file(os.path.join('./output', 'output.xlsx'), as_attachment=True)

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


# get name of class
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
    client = OpenAI(api_key="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")
    app.run(debug=True)
    # main()
    print('done')
