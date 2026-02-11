#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging

from Loki_and.Coordinator.main import askLoki as askLokiAND
from Loki_REL.Relativizer.main import askLoki as askLokiREL
from Loki_COMP.Complementizer.main import askLoki as askLokiCOMP
from pathlib import Path
#from preLokiTool import udFilter
from requests import post
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",        # 格式：時間 - 等級 - 訊息
    handlers=[
        logging.FileHandler(Path.cwd() / "ka_identifier.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

accountPATH = Path.cwd() / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def _getIntentLIST(kaFunction):
    """"""
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

def createTestingLIST():
    """
    找出建模的句子，將建模的句子從 testingLIST 排除。
    使用 kaTestingLIST 作為測試資料。
    """
    projectLIST = ["Complementizer", "Coordinator", "Relativizer"]
    excludeLIST = ["vague.ref", "unsolved.ref", "test.ref"]

    for projectSTR in projectLIST:
        refDIR = Path(f"{Path.cwd()}/{projectSTR}/ref/")
        refLIST = [file for file in refDIR.glob("*.ref") if file.name not in excludeLIST]

        excludeLIST = []
        allExcludeLIST = []

        for refFILE in refLIST:
            refDICT = json.load(open(refFILE, encoding="utf-8"))
            for utteranceSTR in refDICT["utterance"]:
                if utteranceSTR not in excludeLIST:
                    excludeLIST.append(utteranceSTR)

            allExcludeLIST.extend(excludeLIST)

    kaPATH = Path.cwd().parent / "data" / "kaLIST.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    ansPATH = Path.cwd().parent / "data" / "ansLIST.json"
    with open(ansPATH, "r", encoding="utf-8") as f:
        ansLIST = json.load(f)

    excludeIdxSET = set()

    for utteranceSTR in allExcludeLIST:
        for idx, ka_s in enumerate(kaLIST):
            if utteranceSTR in ka_s:
                excludeIdxSET.add(idx)

    kaTestingLIST = []
    ansTestingLIST = []

    for idx, (ka_s, ans_s) in enumerate(zip(kaLIST, ansLIST)):
        if idx not in excludeIdxSET:
            kaTestingLIST.append(ka_s)
            ansTestingLIST.append(ans_s)

    kaTestPATH = Path.cwd().parent / "data" / "kaLIST_test.json"
    with open(kaTestPATH, "w", encoding="utf-8") as f:
        json.dump(kaTestingLIST, f, ensure_ascii=False, indent=4)

    ansTestPATH = Path.cwd().parent / "data" / "ansLIST_test.json"
    with open(ansTestPATH, "r", encoding="utf-8") as f:
        json.dump(ansTestingLIST, f, ensure_ascii=False, indent=4)

    return kaTestingLIST

def main(inputSTR, utterIdx):
    """
    將 ka1, ka2, ka3 的比對順序設為 COMP, and, REL。
    如果句首是 ka，則預設為「然後的 and」。
    """
    resultLIST = []
    #kaIdxSET = set()

    functionDICT = {
        "and": askLokiAND,
        #"COMP": askLokiCOMP,
        #"REL": askLokiREL
    }

    refDICT = {"inputSTR":[inputSTR], "utterance": [], "ka_index":[], "utter_index":[utterIdx], "COMP":[], "and":[], "REL":[]}

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

    for kaSTR, func in functionDICT.items():
        intentLIST = _getIntentLIST(kaSTR)   # 跑單一 intent 結果 in case of timeout when running all intents
        for intent_s in intentLIST:
            attempts = 0
            success = False

            while attempts < 3 and not success:
                lokiResultDICT = func(inputSTR, filterLIST=[intent_s], refDICT=refDICT)
                #sleep(0.8)

                if "msg" in lokiResultDICT.keys():   # Server Error 會回傳 status
                    attempts += 1
                    sleep(5)
                    logging.warning(f"第 {attempts} 次嘗試，{lokiResultDICT['msg']}: {lokiResultDICT}")
                else:
                    success = True

                    if lokiResultDICT["ka_index"] and lokiResultDICT["and"]:
                        resultLIST.append(lokiResultDICT)   # 跑單一 project 的結果
                        logging.info(lokiResultDICT)

            if not success:
                logging.error(f"連續 3 次嘗試失敗，跳過此測試句: {intent_s}")

    return resultLIST

if __name__ == "__main__":
    #kaTestingLIST = createTestingLIST()

    kaPATH = Path.cwd().parent / "data" / "andFP_relTP.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        intersectionLIST = json.load(f)

    predictionLIST = []
    #for utterIdx, inputSTR in enumerate(kaTestingLIST):
    #for utterIdx, inputSTR in enumerate(intersectionLIST):
    inputSTR = "because OBL that PAST- PC. more .AV seek .AV NOM Jew OBL kill -IV .IRR him -OBL because ka not nly spoil -LV he .GEN NOM day OBL sabbath FOC PAST- say .AV also ka God NOM father his ka true .AV"
    resultLIST = main(inputSTR, 0)
    predictionLIST.extend(resultLIST)
    #print(predictionLIST)

    trainingDIR = Path.cwd().parent / "data" / "training"
    trainingDIR.mkdir(exist_ok=True, parents=True)

    with open(trainingDIR / "predictionLIST.json", "w", encoding="utf-8") as f:
        json.dump(predictionLIST, f, ensure_ascii=False, indent=4)


    ##<單筆測試>
    #inputSTR ="So.much.so .AV ka PAST- marvel .AV NOM multitudes while see -LV they .GEN ka speak .AV NOM dumb .AV ka well .AV NOM maimed .AV ka walk .AV NOM lame .AV ka see .AV NOM blind .AV ka PAST- cause.high .AV NOM they cause.great -PV OBL status OBL God OBL Israel"

    ##filterSTR = udFilter(inputSTR)
    #resultLIST = main(inputSTR, 0)  # 預設句子 index = 0
    #print()
    #print(resultLIST)
    ##</單筆測試>

