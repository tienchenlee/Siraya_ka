#!/user/bin/env python
# -*- coding: utf-8 -*-

import re
import json

from bs4 import BeautifulSoup
from pprint import pprint  

def main(htmlSTR):
    soup = BeautifulSoup(htmlSTR, "lxml")
    sirayaDICT = {}
    sentenceDICT = {}
    
    divLIST = soup.select('div[style="padding: 7px;"]')  
    spansLIST = []
    for d in divLIST:
        spans = d.find_all("span")
        spansLIST.append([spans[0].text.strip(), spans[1].text.strip()])

    spans_index = 0  # 用於跟蹤 spansLIST 的起始位置
    h3_LIST = soup.find_all('h3')        
    for h3 in h3_LIST:
        h3STR = h3.get_text()
        cleaned_h3STR = h3STR.replace("\t", "").replace("\n", " ").strip()
        sentences = re.split(r"([\.?])", cleaned_h3STR)
        if len(sentences) == 1 and sentences[0] == cleaned_h3STR:  # 檢查是否為空列表
            cleaned_sentence = [cleaned_h3STR]  # 使用原始字符串
        else:
            cleaned_sentence = [(sentences[i] + sentences[i + 1]).strip() for i in range(0, len(sentences) - 1, 2)]        
        
        #sentences = re.split(r"([\.?])", cleaned_h3STR)
        #cleaned_sentence = [(sentences[i] + sentences[i + 1]).strip() for i in range(0, len(sentences) - 1, 2)]
        #print(cleaned_sentence)
        
        sentenceLIST = []
        for s in cleaned_sentence:
            sLIST = list(s.split())  # 為每個句子建立 sLIST
            tmpLIST = []
    
            for word in sLIST:
                cleaned_word = re.sub("-", "", word)
                if spans_index < len(spansLIST):
                    span = spansLIST[spans_index]
                    cleaned_span = re.sub("-", "", span[0])
                    match = re.search(r"\w+", cleaned_word, re.IGNORECASE)
                    if match and match.group().lower() == cleaned_span.lower():
                        tmpLIST.append(span[1])
                    spans_index += 1 
    
            tmpSTR = " ".join(tmpLIST)
            sentenceLIST.append({s: tmpSTR}) # 將翻譯結果儲存到當前句子
        print(sentenceLIST) 
    
    #h1_LIST = soup.find_all('h1', class_="secBG")
    #for h1 in h1_LIST:
        #h1STR = h1.get_text()
        #match = re.search(r"\d+:\d+", h1STR)
        #if match:
            #key = match.group()
            #sirayaDICT[key] = sentenceLIST    
    
    ##if key and value:
        ##sirayaDICT[key]= value
    #return sirayaDICT    
    
#def extracted_ka():
       


if __name__ == "__main__":
    html_files = {
        "./Matthew Website.html": "ka_in_Matthew.json",
        "./John Website.html": "ka_in_John.json"
    }
    for htmlFILE, jsonFILE in html_files.items():
        with open(htmlFILE, "r", encoding="utf-8") as web:
            htmlSTR = web.read()
            result = main(htmlSTR)
        
    #with open(jsonFILE, "w", encoding="utf-8") as js:
        #json.dump(sentenceDICT, js, ensure_ascii=False, indent=4)     