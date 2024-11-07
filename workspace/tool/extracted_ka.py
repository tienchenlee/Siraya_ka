#!/user/bin/env python
# -*- coding: utf-8 -*-

import fitz
import re
import json

#from pprint import pprint  

def mktxt(pdfFILE, txtFILE):
    with fitz.open(pdfFILE) as doc:
        tot_pages = doc.page_count
        with open(txtFILE, "w", encoding="utf-8") as txt:
            for p in range(tot_pages):
                page = doc.load_page(p)
                text = page.get_text()
                txt.write(text + "\n")    
    
def extracted_ka(txtFILE, jsonFILE):
    with open (txtFILE, "r", encoding="utf-8") as f:
        text = f.read()
        result = re.findall(r"(?<=\.\s\n)\d+:\d+.*(?=\s\n)", text)
        #print(result)
    
    with open(jsonFILE, "w", encoding="utf-8") as js:
        sentenceDICT = {}
        for i in result:
            if re.search(r"\bka\b", i, re.IGNORECASE):
                key = re.findall(r"\d+:\d+", i)
                value = re.findall(r"(?<=\d\s).*", i)
                if key and value:
                    sentenceDICT[key[0]] = value[0]
        #pprint(sentenceDICT)
        json.dump(sentenceDICT, js, ensure_ascii=False)    


if __name__ == "__main__":
    pdfFILES = ("Matthew.pdf", "John.pdf")
    txtFILES = ("Matthew.txt", "John.txt")
    jsonFILES = ("ka_in_Matthew.json", "ka_in_John.json")
    
    for p, t, j in zip(pdfFILES, txtFILES, jsonFILES):
        mktxt(p, t)
        extracted_ka(t, j)