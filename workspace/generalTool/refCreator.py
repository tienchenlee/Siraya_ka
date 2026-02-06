#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging

from math import ceil
from pathlib import Path
from pprint import pprint
#from preLokiTool import udFilter
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

accountPATH = Path.cwd().parent / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

G_projectDICT = {
    "and": "Coordinator",
    "COMP": "Complementizer",
    "REL": "Relativizer"
}

G_lokiCallURL = "https://nlu.droidtown.co/Loki_EN/Call/"

def _articutEN(inputSTR, udDICT):
    """
    使用 Articut 英文版 StandardAPI 對輸入的文字進行詞性標記 (POS)。

    參數:
        inputSTR (str): 需要進行詞性標記的英文文字。
        udDICT (dict)：使用自定義字典。

    回傳:
        list: 詞性標記後的結果，返回 result_pos 內容。
    """
    payload = {
        "username": accountDICT["username"],
        "api_key": accountDICT["api_key"],
        "input_str": inputSTR,
        "user_defined_dict_file": udDICT
    }

    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
    except:
        print(response.status_code)
        print(response.text)

    return resultDICT

def _getPosSTR(inputSTR):
    """
    找到目標句的 POS 結果。

    argument:
        inputSTR 正在處理的句子。

    return:
        posSTR 為 inputSTR 的 POS 結果。
    """
    udPATH = Path.cwd().parent.parent / "data" / "userDefined.json"
    with open(udPATH, "r", encoding="utf-8") as f:
        udDICT =json.load(f)

    resultDICT = _articutEN(inputSTR, udDICT)
    posSTR = resultDICT["result_pos"][0].replace(" ", "")

    return posSTR

def createRef():
    """
    寫出 refFILE
    """
    verbVarKey = "CP_taking_Verb"
    outputDIR = Path(f"{Path.cwd()}/Complementizer/optimized/{verbVarKey}")
    with open(file=f"{outputDIR}/newIntentDICT.json", mode="r", encoding="utf-8") as f:
        verbDICT = json.load(f)

    testLIST = ["speak"]
    for verbSTR, uttLIST in verbDICT.items():
        if verbSTR in testLIST:
            refDICT = {
                "language": "en-us",
                "type": "advance",
                "version": {
                    "atk": "v102",
                    "intent": "1.0"
                    },
                "utterance": {}
            }

            for pairLIST in uttLIST:
                inputSTR = pairLIST[0]
                patternSTR = pairLIST[1]
                posSTR = _getPosSTR(inputSTR)

                refDICT["utterance"][inputSTR] = {
                    "pos": posSTR,
                    "pattern": patternSTR
                }

            refPATH = outputDIR / f"{verbVarKey}_{verbSTR}.ref"
            with open(refPATH, "w", encoding="utf-8") as f:
                json.dump(refDICT, f, ensure_ascii=False, indent=4)

def updateRegexVar():
    """
    Align regex var in three projects (Relativizer, Complementizer, Coordinator).
    """
    varPATH = Path.cwd().parent.parent / "data" / "Complementizer_var.json"
    with open(varPATH, "r", encoding="utf-8") as f:
        varDICT = json.load(f)

    #loki_keys = ["Complementizer", "Coordinator", "Relativizer"]
    #for loki_key in loki_keys:
    payload = {
      "username": accountDICT["username"],
      "loki_key": "URFmzUpw636F27Q7Hlq$h^l@Ep4OKVi",
      # Reset Var
      "func": "reset_var",
      "data": {},
      # Update var
      "func": "update_var",
      "data": {
          "var": varDICT
      }
    }

    #resultDICT = post(G_lokiCallURL, json=payload).json()
    ##print(f"Update regex Var with {loki_key}:")
    #print(resultDICT)
    #print()
    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
        print(f"更新 var：{resultDICT}")
    except:
        print(response.status_code)
        print(response.text)

    return resultDICT

def updateUd():
    """
    Align ud in three projects (Relativizer, Complementizer, Coordinator).
    """
    udPATH = Path.cwd().parent.parent / "data" / "userDefined.json"
    with open(udPATH, "r", encoding="utf-8") as f:
        udDICT = json.load(f)

    #loki_keys = ["Complementizer", "Coordinator", "Relativizer"]
    #for loki_key in loki_keys:

    payload = {
        "username": accountDICT["username"],
        "loki_key": "URFmzUpw636F27Q7Hlq$h^l@Ep4OKVi",
        "func": "reset_userdefined",
        "data": {},
        "func": "update_userdefined",
        "data": {
            "user_defined": udDICT
        }
    }

    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
        print(f"更新 ud：{resultDICT}")
    except:
        print(response.status_code)
        print(response.text)

    return resultDICT

def importRef():
    refDIR = Path(f"{Path.cwd()}/Complementizer/optimized/")
    refLIST = [file for file in refDIR.rglob("*.ref")]

    for refFILE in refLIST:
        refDICT = json.load(open(refFILE, encoding="utf-8"))
        intentSTR = refFILE.stem

        payload = {
          "username": accountDICT["username"],
          "loki_key": "URFmzUpw636F27Q7Hlq$h^l@Ep4OKVi",
          "intent": intentSTR,
          "func": "import_ref",
          "data": {"ref": refDICT}
        }

        try:
            response = post(G_lokiCallURL, json=payload)
            resultDICT = response.json()
            print(f"匯入意圖：{resultDICT}")
        except:
            print(response.status_code)
            print(response.text)

        return resultDICT

def deployModel():
    payload = {
        "username" : accountDICT["username"],
        "loki_key" : "URFmzUpw636F27Q7Hlq$h^l@Ep4OKVi",
        "func": "deploy_model",
        "data": {}
    }

    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
        print(f"部署模型：{resultDICT}")
    except:
        print(response.status_code)
        print(response.text)

    return resultDICT

def main():
    #updateRegexVar()
    #updateUd()
    importRef()
    deployModel()

if __name__ == "__main__":
    main()
    #resultDICT = importRef()
    #print(resultDICT)