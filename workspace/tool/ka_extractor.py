#!/user/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re

from docx import Document
from pprint import pprint  
from requests import post
from time import sleep
from typing import Union

try:
    with open("./account.info", encoding="utf-8") as f:
        accountDICT = json.load(f)
except:
    accountDICT = {"username":"", "apikey":""}

url = "https://nlu.droidtown.co/Articut_EN/API/"
ChiPAT = re.compile(r"[\u4e00-\u9fff]")
KaPAT1 = re.compile(r"^ka\b", re.IGNORECASE)    #字首ka
KaPAT2 = re.compile(r"\ska\b")                  #句中ka
EngPAT1 = re.compile(r"(?:[A-Z]{2,}-).*|.*(?:[A-Z]{2,})")   #e.g. PAST-throughout-three.AV
EngPAT2 = re.compile(r"[a-z]+(?:-[A-Za-z]+|\.[a-z]+)+")     #compuond, e.g. have-also-I, say.as.such
EngPAT3 = re.compile(r"[A-Z]?[a-z]+|\bI\b")                 #小寫字、人名、I
PosPAT = re.compile(r"<[^/>]+>")

def order_file(file_name: str) -> int:
    """
    從檔案名稱中提取並返回數字部分，以便進行排序。
    
    參數:
        file_name (str): 包含數字的文件名稱字串。

    返回:
        int: 檔案名稱中的數字部分，轉換為整數。
    """
    match = re.search(r"\d+", file_name)
    return int(match.group())

def docx_to_txt(docx_path: str, txt_path: str):
    """
    讀取 docx 檔案內容，並寫成 txt 檔案。
    
    參數：
        docx_path (str): 要讀取的 docx 檔案的路徑。
        txt_path (str): 輸出的 txt 檔案的路徑。
    """
    document = Document(docx_path)

    with open(txt_path, 'w', encoding='utf-8') as txt:
        for paragraph in document.paragraphs:
            txt.write(paragraph.text + '\n')

def mktxt_files(folder_path: str):
    """
    將資料夾內所有 docx 檔案依序轉換為對應的 txt 檔案。
    調用 docx_to_txt 函數輸出同名的 txt 檔案，與 docx 保存於同一目錄下。
    
    參數:
        folder_path (str): 包含 docx 檔案的資料夾路徑。
    """
    docFILES = [f for f in os.listdir(folder_path) if f.endswith(".docx")]
    sorted_docFILES = sorted(docFILES, key=lambda f: order_file(f))
    
    for file in sorted_docFILES:
        file_path = os.path.join(folder_path, file)
        output_txt_path = os.path.join(folder_path, os.path.splitext(file)[0] + ".txt")
        docx_to_txt(file_path, output_txt_path)
        
def read_txt(folder_path: str) -> list:
    """
    讀取資料夾中的所有 txt 檔案內容，並將其整理為列表返回。
    
    參數:
        folder_path (str): 包含 txt 檔案的資料夾路徑。

    回傳:
        list: 一個嵌套列表，其中每個內部列表對應一個 txt 檔案的所有行內容。
    """
    txtFILES = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    sorted_txtFILES = sorted(txtFILES, key=lambda f: order_file(f))
    all_contentLIST = []
    
    for file in sorted_txtFILES:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "r", encoding="utf-8") as f:
            contentLIST = [r.replace("\n", "").strip() for r in f.readlines()]  #contentLIST是一個txt的內容
            all_contentLIST.append(contentLIST)
    #all_contentLIST包含每個txt內容
    #pprint(all_contentLIST)
    return all_contentLIST
        
def get_kaLIST(contentLIST: list) -> list:
    """
    從輸入的內容列表中篩選出包含 "ka" 的句子，如果 ka 位於句首會多拿前一句。
    
    參數:
        contentLIST (list): 包含多行文字的列表，每行可能是西拉雅語句子、gloss 句子。
        
    回傳:
        list: 篩選出包含 "ka" 的句子對列表。
            - 返回列表包含以下兩種格式:
                - 若直接匹配: [西拉雅, gloss]
                - 若額外加入前一句: ([西拉雅, gloss], [西拉雅, gloss])
    """
    
    #排除「第幾章」之前的文字、1:1 那行
    tmpLIST = [c for c in contentLIST if isinstance(c, str) and not re.search(r"\d+:", c) and c != ""]
    for i, c in enumerate(tmpLIST):
        if "章" in c:
            tmpLIST = tmpLIST[i+1:]
            break
    #pprint(tmpLIST)
    
    #將內容拆分為 Siraya + gloss 句子、中文句子及英文句子，並將其組織成對應的 `alignLIST`
    sirayaLIST = []
    alignLIST = []
    i = 0
    while i < len(tmpLIST):
        while i < len(tmpLIST) and not re.search(ChiPAT, tmpLIST[i]):
            sirayaLIST.append(tmpLIST[i].strip())
            i += 1
        if i < len(tmpLIST) and re.search(ChiPAT, tmpLIST[i]):
            c_STR = tmpLIST[i].strip()
            i += 1
        else:
            c_STR = ""
    
        if i < len(tmpLIST):
            e_STR = tmpLIST[i].strip()
            i += 1
        else:
            e_STR = ""
    
        alignLIST.append({
            "s": sirayaLIST,
            "c": c_STR,
            "e": e_STR
        })
        sirayaLIST = []
    
    #處理格式不一致問題，中英句子位置顛倒、英文有一句以上
    for i, a in enumerate(alignLIST):
        if "\t" in a["e"]:
            if i + 1 < len(alignLIST):
                alignLIST[i+1]["s"].insert(0, a["e"])
            a["e"] = a["s"].pop()
        for s in a["s"]:
            if "\t" not in s and len(re.findall(r'\w+', s)) > 1:
                if i > 0:
                    alignLIST[i-1]["e"] += " " + s
                a["s"].remove(s)
    #pprint(alignLIST)
    
    removeLIST = []
    for a in alignLIST:
        sirayaLIST = a["s"]
        
        # 將sirayaLIST進行配對處理
        pairedLIST = []
        for i in range(0, len(sirayaLIST) - 1, 2):  # 兩個一組
            if len(sirayaLIST[i]) == 0 or len(sirayaLIST[i+1]) == 0:
                continue  # 如果當前配對項目為空，跳過
            # 清理多餘的空格和 tab
            pairedLIST.append([
                sirayaLIST[i].replace("\t", " ").replace("  ", " ").replace("  ", " ").strip(), 
                sirayaLIST[i+1].replace("\t", " ").replace("  ", " ").replace("  ", " ").strip()
            ])
            
        a["s"] = pairedLIST
        
        kaLIST = []
        for p, pair in enumerate(pairedLIST):
            if KaPAT1.match(pair[0]) and p > 0:
                kaLIST.append((pairedLIST[p-1], pair))
            if KaPAT2.search(pair[0]):
                kaLIST.append(pair)
        a["s"] = kaLIST
        if not kaLIST:
            removeLIST.append(a)
        
    # pair 完且有 ka 的 sirayaLIST 放回 alignLIST
    for r in removeLIST:
        alignLIST.remove(r)
        
    sceLIST = []    
    for a in alignLIST:
        for i, s_item in enumerate(a["s"]):
            sceLIST.append({
                "c": a["c"],
                "e": a["e"],
                "s": s_item
            })
    #pprint(sceLIST)
        
    #pprint(alignLIST)
    return sceLIST   

def articutEN(inputSTR: str) -> list:
    """
    使用 Articut 英文版 StandardAPI 對輸入的文字進行詞性標記 (POS)。
    
    參數:
        inputSTR (str): 需要進行詞性標記的英文文字。
    
    回傳:
        list: 詞性標記後的結果，返回 result_pos 內容。
    """
    payload = {
        "username": accountDICT["username"],
        "api_key": accountDICT["api_key"],
        "input_str": inputSTR
    }    
    response = post(url, json=payload).json()
    print(f"詞性標記中：{response['result_pos']}")
    return response["result_pos"]

def align2DICT(sceDICT: dict) -> dict:
    """
    處理兩種不同格式的資料：一個是字串列表，一個是包含兩個字串列表的元組。
    並且產生詞性標註（POS）結果。

    參數:
    sceDICT["s"]: (Union[list[str], tuple[list[str], list[str]]]): 
    可以是字符串列表或包含兩個字符串列表的元組。
    sceDICT["c"]: str
    sceDICT["e"]: str

    返回:
    dict: 處理後的結果字典，格式為：
    {
        "s": "Siraya",    # 西拉雅
        "g": "gloss",     # 詞彙對應
        "p": "pos",       # 詞性標記
        "c": "chinese",   # 中文句子（來自 sceDICT 的 "c"）
        "e": "english"    # 英文句子（來自 sceDICT 的 "e"）
    }
    
    """
    skipLIST = ["NOM", "DET", "FOC", "OBL", "LOC", "GEN", "PART", "Q", "REL", "PAST", "NEG"]
    resultDICT = {"s": None, "g": None, "p": [], "c": sceDICT["c"], "e": sceDICT["e"]}
    if isinstance(sceDICT["s"], list):
        resultDICT["s"] = sceDICT["s"][0]
        resultDICT["g"] = sceDICT["s"][1]
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
                        tmpSTR = re.sub(r"\b" + engSTR + r"\b", pos, tmpSTR)
                    posLIST.append(tmpSTR)                
                sleep(0.8)            
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
                        tmpSTR = re.sub(r"\b" + engSTR + r"\b", pos, tmpSTR)
                    posLIST.append(tmpSTR)
                sleep(0.8)
            else:
                engSTR = EngPAT3.findall(glossLIST[i])[0]
                print(engSTR)
                posLIST.append(PosPAT.findall(articutEN(engSTR)[0])[0])
                sleep(0.8)
        resultDICT["p"] = " ".join(posLIST)
    else:   #是 tuple
        resultDICT["s"] = sceDICT["s"][0][0] + " " + sceDICT["s"][1][0]   #兩句相接
        resultDICT["g"] = sceDICT["s"][0][1] + " " + sceDICT["s"][1][1]
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
                        tmpSTR = re.sub(r"\b" + engSTR + r"\b", pos, tmpSTR)
                    posLIST.append(tmpSTR)                
                sleep(0.8)            
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
                        tmpSTR = re.sub(r"\b" + engSTR + r"\b", pos, tmpSTR)
                    posLIST.append(tmpSTR)
                sleep(0.8)
            else:
                engSTR = EngPAT3.findall(glossLIST[i])[0]
                print(engSTR)
                posLIST.append(PosPAT.findall(articutEN(engSTR)[0])[0])
                sleep(0.8)
        resultDICT["p"] = " ".join(posLIST)        

    return resultDICT

if __name__ == "__main__":
    files = {
        "./All chapters, Gospel of Matthew, 2024.12.02": "ka_in_Matthew",
        "./All chapters, Gospel of John, 2024.12.02": "ka_in_John"
    }
    
    for folder_path, jsonFILE_base in files.items():
        if not os.path.exists(jsonFILE_base):
            os.makedirs(jsonFILE_base)
            
        mktxt_files(folder_path)
        all_contentLIST = read_txt(folder_path)
        
        file_cnt = 1    #指定檔名編號
        for contentLIST in all_contentLIST:
            sceLIST = get_kaLIST(contentLIST)
            pprint(sceLIST)
            
            resultLIST = []
            for sceDICT in sceLIST:
                tmpDICT = align2DICT(sceDICT)
                pprint(tmpDICT)
                resultLIST.append(tmpDICT)
            
            jsonFILE = f"{jsonFILE_base}/{jsonFILE_base}_{file_cnt}.json"
            with open(jsonFILE, "w", encoding="utf-8") as f:
                json.dump(resultLIST, f, ensure_ascii=False, indent=4)
            
            file_cnt += 1
