#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
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
        logging.FileHandler(Path(f"{Path.cwd()}/ka_identifier.log"), encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

with open(f"{Path.cwd()}/account.info", "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

G_srcDIR = Path(f"{Path.cwd().parent}/data/src")
G_srcDIR.mkdir(exist_ok=True, parents=True)
G_resultDIR = Path(f"{Path.cwd().parent}/data/results")
G_resultDIR.mkdir(exist_ok=True, parents=True)

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

def createTestingLIST():
    """
    找出建模的句子，將建模的句子從 testingLIST 排除。
    使用 kaTestingLIST 作為測試資料。
    """
    projectLIST = ["Complementizer", "Coordinator", "Relativizer"]
    excludeRefLIST = ["vague.ref", "unsolved.ref", "test.ref"]

    allUtterSET = set()

    for projectSTR in projectLIST:
        refDIR = Path(f"{Path.cwd()}/generalTool/{projectSTR}/ref/")
        refLIST = [file for file in refDIR.glob("*.ref") if file.name not in excludeRefLIST]

        for refFILE in refLIST:
            refDICT = json.load(open(refFILE, encoding="utf-8"))
            allUtterSET.update(refDICT["utterance"])

    allUtterLIST = list(allUtterSET)

    with open(f"{G_srcDIR}/kaLIST.json", "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    with open(f"{G_srcDIR}/ansLIST.json", "r", encoding="utf-8") as f:
        ansLIST = json.load(f)

    excludeIdxSET = set()

    for utteranceSTR in allUtterLIST:
        for idx, ka_s in enumerate(kaLIST):
            if re.search(rf"\b{re.escape(utteranceSTR)}\b", ka_s):
                excludeIdxSET.add(idx)

    kaTestingLIST = []
    ansTestingLIST = []
    kaUtterLIST = []
    ansUtterLIST = []

    for idx, (ka_s, ans_s) in enumerate(zip(kaLIST, ansLIST)):
        if idx not in excludeIdxSET:
            kaTestingLIST.append(ka_s)
            ansTestingLIST.append(ans_s)
        elif idx in excludeIdxSET:
            kaUtterLIST.append(ka_s)
            ansUtterLIST.append(ans_s)

    with open(f"{G_srcDIR}/kaLIST_test.json", "w", encoding="utf-8") as f:
        json.dump(kaTestingLIST, f, ensure_ascii=False, indent=4)

    with open(f"{G_srcDIR}/ansLIST_test.json", "w", encoding="utf-8") as f:
        json.dump(ansTestingLIST, f, ensure_ascii=False, indent=4)

    with open(f"{G_srcDIR}/kaLIST_utter.json", "w", encoding="utf-8") as f:
        json.dump(kaUtterLIST, f, ensure_ascii=False, indent=4)

    with open(f"{G_srcDIR}/ansLIST_utter.json", "w", encoding="utf-8") as f:
        json.dump(ansUtterLIST, f, ensure_ascii=False, indent=4)

    return kaTestingLIST

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
    intentLIST = _getIntentLIST(ka_type)   # 跑單一 intent 結果 in case of timeout when running all intents
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

                if lokiResultDICT["ka_index"] and lokiResultDICT[ka_type]:
                    resultLIST.append(lokiResultDICT)   # 跑單一 project 的結果
                    logging.info(lokiResultDICT)

        if not success:
            logging.error(f"連續 3 次嘗試失敗，跳過此測試句: {intent_s}")

    return resultLIST

if __name__ == "__main__":
    MODE = "test" #test, eval
    COVERAGE = True #True, False
    KA = "COMP" #COMP, and, REL

    if MODE == "test":
        if COVERAGE:
            with open(f"{G_srcDIR}/kaLIST.json", "r", encoding="utf-8") as f:
                inputLIST = json.load(f)
        else:
            inputLIST = createTestingLIST()

    elif MODE == "eval":
        with open(f"{G_srcDIR}/kaLIST_eval.json", "r", encoding="utf-8") as f:
            inputLIST = json.load(f)

    predictionLIST = []
    logging.info(f"PHASE:{MODE}, COVERAGE:{COVERAGE}, KA:{KA}, 測資數量:{len(inputLIST)}")

    for utterIdx, inputSTR in enumerate(inputLIST):
        resultLIST = main(inputSTR, utterIdx, ka_type=KA)
        predictionLIST.extend(resultLIST)

    # 紀錄結果
    SUFFIX = "_coverage" if COVERAGE else ""
    with open(f"{G_resultDIR}/{KA}_{MODE}{SUFFIX}.json", "w", encoding="utf-8") as f:
        json.dump(predictionLIST, f, ensure_ascii=False, indent=4)

    ##<單筆測試>
    #inputSTR ="therefore anything ka speak -LV .IRR they .GEN cause.obey .AV you .PL -OBL obey -PV .IRR you .GEN FOC do -PV .IRR -also NOM it yet PART work their not obey -PV .IRR"

    #resultLIST = main(inputSTR, 0, ka_type="COMP")  # 預設句子 index = 0
    #print()
    #print(resultLIST)
    ##</單筆測試>

