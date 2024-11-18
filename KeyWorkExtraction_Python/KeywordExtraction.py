import os
import calendar
import time
import math
import collections
import threading
import re
import string
import json
#from threading import Thread

import numpy as np
import collections
#from logger import logger  #import logging #日志

from flask import Flask, request, send_from_directory,Response
from flask_cors import CORS
# anti api filename attack
from werkzeug.utils import secure_filename

# TF-IDF（Term Frequency-Inverse Document Frequency）
from sklearn.feature_extraction.text import TfidfVectorizer
# filter english common word
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# OpenMP或Intel MKL库 ignore duplicate load
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

#监听地址端口
host = '0.0.0.0'
port = 5600

# 上传文件大小限制
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# 關閉ascii編碼方式-返回中文
app.config['JSON_AS_UTF8'] = False
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

# Allowed upload file types and storage locations
ALLOWED_EXTENSIONS = set(['cv', 'xls', 'xlsx','txt'])
UPLOAD_FOLDER = './files/'

# File upload processing method
@app.route('/detect', methods=['POST', 'GET'])
def do_upload():

    # post上传
    if request.method == 'POST':
        # Get uploaded files
        file = request.files['file']
        # File types allowed to be uploaded
        if file and allowed_file(file.filename):
            # Start counting time
            old_time=time.time()
            # Get the actual file name
            filename = secure_filename(file.filename)
            # Get the path to save the image
            text_path_file = os.path.join(UPLOAD_FOLDER, filename)
            # Save to settings directory
            file.save(text_path_file)
            # recognize text content -------------------------------
            content_of_read_text =  read_text_file(text_path_file)
            if len(content_of_read_text) <= 0:
                return {'error':-1, 'description':'No keywords were extracted from the text content.'}

            # Extract keywords and return structure 處理和提取關鍵詞
            keyword= keyword_extraction(content_of_read_text)

            # calculating timelapse
            take_time = time.time()-old_time

            # delete the source text file after keyword extracted
            # os.remove(text_path_file);

            # 使用 json.dumps() 並設置 ensure_ascii=False
            joson_res_structure = {
                'error': 0,
                'calc_time': take_time,
                'result_of_keyword_extraction': keyword
            }
            json_data = json.dumps(joson_res_structure, ensure_ascii=False)

            # return result
            # 返回自定义的 JSON 响应
            return Response(json_data, content_type='application/json; charset=utf-8')


        return {'error':-1, 'description':'Unsupported file type'}

    # http get
    # Get request to get the uploaded web page
    # render html ui
    return '''
    <!doctype html>
    <title>KeyWord Extraction</title>
    <h1>KeyWord Extraction</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p>
         Select plain text file：<input type=file name=file>
         <input type=submit value=Start to extract>
      </p>
    </form>
    '''

#Download specified file
@app.route('/download/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

@app.route('/clean', methods=['POST', 'GET'])
def clean(): 
     
    thread1 = threading.Thread(target=thread_1)
    thread1.run()

    return {
                'thread_id':thread1.native_id,
                'time': time(),
                 'run_status': True
            }

def thread_1():

    while(1):
        for file_name in os.listdir(os.path.join("files")) :
            text_path = os.path.join(UPLOAD_FOLDER, file_name)
            print(text_path)
            ts_createtime = os.path.getatime(text_path)
            now =  calendar.timegm(time.gmtime())
            now_before_30_minutes =  now - 30 * 60 * 60;
            if ts_createtime < now_before_30_minutes : 
                os.remove(text_path)
                print("deleted :",text_path)
            else:
                print("still remain :%s",text_path)

        time.sleep(180)  # time.sleep(1800) 

# keyword extraction
def keyword_extraction(text_content):

    documents = [ text_content ]

    # 数据预处理
    preprocessed_docs = [preprocess_text(doc) for doc in documents]

    # 初始化TfidfVectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # 计算TF-IDF矩阵
    tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_docs)

    # 获取TF-IDF特征名称
    feature_names = tfidf_vectorizer.get_feature_names_out()

    # 转换为数组形式
    tfidf_array = tfidf_matrix.toarray()
    print("Feature Names：\n", feature_names)
    print("TF-IDF Matrix：\n", tfidf_array)
    # 计算TF-IDF矩阵
    tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_docs)
    # 获取特征名称
    feature_names = tfidf_vectorizer.get_feature_names_out()
    # top_n
    top_n = 3
    # 提取每篇文档的关键词
    keywords = []
    for row in tfidf_matrix:
        row_data = row.toarray().flatten()
        top_indices = row_data.argsort()[-top_n:]
        top_keywords = [feature_names[i] for i in top_indices]
        keywords.append(top_keywords)

    # print the keyword
    for i, kw in enumerate(keywords):
        print(f"Keyword of text {i + 1} ：",", ".join(kw))

    return keywords


# File type checking
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Convert to percentage, keep 3 decimal places
def to_percent(pos, file):
    return [round(pos[0] / file[0], 3), round(file[0] / file[1], 3)]


# read text file
def read_text_file(path_file):
    try:
        with open(path_file, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "file not exist"
    except IOError:
        return "read file error"

# preprocess the text
def preprocess_text(text):
    # 转小写
    text = text.lower()
    # 去除标点符号
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    # 去除停用词
    words = [word for word in text.split() if word not in ENGLISH_STOP_WORDS]
    return " ".join(words)





# StartUp Of Program
if __name__ == '__main__':
    # current_path
    current_path = os.getcwd()
    # print the current path
    print(current_path)
    app.run(host = host, port = port, debug = True )
 