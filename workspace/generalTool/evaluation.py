#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
from pathlib import Path

G_kaPat = re.compile(r"\bka\b")
G_resultDIR = Path(f"{Path.cwd().parent.parent}/data/results")
G_resultDIR.mkdir(exist_ok=True, parents=True)
G_srcDIR = Path(f"{Path.cwd().parent.parent}/data/src")
G_performanceDIR = Path(f"{Path.cwd().parent.parent}/data/performance")
G_performanceDIR.mkdir(exist_ok=True, parents=True)

def createAnswer(phase=None, coverage=False):
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
    SUFFIX = "_coverage" if coverage else ""

    if coverage:
        with open(f"{G_srcDIR}/kaLIST.json", "r", encoding="utf-8") as f:
            kaLIST = json.load(f)

        with open(f"{G_srcDIR}/ansLIST.json", "r", encoding="utf-8") as f:
            ansLIST = json.load(f)
    else:
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

    with open(f"{ansPhaseDIR}/REL{SUFFIX}.json", "w", encoding="utf-8") as f:
        json.dump(RELLIST, f, ensure_ascii=False, indent=4)

    with open(f"{ansPhaseDIR}/COMP{SUFFIX}.json", "w", encoding="utf-8") as f:
        json.dump(COMPLIST, f, ensure_ascii=False, indent=4)

    with open(f"{ansPhaseDIR}/and{SUFFIX}.json", "w", encoding="utf-8") as f:
        json.dump(andLIST, f, ensure_ascii=False, indent=4)

    return COMPLIST, andLIST, RELLIST, len(targetLIST)

def makePrediction(phase=None, coverage=False):
    """
    將 predictionLIST 中的 lokiResultDICT 分別寫出與 answer/ 一樣的資料結構。
    在 mapDICT 選擇此次 askLoki 的專案。
    """
    SUFFIX = "_coverage" if coverage else ""
    kaLIST = ["COMP", "and", "REL"]
    predPhaseDIR = Path(f"{Path.cwd().parent.parent}/data/prediction/{phase}")
    predPhaseDIR.mkdir(exist_ok=True, parents=True)

    resultDICT = {}
    for KA in kaLIST:
        idxSET = set()
        with open(f"{G_resultDIR}/{KA}_{phase}{SUFFIX}.json", "r", encoding="utf-8") as f:
            predictionLIST = json.load(f)

        for lokiResultDICT in predictionLIST:   #處理每個 prediction item
            if KA in lokiResultDICT.keys():
                utter_index = lokiResultDICT["utter_index"][0]
                for ka_index in lokiResultDICT["ka_index"]:
                    idxSET.add((utter_index, ka_index))

        resultDICT[KA] = sorted(
            [list(pair) for pair in idxSET],
            key=lambda x: (x[0], x[1])
        )
        with open(f"{predPhaseDIR}/{KA}{SUFFIX}.json", "w", encoding="utf-8") as f:
            json.dump(resultDICT[KA], f, ensure_ascii=False, indent=4)

    return resultDICT["COMP"], resultDICT["and"], resultDICT["REL"]

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

def getRecall(predLIST, ansLIST, coverage=False):
    """
    實際為真的樣本中，正確預測的比例。
    recall = (∣Prediction ∩ Answer∣​ / |Answer∣) * 100
    """
    TP = _getTP(predLIST, ansLIST)
    FN = len(ansLIST) - TP
    recall = TP / len(ansLIST)

    if coverage:
        print(f"FN: {FN}")

    else:
        print(f"TP：{TP}")
        print(f"FN: {FN}")
        print(f"TP+FN：{len(ansLIST)}")
        print(f"recall: {recall * 100:.2f}%")
        print(f"--------------------------------")

    return FN, recall

def getPrecision(predLIST, ansLIST, coverage=False):
    """
    陽性樣本中，正確預測的比例。
    """
    TP = _getTP(predLIST, ansLIST)
    FP = len(predLIST) - TP
    precision = TP / len(predLIST)

    if coverage:
        print(f"FP: {FP}")

    else:
        print(f"TP：{TP}")
        print(f"FP: {FP}")
        print(f"TP+FP：{len(predLIST)}")
        print(f"precision: {precision * 100:.2f}%")
        print(f"--------------------------------")

    return FP, precision

def getAccuracy(totalKaINT, FN, FP, coverage=False):
    """
    預測正確的比例。
    """
    TP = _getTP(predLIST, ansLIST)
    TN = totalKaINT - TP - FP - FN
    accuracy = (TP + TN) / (TP + TN + FP + FN)

    if coverage:
        print(f"TN: {TN}")
        print(f"================================")
    else:
        print(f"TN: {TN}")
        print(f"TP+TN: {TP + TN}")
        print(f"TP+TN+FP+FN: {TP + TN + FP + FN}")
        print(f"accuracy: {accuracy * 100:.2f}%")
        print(f"--------------------------------")

    return TN

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
    print(f"--------------------------------")

def getF1score(recall, precision):
    """
    2 x Recall x Precision / (Recall + Precision)。
    Recall 及 Precision 的調和平均數。
    """
    f1 = 2 * recall * precision / (recall + precision)
    print(f"f1: {f1 * 100:.2f}%")
    print(f"================================")

if __name__ == "__main__":
    PHASE = "test" #test, eval
    COVERAGE = False #True, False

    COMPAnsLIST, andAnsLIST, RELAnsLIST, totalKaINT = createAnswer(phase=PHASE, coverage=COVERAGE)
    COMPPredLIST, andPredLIST, RELPredLIST = makePrediction(phase=PHASE, coverage=COVERAGE)   # The prediction is made respectively

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

        if COVERAGE:
            getCoverage(predLIST, ansLIST)
            # for calculating TN, FP, FN
            FN, recall = getRecall(predLIST, ansLIST, coverage=COVERAGE)
            FP, precision = getPrecision(predLIST, ansLIST, coverage=COVERAGE)
            getAccuracy(totalKaINT, FN, FP, coverage=COVERAGE)

        else:
            FN, recall = getRecall(predLIST, ansLIST, coverage=COVERAGE)
            FP, precision = getPrecision(predLIST, ansLIST, coverage=COVERAGE)
            getAccuracy(totalKaINT, FN, FP, coverage=COVERAGE)
            getF1score(recall, precision)

        if PHASE == "eval":
            fnLIST = extractFN(predLIST, ansLIST)
            allFnLIST.extend(fnLIST)

            with open(f"{G_performanceDIR}/eval/missedLIST.json", "w", encoding="utf-8") as f:
                json.dump(allFnLIST, f, ensure_ascii=False, indent=4)