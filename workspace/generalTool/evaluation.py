#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
from itertools import permutations
from pathlib import Path

G_kaPat = re.compile(r"\bka\b")
G_ansDIR = Path.cwd().parent.parent / "data" / "answer"
G_ansDIR.mkdir(exist_ok=True, parents=True)
G_predictionDIR = Path.cwd().parent.parent / "data" / "prediction"
G_predictionDIR.mkdir(exist_ok=True, parents=True)
G_trainingDIR = Path.cwd().parent.parent / "data" / "training"
G_trainingDIR.mkdir(exist_ok=True, parents=True)

def createAnswer():
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
    kaPATH = Path.cwd().parent.parent / "data" / "kaLIST_test.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    ansPATH = Path.cwd().parent.parent / "data" / "ansLIST_test.json"
    with open(ansPATH, "r", encoding="utf-8") as f:
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

    with open(G_ansDIR / "REL.json", "w", encoding="utf-8") as f:
        json.dump(RELLIST, f, ensure_ascii=False, indent=4)

    with open(G_ansDIR / "COMP.json", "w", encoding="utf-8") as f:
        json.dump(COMPLIST, f, ensure_ascii=False, indent=4)

    with open(G_ansDIR / "and.json", "w", encoding="utf-8") as f:
        json.dump(andLIST, f, ensure_ascii=False, indent=4)

    return COMPLIST, andLIST, RELLIST

def makePrediction():
    """
    將 predictionLIST 中各個 project 的 lokiResultDICT 分別寫出與 answer/ 一樣的資料結構。
    """
    COMPLIST = []
    andLIST = []
    RELLIST = []

    mapDICT = {"COMP": COMPLIST,
               "and": andLIST,
               "REL": RELLIST}

    with open(f"{G_trainingDIR}/predictionLIST.json", "r", encoding="utf-8") as f:
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
        with open(f"{G_predictionDIR}/{keySTR}.json", "w", encoding="utf-8") as f:
            json.dump(mapDICT[keySTR], f, ensure_ascii=False, indent=4)

    return COMPLIST, andLIST, RELLIST

def getCoverage(predLIST, ansLIST):
    """
    正確答案中，有多少被模型預測到。
    coverage = (∣Prediction ∩ Answer∣​ / |Answer∣) * 100
    """
    correct = 0
    for item_l in predLIST:
        if item_l in ansLIST:
            correct += 1

    print(f"正確預測：{correct}")
    print(f"正確答案：{len(ansLIST)}")
    coverage = correct / len(ansLIST)
    print(f"coverage: {coverage * 100:.2f}%")
    print(f"================================")

def findUncoveredAnswer(predLIST, ansLIST, kaFunction):
    """
    正確答案中，沒有被模型預測到的資料。
    """
    missedLIST = []

    for item_l in ansLIST:
        if item_l not in predLIST:
            missedLIST.append(item_l)

    with open(f"{G_trainingDIR}/{kaFunction}.json", "w", encoding="utf-8") as f:
        json.dump(missedLIST, f, ensure_ascii=False, indent=4)

def getFalsePositive(predLIST, ansLIST):
    """
    不是正確答案，卻被模型預測到的資料。
    """
    incorrect = 0
    for item_l in predLIST:
        if item_l not in ansLIST:
            incorrect += 1

    print(f"錯誤預測：{incorrect}")
    print(f"正確答案：{len(ansLIST)}")
    FT = incorrect / len(ansLIST)
    print(f"falsePositive: {FT* 100:.2f}%")
    print(f"================================")

def _oderedPredLIST(order, mapDICT):
    """
    predLIST2 (list of list) 的 item_l 不能與 predLIST1 重複；
    predLIST3 (list of list) 的 item_l 不能與 predLIST1, predLIST2 重複
    """
    seenSET = set()
    newMapDICT = {}

    for key in order:
        newLIST = []
        for item_l in mapDICT[key]:
            t = tuple(item_l)
            if t not in seenSET:
                seenSET.add(t)
                newLIST.append(item_l)
        newMapDICT[key] = newLIST

    return newMapDICT

def tryPermutation(COMPPredLIST, andPredLIST, RELPredLIST,
                   COMPAnsLIST, andAnsLIST, RELAnsLIST):
    """
    記錄不同排列方式的 Coverage, falsePositive
    """
    functionLIST = ["COMP", "and", "REL"]

    predMapDICT = {
        "COMP": COMPPredLIST,
        "and": andPredLIST,
        "REL": RELPredLIST
    }

    ansMapDICT = {
        "COMP": COMPAnsLIST,
        "and": andAnsLIST,
        "REL": RELAnsLIST
    }

    for order in permutations(functionLIST):
        print(f"===== Order: {order} =====")

        newPredDICT = _oderedPredLIST(order, predMapDICT)

        for keySTR in functionLIST:
            print(f"[{keySTR}]")
            getCoverage(newPredDICT[keySTR], ansMapDICT[keySTR])
            getFalsePositive(newPredDICT[keySTR], ansMapDICT[keySTR])
            #findUncoveredAnswer(newPredDICT[keySTR], ansMapDICT[keySTR], keySTR)

if __name__ == "__main__":
    COMPAnsLIST, andAnsLIST, RELAnsLIST = createAnswer()
    COMPPredLIST, andPredLIST, RELPredLIST = makePrediction()   # The prediction is made respectively

    functionDICT = {
        "COMP": (COMPPredLIST, COMPAnsLIST),
        "and":  (andPredLIST,  andAnsLIST),
        "REL":  (RELPredLIST,  RELAnsLIST),
    }

    print(f"===== 個別 Project 結果 =====")
    for keySTR, (predLIST, ansLIST) in functionDICT.items():
        print(f"[{keySTR}]")
        getCoverage(predLIST, ansLIST)
        getFalsePositive(predLIST, ansLIST)
        findUncoveredAnswer(predLIST, ansLIST, keySTR)

    print("===== 排列實驗結果 =====")
    tryPermutation(
        COMPPredLIST, andPredLIST, RELPredLIST,
        COMPAnsLIST, andAnsLIST, RELAnsLIST
    )