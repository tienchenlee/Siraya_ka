#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
from pathlib import Path

G_kaPat = re.compile(r"\bka\b")
G_ansDIR = Path.cwd() / "answer"
G_ansDIR.mkdir(exist_ok=True, parents=True)
G_predictionDIR = Path.cwd() / "prediction"
G_predictionDIR.mkdir(exist_ok=True, parents=True)
G_dataDIR = Path.cwd().parent / "data"
G_resultDIR = Path.cwd() / "results"

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
    kaPATH = G_dataDIR / "kaLIST_eval.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    ansPATH = G_dataDIR / "ansLIST_eval.json"
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
    將 results/ 中的 LLM 預測 分別寫出與 answer/ 一樣的資料結構。
    """
    COMPLIST = []
    andLIST = []
    RELLIST = []

    mapDICT = {
               "COMP": COMPLIST,
               "and": andLIST,
               "REL": RELLIST
               }

    with open(f"{G_resultDIR}/phase_1.json", "r", encoding="utf-8") as f:
        resultLIST = json.load(f)

    with open(f"{G_dataDIR}/kaLIST_eval.json", "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    for llmResultDICT in resultLIST:   #處理每個 prediction item
        if llmResultDICT["status"] == "Succeeded":
            for keySTR in mapDICT.keys():
                if keySTR in llmResultDICT.keys() and llmResultDICT[keySTR]:
                    ka_indexLIST = llmResultDICT[keySTR]
                    inputSTR = llmResultDICT["inputSTR"]

                    utterDICT = {s: i for i, s in enumerate(kaLIST)}
                    utter_index = utterDICT.get(inputSTR)

                    for ka_index in ka_indexLIST:
                        if [utter_index, ka_index] not in mapDICT[keySTR]:
                            mapDICT[keySTR].append([utter_index, ka_index])

    for keySTR in mapDICT:
        with open(f"{G_predictionDIR}/{keySTR}.json", "w", encoding="utf-8") as f:
            json.dump(mapDICT[keySTR], f, ensure_ascii=False, indent=4)

    with open(f"{G_predictionDIR}/COMP.json", "r", encoding="utf-8") as f:
        COMPPredLIST = json.load(f)
    with open(f"{G_predictionDIR}/and.json", "r", encoding="utf-8") as f:
        andPredLIST = json.load(f)
    with open(f"{G_predictionDIR}/REL.json", "r", encoding="utf-8") as f:
        RELPredLIST = json.load(f)

    return COMPPredLIST, andPredLIST, RELPredLIST

def getRecall(predLIST, ansLIST):
    """
    實際為真的樣本中，正確預測的比例。
    recall = (∣Prediction ∩ Answer∣​ / |Answer∣) * 100
    """
    TP = 0
    for item_l in predLIST:
        if item_l in ansLIST:
            TP += 1

    print(f"正確預測：{TP}")
    print(f"正確答案：{len(ansLIST)}")
    recall = TP / len(ansLIST)
    print(f"recall: {recall * 100:.2f}%")
    print(f"================================")

def getPrecision(predLIST, ansLIST, kaFunction):
    """
    陽性樣本中，正確預測的比例。
    """
    TP = 0
    for item_l in predLIST:
        if item_l in ansLIST:
            TP += 1

    print(f"正確預測：{TP}")
    print(f"正確答案：{len(ansLIST)}")
    precision = TP / len(predLIST)
    print(f"precision: {precision * 100:.2f}%")
    print(f"================================")

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

    accuracy = TP + TN / len(allAnsLIST)
    print(f"accuracy: {accuracy * 100:.2f}%")
    print(f"================================")

if __name__ == "__main__":
    COMPAnsLIST, andAnsLIST, RELAnsLIST = createAnswer()
    COMPPredLIST, andPredLIST, RELPredLIST = makePrediction()   # The prediction is made respectively

    functionDICT = {
        "COMP": (COMPPredLIST, COMPAnsLIST),
        "and":  (andPredLIST,  andAnsLIST),
        "REL":  (RELPredLIST,  RELAnsLIST),
    }

    allAnsLIST = COMPAnsLIST + andAnsLIST + RELAnsLIST
    print(f"===== 個別 Project 結果 =====")
    for keySTR, (predLIST, ansLIST) in functionDICT.items():
        print(f"[{keySTR}]")
        getRecall(predLIST, ansLIST)
        getPrecision(predLIST, ansLIST, keySTR)
        getAccuracy(predLIST, ansLIST, allAnsLIST)