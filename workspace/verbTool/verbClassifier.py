#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
import requests

from pathlib import Path
from requests import post

verbPat = re.compile(r"[\w\.]+(?=\.AV|-AV|\.PV|-PV|\.LV|-LV|-IV)")

dataDIR = Path.cwd().parent.parent / "data"

accountPATH = Path.cwd() / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def _verbExtractor():
    """"""
    dictPATH = dataDIR / "globalDICT.json"
    with open(dictPATH, "r", encoding="utf-8") as f:
        globalDICT = json.load(f)

    verbSET = set()
    for valueLIST in globalDICT.values():
        for valueSTR in valueLIST:
            match = re.search(verbPat, valueSTR)
            if match:
                verbSET.add(match.group())
    print(f"動詞：{verbSET}")
    print(f"動詞數量{len(verbSET)}")

    return verbSET

def _call_LLM(verbSTR):
    """"""
    url = "https://nlu.droidtown.co/Loki_EN/Call/" # 英文版

    payload = {
      "username": accountDICT["username"],
      "func": "call_llm",
      "data": {
        "model": "Gemma3-27B",
        "system": "You are a professional syntactician.", # optional
        "assistant": "", # optional
        "user": f"Identify the verb '{verbSTR}'. Reply V1 if it's intransitive verb. Reply V2 if it's transitive verb. Reply V3 if it's ditransitive verb. Only reply V1 / V2 / V3 without further explanation.", # required
      }
    }

    response = post(url, json=payload)

    if response.status_code != 200:
        return f"伺服器問題：{response.status_code}"

    try:
        resultDICT = response.json()
        valencySTR = resultDICT["result"][0]["message"]["content"]
        return valencySTR
    except requests.exceptions.JSONDecodeError:
        return f"JSON 格式錯誤：{response.text[:200]}"

def verbClassifier():
    """"""
    verbSET = _verbExtractor()
    valencyDICT = {}

    for verbSTR in verbSET:
        print(f"辨別 {verbSTR} 為...")
        valencySTR = _call_LLM(verbSTR)
        print(f"{valencySTR.strip()}")
        print()

        valencyDICT[verbSTR] = valencySTR.strip()

    print(valencyDICT)
    valencyPATH = dataDIR / "valencyDICT.json"
    with open(valencyPATH, "w", encoding="utf-8") as f:
        json.dump(valencyDICT, f, ensure_ascii=False, indent=4)

def main():
    valencyPATH = dataDIR / "valencyDICT.json"
    with open(valencyPATH, "r", encoding="utf-8") as f:
        valencyDICT = json.load(f)

    dictPATH = dataDIR / "globalDICT.json"
    with open(dictPATH, "r", encoding="utf-8") as f:
        globalDICT = json.load(f)

    verbDICT = {}

    for keySTR, valueLIST in globalDICT.items():
        subDICT = {}

        for valueSTR in valueLIST:
            match = re.search(verbPat, valueSTR)
            if match:
                verbStemSTR = match.group()

                if verbStemSTR in valencyDICT.keys():
                    subDICT[valueSTR] = valencyDICT[verbStemSTR]

        if subDICT:
            verbDICT[keySTR] = subDICT

    print(verbDICT)
    verbPATH = dataDIR / "verbDICT.json"
    with open(verbPATH, "w", encoding="utf-8") as f:
        json.dump(verbDICT, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    #verbClassifier()
    main()
