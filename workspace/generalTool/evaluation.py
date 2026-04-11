#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
from itertools import permutations
from pathlib import Path

G_kaPat = re.compile(r"\bka\b")
G_resultDIR = Path(f"{Path.cwd().parent.parent}/data/results")
G_resultDIR.mkdir(exist_ok=True, parents=True)
G_srcDIR = Path(f"{Path.cwd().parent.parent}/data/src")
G_performanceDIR = Path(f"{Path.cwd().parent.parent}/data/performance")
G_performanceDIR.mkdir(exist_ok=True, parents=True)

def createAnswer(phase=None):
    """
    將 kaLIST 與 ansLIST 各自分詞（以空白分割），逐詞比對：
    若 Siraya 詞為 "ka"，則檢查 ansLIST 中相同詞位的對應標記：
    - 若為 "REL" → 加入 RELLIST
    - 若為 "COMP" → 加入 COMPLIST
    - 若為 "AND" 或 "and" → 加入 andLIST

    output:
    [
        [string_index, word_index],
        ...
    ]
    - string_index：對應 kaLIST/ansLIST 中的句子索引。
    - word_index：該句中詞彙（word）的索引位置。

    """
    with open(f"{G_srcDIR}/kaLIST_{phase}.json", "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    with open(f"{G_srcDIR}/ansLIST_{phase}.json", "r", encoding="utf-8") as f:
        ansLIST = json.load(f)

    targetLIST = []
    for i, s in enumerate(kaLIST):
        for m in re.finditer(G_kaPat, s):
            targetLIST.append((i, m.start(), m.end()))

    RELLIST = []
    COMPLIST = []
    andLIST = []
    errorLIST = []

    kaWordLIST = [s.split() for s in kaLIST]
    ansWordLIST = [s.split() for s in ansLIST]

    for string_i, (ka_s, ans_s) in enumerate(zip(kaWordLIST, ansWordLIST)):
        for word_i, kaSTR in enumerate(ka_s):
            if kaSTR == "ka":
                ansSTR = ans_s[word_i]  # 對應 ansLIST 同位置的 word

                if ansSTR == "REL":
                    RELLIST.append([string_i, word_i])
                elif ansSTR == "COMP":
                    COMPLIST.append([string_i, word_i])
                elif ansSTR.lower() == "and":
                    andLIST.append([string_i, word_i])
                else:
                    errorLIST.append([string_i, word_i, ansSTR])

    print(f"COMP: {len(COMPLIST)} 個")
    print(f"and: {len(andLIST)} 個")
    print(f"REL: {len(RELLIST)} 個")
    print(f"total: {len(targetLIST)} 個")

    if len(RELLIST) + len(COMPLIST) + len(andLIST) == len(targetLIST):
        print(f"正解與測資的 ka 數量一致")
        print(f"================================")
    else:
        raise ValueError(f"!!!正解與測資的 ka 數量不一致，請檢查 errorLIST!!!")

    ansPhaseDIR = Path(f"{Path.cwd().parent.parent}/data/answer/{phase}")
    ansPhaseDIR.mkdir(exist_ok=True, parents=True)

    with open(f"{ansPhaseDIR}/REL.json", "w", encoding="utf-8") as f:
        json.dump(RELLIST, f, ensure_ascii=False, indent=4)

    with open(f"{ansPhaseDIR}/COMP.json", "w", encoding="utf-8") as f:
        json.dump(COMPLIST, f, ensure_ascii=False, indent=4)

    with open(f"{ansPhaseDIR}/and.json", "w", encoding="utf-8") as f:
        json.dump(andLIST, f, ensure_ascii=False, indent=4)

    return COMPLIST, andLIST, RELLIST

def makePrediction(phase=None):
    """
    將 predictionLIST 中的 lokiResultDICT 分別寫出與 answer/ 一樣的資料結構。
    在 mapDICT 選擇此次 askLoki 的專案。
    """
    COMPLIST = []
    andLIST = []
    RELLIST = []

    mapDICT = {
        "COMP": COMPLIST,
        "and": andLIST,
        "REL": RELLIST
               }

    kaLIST = ["COMP", "and", "REL"]
    predPhaseDIR = Path(f"{Path.cwd().parent.parent}/data/prediction/{phase}")
    predPhaseDIR.mkdir(exist_ok=True, parents=True)

    for KA in kaLIST:
        with open(f"{G_resultDIR}/{KA}_{phase}.json", "r", encoding="utf-8") as f:
            predictionLIST = json.load(f)

        for lokiResultDICT in predictionLIST:   #處理每個 prediction item
            for keySTR in mapDICT.keys():
                if keySTR in lokiResultDICT.keys():
                    ka_indexLIST = lokiResultDICT["ka_index"]
                    utter_index = lokiResultDICT["utter_index"][0]
                    for ka_index in ka_indexLIST:
                        if [utter_index, ka_index] not in mapDICT[keySTR]:
                            mapDICT[keySTR].append([utter_index, ka_index])

        for keySTR in mapDICT:
            with open(f"{predPhaseDIR}/{keySTR}.json", "w", encoding="utf-8") as f:
                json.dump(mapDICT[keySTR], f, ensure_ascii=False, indent=4)


    with open(f"{predPhaseDIR}/COMP.json", "r", encoding="utf-8") as f:
        COMPPredLIST = json.load(f)
    with open(f"{predPhaseDIR}/and.json", "r", encoding="utf-8") as f:
        andPredLIST = json.load(f)
    with open(f"{predPhaseDIR}/REL.json", "r", encoding="utf-8") as f:
        RELPredLIST = json.load(f)

    return COMPPredLIST, andPredLIST, RELPredLIST

def _getTP(predLIST, ansLIST):
    """"""
    TP = 0
    for item_l in predLIST:
        if item_l in ansLIST:
            TP += 1

    return TP

def extractFN(predLIST, ansLIST):
    """"""
    with open(f"{G_srcDIR}/ansLIST_eval.json", "r", encoding="utf-8") as f:
        evalLIST = json.load(f)

    utterIdxSET = set()
    fnLIST = []

    for item_l in ansLIST:
        if item_l not in predLIST:
            utterIdxSET.add(item_l[0])

    for i in utterIdxSET:
        fnLIST.append(evalLIST[i])

    return fnLIST

def getRecall(predLIST, ansLIST):
    """
    實際為真的樣本中，正確預測的比例。
    recall = (∣Prediction ∩ Answer∣​ / |Answer∣) * 100
    """
    TP = _getTP(predLIST, ansLIST)
    FN = len(ansLIST) - TP

    print(f"TP：{TP}")
    print(f"FN: {FN}")
    print(f"TP+FN：{len(ansLIST)}")
    recall = TP / len(ansLIST)
    print(f"recall: {recall * 100:.2f}%")
    print(f"--------------------------------")

def getPrecision(predLIST, ansLIST):
    """
    陽性樣本中，正確預測的比例。
    """
    TP = _getTP(predLIST, ansLIST)
    FP = len(predLIST) - TP

    print(f"TP：{TP}")
    print(f"FP: {FP}")
    print(f"TP+FP：{len(predLIST)}")
    precision = TP / len(predLIST)
    print(f"precision: {precision * 100:.2f}%")
    print(f"--------------------------------")

def getAccuracy(predLIST, ansLIST, allAnsLIST):
    """
    預測正確的比例。
    """
    TP = 0
    TN = 0

    for item_l in allAnsLIST:
        if item_l in predLIST and item_l in ansLIST:
            TP += 1
        elif item_l not in predLIST and item_l not in ansLIST:
            TN += 1

    accuracy = (TP + TN) / len(allAnsLIST)
    print(f"TP+TN: {TP + TN}")
    print(f"TP+TN+FP+FN: {len(allAnsLIST)}")
    print(f"accuracy: {accuracy * 100:.2f}%")
    print(f"--------------------------------")

def getCoverage(predLIST, ansLIST):
    """
    TP / Total，句型模型對此次語料的覆蓋程度。
    """
    TP = _getTP(predLIST, ansLIST)
    Total = len(ansLIST)

    coverage = TP / Total
    print(f"TP: {TP}")
    print(f"Total: {Total}")
    print(f"coverage: {coverage * 100:.2f}%")
    print(f"================================")

if __name__ == "__main__":
    PHASE = "test" #test, eval

    COMPAnsLIST, andAnsLIST, RELAnsLIST = createAnswer(phase=PHASE)
    COMPPredLIST, andPredLIST, RELPredLIST = makePrediction(phase=PHASE)   # The prediction is made respectively

    functionDICT = {
        "REL":  (RELPredLIST,  RELAnsLIST),
        "COMP": (COMPPredLIST, COMPAnsLIST),
        "and":  (andPredLIST,  andAnsLIST),
    }

    allAnsLIST = COMPAnsLIST + andAnsLIST + RELAnsLIST
    print(f"language models constructed using Loki")
    print(f"=== [{PHASE}] 個別 Project 結果 ===")

    allFnLIST = []

    for keySTR, (predLIST, ansLIST) in functionDICT.items():
        print(f"[{keySTR}]")
        getRecall(predLIST, ansLIST)
        getPrecision(predLIST, ansLIST)
        getAccuracy(predLIST, ansLIST, allAnsLIST)
        getCoverage(predLIST, ansLIST)

        if PHASE == "eval":
            fnLIST = extractFN(predLIST, ansLIST)
            allFnLIST.extend(fnLIST)

            with open(f"{G_performanceDIR}/eval/missedLIST.json", "w", encoding="utf-8") as f:
                json.dump(allFnLIST, f, ensure_ascii=False, indent=4)