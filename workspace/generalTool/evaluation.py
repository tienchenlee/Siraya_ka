#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
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
    kaPATH = Path.cwd().parent.parent / "data" / "kaLIST.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    ansPATH = Path.cwd().parent.parent / "data" / "ansLIST.json"
    with open(ansPATH, "r", encoding="utf-8") as f:
        ansLIST = json.load(f)

    targetLIST = []
    for i, s in enumerate(kaLIST):
        for m in re.finditer(G_kaPat, s):
            targetLIST.append((i, m.start(), m.end()))

    RELLIST = []
    COMPLIST = []
    andLIST = []

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

    print(f"COMP: {len(COMPLIST)} 個")
    print(f"and: {len(andLIST)} 個")
    print(f"REL: {len(RELLIST)} 個")
    print(f"total: {len(targetLIST)} 個")

    if len(RELLIST) + len(COMPLIST) + len(andLIST) == len(targetLIST):
        print(f"正解與測資的 ka 數量一致")
        print(f"================================")
    else:
        raise ValueError(f"!!!正解與測資的 ka 數量不一致，請檢查 ansLIST、kaLIST!!!")

    with open(G_ansDIR / "REL.json", "w", encoding="utf-8") as f:
        json.dump(RELLIST, f, ensure_ascii=False, indent=4)

    with open(G_ansDIR / "COMP.json", "w", encoding="utf-8") as f:
        json.dump(COMPLIST, f, ensure_ascii=False, indent=4)

    with open(G_ansDIR / "and.json", "w", encoding="utf-8") as f:
        json.dump(andLIST, f, ensure_ascii=False, indent=4)

    return COMPLIST, andLIST, RELLIST

#def getCoverage():
    #"""
    #計算模型句型覆蓋率。
    #比對 Prediction 與 Answer 中的 ka_index。
    #"""
    #functionLIST = [
        ##"REL",
        #"COMP",
        ##"and"
    #]

    #for functionSTR in functionLIST:

        #with open(f"{G_ansDIR}/{functionSTR}.json", "r", encoding="utf-8") as f:
            #answerLIST = json.load(f)

        #with open(f"{G_predictionDIR}/{functionSTR}.json", "r", encoding="utf-8") as f:
            #predictionLIST = json.load(f)

        #indexPredictionLIST = []
        #indexPredictionSET = set()
        #for item_d in predictionLIST:
            #ka_indexLIST = item_d["ka_index"]
            #utter_index = item_d["utter_index"][0]
            #for ka_index in ka_indexLIST:
                #item = (utter_index, ka_index)
                #if item not in indexPredictionSET:
                    #indexPredictionLIST.append([utter_index, ka_index])
                    #indexPredictionSET.add(item)

        #print(indexPredictionLIST)

        #match = 0
        #for item_l in indexPredictionLIST:
            #if item_l in answerLIST:
                #match += 1

        #total = len(answerLIST)
        #coverage = (match / total) * 100
        #print(f"{functionSTR} 覆蓋率：{coverage*100:.2f}%")

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
                    mapDICT[keySTR].append([utter_index, ka_index])

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


if __name__ == "__main__":
    COMPAnsLIST, andAnsLIST, RELAnsLIST = createAnswer()
    COMPPredLIST, andPredLIST, RELPredLIST = makePrediction()

    functionDICT = {
        "COMP": (COMPPredLIST, COMPAnsLIST),
        "and":  (andPredLIST,  andAnsLIST),
        "REL":  (RELPredLIST,  RELAnsLIST),
    }

    for keySTR, (predLIST, ansLIST) in functionDICT.items():
        print(f"[{keySTR}]")
        coverage = getCoverage(predLIST, ansLIST)
        findUncoveredAnswer(predLIST, ansLIST, keySTR)