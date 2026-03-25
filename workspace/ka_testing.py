#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging

from Loki_and.Coordinator.main import askLoki as askLokiAND
from Loki_REL.Relativizer.main import askLoki as askLokiREL
from Loki_COMP.Complementizer.main import askLoki as askLokiCOMP
from pathlib import Path
from requests import post
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",        # 格式：時間 - 等級 - 訊息
    handlers=[
        logging.FileHandler(Path(f"{Path.cwd()}/ka_testing.log"), encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

with open(f"{Path.cwd()}/account.info", "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def _getIntentLIST(kaFunction):
    """
    拿到該 Project 的所有 intent。

    回傳：intentLIST
    """
    intentLIST = []
    url = "https://nlu.droidtown.co/Loki_EN/Call/"

    projectDICT = {
        "and": "Coordinator",
        "COMP": "Complementizer",
        "REL": "Relativizer"
    }

    project = projectDICT[kaFunction]

    payload = {
        "username" : accountDICT["username"],
        "loki_key": accountDICT[project],
        "project": project,
        "func": "get_info",
        "data": {}
    }

    response = post(url, json=payload)

    try:
        resultDICT = response.json()
        intentDICT = resultDICT["result"]["intent"]

        for keySTR in intentDICT.keys():
            intentLIST.append(keySTR)

        return intentLIST

    except:
        print(response.status_code)
        print(response.text)

def main(inputSTR, utterIdx, ka_type):
    """
    在 functionDICT 選擇此次 askLoki 的專案。
    如果句首是 ka，則預設為「然後的 and」。
    """
    resultLIST = []

    FUNCTION_MAP = {
        "COMP": askLokiCOMP,
        "and": askLokiAND,
        "REL": askLokiREL
    }

    refDICT = {
        "inputSTR":[inputSTR],
        "utterance": [],
        "ka_index":[],
        "utter_index":[utterIdx],
        "COMP":[],
        "and":[],
        "REL":[]
    }

    # <句首為 ka 預設為「然後的 and」>
    inputWordLIST = inputSTR.split(" ")
    if inputWordLIST[0] == "ka":
        defaultKaDICT = {
            "inputSTR": [inputSTR],
            "and": [{"then": True}],
            "ka_index": [0],
            "utter_index": [utterIdx],
        }

        resultLIST.append(defaultKaDICT)
    # <句首為 ka 預設為「然後的 and」>

    func = FUNCTION_MAP[ka_type]
    #intentLIST = _getIntentLIST(ka_type)   # 跑單一 intent 結果 in case of timeout when running all intents
    intentLIST = ["Left_Periphery"]
    for intent_s in intentLIST:
        attempts = 0
        success = False

        while attempts < 3 and not success:
            lokiResultDICT = func(inputSTR, filterLIST=[intent_s], refDICT=refDICT)
            sleep(0.8)

            if "msg" in lokiResultDICT.keys():   # Server Error 會回傳 status
                attempts += 1
                sleep(5)
                logging.warning(f"第 {attempts} 次嘗試，{lokiResultDICT['msg']}: {lokiResultDICT}")
            else:
                success = True

                if lokiResultDICT["ka_index"] and lokiResultDICT[ka_type]:
                    print(lokiResultDICT)
                    resultLIST.append(lokiResultDICT)   # 跑單一 project 的結果
                    #logging.info(lokiResultDICT)

                else:
                    print(f"Does not match any utterance in [{intent_s}]")

        if not success:
            logging.error(f"連續 3 次嘗試失敗，跳過此測試句: {intent_s}")

    return resultLIST

if __name__ == "__main__":
    inputSTR = "because ka PAST- work.for.pay -LV we .INCL .GEN NOM death OBL sin our .INCL"   #testing sentence
    utterIdx = -1   #default
    ka_type = "COMP"    #COMP, and, REL

    print(f"Loki 測試句：")
    print(inputSTR)
    print()

    originalSTR = inputSTR.replace(" -", "-").replace("- ", "-").replace(" .", ".").replace(". ", ".").replace(" ,", ",")
    print(f"VS Code 原句：")
    print(originalSTR)
    print()

    main(inputSTR, utterIdx, ka_type)