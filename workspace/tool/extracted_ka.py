#!/user/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re

from docx import Document
from pprint import pprint  

folder_path = r"Gospel of Matthew, 2024.9.03"
def order_file(file_name):
    match = re.search(r"\d+", file_name)
    return int(match.group())

def docx_to_txt(docx_path, txt_path):
    # 讀取 Word 文件
    document = Document(docx_path)

    # 開啟並寫入文字文件
    with open(txt_path, 'w', encoding='utf-8') as txt:
        for paragraph in document.paragraphs:
            # 去除段落中的空格並寫入文本文件
            #clean_paragraph = re.sub(" ", "", paragraph.text)
            txt.write(paragraph.text + '\n')

def mktxt_files():
    docFILES = [f for f in os.listdir(folder_path) if f.endswith(".docx")]
    sorted_docFILES = sorted(docFILES, key=lambda f: order_file(f))
    
    for file in sorted_docFILES:
        file_path = os.path.join(folder_path, file)
        output_txt_path = os.path.join(folder_path, os.path.splitext(file)[0] + ".txt")
        docx_to_txt(file_path, output_txt_path)
        
def extracted_ka():
    txtFILES = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    sorted_txtFILES = sorted(txtFILES, key=lambda f: order_file(f))
    
    #kaDICT = {} 
    for file in sorted_txtFILES:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "r", encoding="utf-8") as txt:
            content = txt.read()
            #看一下內容長怎樣
            #print(content)
            
            del_chinese = re.sub(r"[\u4e00-\u9fff]+", "", content)
            print(del_chinese)
            #sentences = re.findall(r"[a-zA-Z\.,:;-?].+\t[a-zA-Z\.,:;-?]+-?[a-zA-Z\.,:;?]+", content)
            #chapters = re.findall(r"(?<=[.?:;]\n)\d+:\d+", content)
            #print(sentences)
            
            #for ch in sorted(set(chapters), key=lambda x: tuple(map(int, x.split(":")))):            
                #print(f"Gloss sentences for '{ch}':")

            
    
    

if __name__ == "__main__":
    mktxt_files()
    extracted_ka()
    #html_files = {
        #"./Matthew Website.html": "ka_in_Matthew.json",
        #"./John Website.html": "ka_in_John.json"
    #}
    #for htmlFILE, jsonFILE in html_files.items():
        #with open(htmlFILE, "r", encoding="utf-8") as web:
            #htmlSTR = web.read()
            #result = main(htmlSTR)
        
    #with open(jsonFILE, "w", encoding="utf-8") as js:
        #json.dump(sentenceDICT, js, ensure_ascii=False, indent=4)     