#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging

from math import ceil
from pathlib import Path
from pprint import pprint
from preLokiTool import udFilter
from requests import post
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",        # 格式：時間 - 等級 - 訊息
    handlers=[
        logging.FileHandler(Path.cwd() / "insertUtter.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

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

    BATCH_SIZE = 5 # 每次送 5 筆
    for valencySTR, kaLIST in kaDICT.items():
        batchesINT = ceil(len(kaLIST) / BATCH_SIZE) # 計算要送幾批
        print(f"意圖：{valencySTR}，總共 {len(kaLIST)} 筆，分成 {batchesINT} 批")

        for i in range(batchesINT):
            start = i * BATCH_SIZE
            end = start + BATCH_SIZE
            batchLIST = kaLIST[start:end]
            utteranceLIST = [udFilter(item_s) for item_s in batchLIST]  # udFilter 為進入 loki 的字串前處理

            payload = {
                "username" : accountDICT["username"],
                "loki_key" : accountDICT["loki_key"],
                "project": "Siraya_ka", #專案名稱
                "intent": valencySTR, #意圖名稱
                "func": "insert_utterance",
                "data": {
                    "utterance": utteranceLIST
                    #[udFilter(item_s) for item_s in kaLIST[:5]] # 小測資
                }
            }

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = post(lokiURL, json=payload)

                    if response.status_code != 200:
                        logging.warning(f"[Attempt {attempt + 1}] HTTP {response.status_code} - {response.text}")

                        if response.status_code == 504:
                            sleep(5 * (attempt + 1))
                            continue

                        if response.status_code == 500: # server error 時，寫 log 並跳過。
                            logging.error(f"Response [500]. utteranceLIST = {utteranceLIST}")
                            break

                        sleep(5)
                        continue

                    data = response.json()
                    pprint(data)
                    break

                except Exception as e:
                    logging.error(f"[Attempt {attempt + 1}] [ERROR] insertUtter ({str(e)})")

                sleep(5)

            else:
                logging.warning(f"Failed after {max_retries} retries. utterance = {utteranceLIST}")


if __name__ == "__main__":
    updateUserDefined()
    insertUtterance()