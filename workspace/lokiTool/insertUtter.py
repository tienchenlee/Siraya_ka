#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json

from requests import post
from pathlib import Path
from pprint import pprint
from preLokiTool import udFilter

lokiURL = "https://nlu.droidtown.co/Loki_EN/Call/"

accountPATH = Path.cwd() / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def updateUserDefined():
    """"""
    udPATH = Path.cwd().parent.parent / "data" / "userDefined.json"
    with open(udPATH, "r", encoding="utf-8") as f:
        userDefined = json.load(f)

    payload = {
        "username" : accountDICT["username"],
        "loki_key" : accountDICT["loki_key"],
        "project": "Siraya_ka", #專案名稱
        "func": "update_userdefined",
        "data": {
            "user_defined": userDefined
        }
    }

    response = post(lokiURL, json=payload)
    print(response)
    response = response.json()
    pprint(f"自定義字典：{response}")
    return None

def insertUtterance():
    """
    kaDICT = {
    "V1":["sentence", "sentence"],
    "V2":["sentence", "sentence"],
    "V3":["sentence", "sentence"]
    }
    """
    kaDictPATH = Path.cwd().parent.parent / "data" / "kaDICT.json"
    with open(kaDictPATH, "r", encoding="utf-8") as f:
        kaDICT = json.load(f)

    for valencySTR, kaLIST in kaDICT.items():
        print(f"句型：{(kaLIST[:5])}")
        payload = {
            "username" : accountDICT["username"],
            "loki_key" : accountDICT["loki_key"],
            "project": "Siraya_ka", #專案名稱
            "intent": valencySTR, #意圖名稱
            "func": "insert_utterance",
            "data": {
                "utterance": [udFilter(item_s) for item_s in kaLIST[:5]] # 小測資
            }
        }
        response = post(lokiURL, json=payload).json()
        pprint(response)

if __name__ == "__main__":
    updateUserDefined()
    insertUtterance()