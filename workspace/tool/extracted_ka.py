#!/user/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re

from docx import Document
from pprint import pprint  
from requests import post
from time import sleep

try:
    with open("./account.info", encoding="utf-8") as f:
        accountDICT = json.load(f)
except:
    accountDICT = {"username":"", "apikey":""}

pat1 = re.compile(r"^ka\b", re.IGNORECASE)
pat2 = re.compile(r"\ska\b")
pat3 = re.compile(r"\b[A-Z]?[a-z]+\b")

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
        
def read_txt(folder_path):
    txtFILES = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    sorted_txtFILES = sorted(txtFILES, key=lambda f: order_file(f))
    all_contentLIST = []
    
    for file in sorted_txtFILES:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "r", encoding="utf-8") as f:
            contentLIST = [r.replace("\n", "") for r in f.readlines(0)]
            all_contentLIST.append(contentLIST)
    #看一下內容長怎樣
    #pprint(all_contentLIST)
    return all_contentLIST
        
def get_kaLIST(contentLIST):
    sirayaLIST = []
    for c in contentLIST:
        if "\t" in c and c != "\t":
            tmp = c
            while "\t\t" in tmp:
                tmp = tmp.replace("\t\t", "\t")
            if tmp != "\t":
                sirayaLIST.append(tmp)
    #看一下內容長怎樣
    #pprint(sirayaLIST)    
    
    pairedLIST = []
    for i in range(0, len(sirayaLIST), 2):
        if len(sirayaLIST[i]) == 0:
            pass
        else:
            pairedLIST.append([sirayaLIST[i].replace("\t", " ").replace("  ", " ").strip(), sirayaLIST[i+1].replace("\t", " ").replace("  ", " ").strip()])
    #pprint(pairedLIST)
    
    kaLIST = []
    for p, pair in enumerate(pairedLIST):
        if pat1.match(pair[0]) and p > 0:
            kaLIST.append((pairedLIST[p-1], pair))
        if pat2.search(pair[0]):
            kaLIST.append(pair)
    return kaLIST    
    
def get_engLIST(kaLIST):
    engLIST = []
    for k in kaLIST:
        if isinstance(k, list):          
            matches = pat3.findall(k[1])
            engLIST.append(matches)
        elif isinstance(k, tuple):
            word = " ".join([lst[1] for lst in k])
            matches = pat3.findall(word)
            engLIST.append(matches)
    #print(engLIST)
    for lst in engLIST:
        engSTR = " ".join(lst)
        get_pos(engSTR)
        sleep(0.5)
        #print(engSTR)

def get_pos(inputSTR):
    url = "https://nlu.droidtown.co/Articut_EN/API/"
    payload = {
        "username": accountDICT["username"],
        "api_key": accountDICT["api_key"],
        "input_str": inputSTR
    }    
    response = post(url, json=payload).json()
    print(response["result_pos"])  

if __name__ == "__main__":
    folder_path = r"Gospel of Matthew, 2024.9.03"
    mktxt_files()
    all_contentLIST = read_txt(folder_path)
    for contentLIST in all_contentLIST:
        kaLIST = get_kaLIST(contentLIST)
        get_engLIST(kaLIST)
        
    #with open(jsonFILE, "w", encoding="utf-8") as js:
        #json.dump(sentenceDICT, js, ensure_ascii=False, indent=4)     