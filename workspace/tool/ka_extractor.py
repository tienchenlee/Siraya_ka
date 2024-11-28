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

url = "https://nlu.droidtown.co/Articut_EN/API/"
ChiPAT = re.compile(r"[\u4e00-\u9fff]")
KaPAT1 = re.compile(r"^ka\b", re.IGNORECASE)
KaPAT2 = re.compile(r"\ska\b")
EngPAT1 = re.compile(r"(?:[A-Z]{2,}-).*|.*(?:[A-Z]{2,})")   #e.g. PAST-throughout-three.AV
EngPAT2 = re.compile(r"[a-z]+(?:-[A-Za-z]+|\.[a-z]+)+")        #compuond, e.g. have-also-I, say.as.such
EngPAT3 = re.compile(r"[A-Z]?[a-z]+|\bI\b")                 #小寫字、人名、I
PosPAT = re.compile(r"(?<=</)[^>]+(?=>)")

def order_file(file_name):
    match = re.search(r"\d+", file_name)
    return int(match.group())

def docx_to_txt(docx_path, txt_path):
    # 讀取 Word 文件
    document = Document(docx_path)

    with open(txt_path, 'w', encoding='utf-8') as txt:
        for paragraph in document.paragraphs:
            txt.write(paragraph.text + '\n')

def mktxt_files(folder_path):
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
            contentLIST = [r.replace("\n", "").strip() for r in f.readlines()]
            all_contentLIST.append(contentLIST)
    #看一下內容長怎樣
    #pprint(all_contentLIST)
    return all_contentLIST
        
def get_kaLIST(contentLIST):
    sirayaLIST = []
    for c in contentLIST:
        if "\t" in c and c != "\t":     #拿有tab那行
            tmp = c
            tmp = tmp.replace(" ", "").replace("\t.", ".")
            while "\t\t" in tmp:
                tmp = tmp.replace("\t\t", "\t")
            if tmp != "\t":
                sirayaLIST.append(tmp)
        elif " " not in c and c != "" and not ChiPAT.search(c):  #該行只有一個字，且不是中文
            sirayaLIST.append(c)
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
        if KaPAT1.match(pair[0]) and p > 0:
            kaLIST.append((pairedLIST[p-1], pair))
        if KaPAT2.search(pair[0]):
            kaLIST.append(pair)
    return kaLIST    

def articutEN(inputSTR):
    payload = {
        "username": accountDICT["username"],
        "api_key": accountDICT["api_key"],
        "input_str": inputSTR
    }    
    response = post(url, json=payload).json()
    print(f"詞性標記中：{response['result_pos']}")
    return response["result_pos"]

def align2DICT(inputLIST):
    """
    """
    skipLIST = ["NOM", "DET", "FOC", "OBL", "LOC", "GEN", "PART", "Q", "REL", "PAST", "NEG"]
    resultDICT = {"s": None, "g": None, "p": []}
    if isinstance(inputLIST, list):
        resultDICT["s"] = inputLIST[0]
        resultDICT["g"] = inputLIST[1]
        sirayaLIST = resultDICT["s"].split(" ")
        glossLIST = resultDICT["g"].split(" ")
        posLIST = []
        for i in range(0, len(sirayaLIST)):
            if sirayaLIST[i] == "ka" or sirayaLIST[i] == "Ka":       #ka
                posLIST.append("ka")
            elif glossLIST[i] in skipLIST:  #functional word
                posLIST.append(glossLIST[i])
            elif EngPAT1.search(glossLIST[i]):      #e.g. PAST-throughout-three.AV
                match = EngPAT1.search(glossLIST[i])
                if match:
                    before_pos = glossLIST[i]
                    print("before_pos:", before_pos)
                    engLIST = EngPAT3.findall(before_pos)
                    print("engLIST:", engLIST)
                    tmpSTR = glossLIST[i]
                    for engSTR in engLIST:
                        articut = articutEN(engSTR)
                        pos = PosPAT.findall(" ".join(articut))[0] 
                        tmpSTR = tmpSTR.replace(engSTR, pos)
                    posLIST.append(tmpSTR)                
                sleep(0.5)            
            elif EngPAT2.search(glossLIST[i]):      #e.g. have-also-I, say.as.such
                match = EngPAT2.search(glossLIST[i])
                if match:
                    before_pos = glossLIST[i]
                    print("before_pos:", before_pos)
                    engLIST = EngPAT3.findall(before_pos)
                    print("engLIST:", engLIST)
                    tmpSTR = glossLIST[i]
                    for engSTR in engLIST:
                        articut = articutEN(engSTR)
                        pos = PosPAT.findall(" ".join(articut))[0] 
                        tmpSTR = tmpSTR.replace(engSTR, pos)
                    posLIST.append(tmpSTR)
                sleep(0.5)
            else:
                engSTR = EngPAT3.findall(glossLIST[i])[0]
                print(engSTR)
                posLIST.append(PosPAT.findall(articutEN(engSTR)[0])[0])
                sleep(0.5)
        resultDICT["p"] = " ".join(posLIST)
    else:   #是 tuple
        resultDICT["s"] = inputLIST[0][0] + " " + inputLIST[1][0]   #兩句相接
        resultDICT["g"] = inputLIST[0][1] + " " + inputLIST[1][1]
        sirayaLIST = resultDICT["s"].split(" ")
        glossLIST = resultDICT["g"].split(" ")
        posLIST = []
        for i in range(0, len(sirayaLIST)):
            if sirayaLIST[i] == "ka" or sirayaLIST[i] == "Ka":
                posLIST.append("ka")
            elif glossLIST[i] in skipLIST:  
                posLIST.append(glossLIST[i])
            elif EngPAT1.search(glossLIST[i]):      #e.g. PAST-throughout-three.AV
                match = EngPAT1.search(glossLIST[i])
                if match:
                    before_pos = glossLIST[i]
                    print("before_pos:", before_pos)
                    engLIST = EngPAT3.findall(before_pos)
                    print("engLIST:", engLIST)
                    tmpSTR = glossLIST[i]
                    for engSTR in engLIST:
                        articut = articutEN(engSTR)
                        pos = PosPAT.findall(" ".join(articut))[0] 
                        tmpSTR = tmpSTR.replace(engSTR, pos)
                    posLIST.append(tmpSTR)                
                sleep(0.5)            
            elif EngPAT2.search(glossLIST[i]):      #e.g. have-also-I, say.as.such
                match = EngPAT2.search(glossLIST[i])
                if match:
                    before_pos = glossLIST[i]
                    print("before_pos:", before_pos)
                    engLIST = EngPAT3.findall(before_pos)
                    print("engLIST:", engLIST)
                    tmpSTR = glossLIST[i]
                    for engSTR in engLIST:
                        articut = articutEN(engSTR)
                        pos = PosPAT.findall(" ".join(articut))[0] 
                        tmpSTR = tmpSTR.replace(engSTR, pos)
                    posLIST.append(tmpSTR)
                sleep(0.5)
            else:
                engSTR = EngPAT3.findall(glossLIST[i])[0]
                print(engSTR)
                posLIST.append(PosPAT.findall(articutEN(engSTR)[0])[0])
                sleep(0.5)
        resultDICT["p"] = " ".join(posLIST)        

    return resultDICT        

if __name__ == "__main__":
    resultLIST = []
    files = {
        "./Gospel of Matthew, 2024.9.03": "ka_in_Matthew.json",
        "./Gospel of John, 2024.9.03": "ka_in_John.json"
        }
    
    for folder_path, jsonFILE in files.items():
        mktxt_files(folder_path)
        all_contentLIST = read_txt(folder_path)
        
        for contentLIST in all_contentLIST:
            kaLIST = get_kaLIST(contentLIST)
            pprint(kaLIST)
            
            for r_l in kaLIST:
                tmpDICT = align2DICT(r_l)
                pprint(tmpDICT)
                resultLIST.append(tmpDICT)
    
        with open(jsonFILE, "w", encoding="utf-8") as f:
            json.dump(resultLIST, f, ensure_ascii=False, indent=4)     