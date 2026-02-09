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
        logging.FileHandler(Path.cwd() / "refCreator.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

accountPATH = Path(f"{Path.cwd().parent}/account.info")
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

G_udPATH = Path(f"{Path.cwd().parent.parent}/data/userDefined.json")
with open(G_udPATH, "r", encoding="utf-8") as f:
    G_udDICT = json.load(f)

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

    response = post(url="https://nlu.droidtown.co/Articut_EN/API/", json=payload)

    try:
        resultDICT = response.json()
        return resultDICT
    except ValueError:
        logging.warning(f"non-JSON response:{inputSTR}")
        logging.warning(f"status={response.status_code}")
        logging.warning(response.text)
        return None

def _getPosSTR(inputSTR):
    """
    找到目標句的 POS 結果。

    argument:
        inputSTR 正在處理的句子。

    return:
        posSTR 為 inputSTR 的 POS 結果。
    """
    resultDICT = _articutEN(inputSTR, G_udDICT)
    sleep(0.8)

    try:
        posSTR = resultDICT["result_pos"][0].replace(" ", "")
        return posSTR
    except Exception as e:
        logging.warning(f"pos parse failed: {e}")
        logging.warning(resultDICT)
        return None

def _verifyPattern(projectSTR, inputSTR, patternSTR):
    """"""
    payload = {
      "username": accountDICT["username"],
      "loki_key": accountDICT[projectSTR],
      "intent": "test",
      "func": "verify_pattern",
      "data": {
        "utterance": inputSTR,
        "pattern": patternSTR
      }
    }

    resultDICT = post(G_lokiCallURL, json=payload).json()
    print(f"比對句型：{resultDICT}")

    if resultDICT["msg"] == "Success!":
        return True

    return False

def createRef(verbVarKey, projectSTR):
    """
    寫出 refFILE
    """
    outputDIR = Path(f"{Path.cwd()}/{projectSTR}/optimized/{verbVarKey}")
    with open(file=f"{outputDIR}/newIntentDICT.json", mode="r", encoding="utf-8") as f:
        verbDICT = json.load(f)

    with open(file=f"{outputDIR}/noV2LIST.json", mode="r", encoding="utf-8") as f:
        noV2LIST = json.load(f)

    # 寫出 pattern 中，有 V2 的 intent
    for verbSTR, uttLIST in verbDICT.items():
        print(f"寫出意圖：{verbSTR}")
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

            if _verifyPattern(projectSTR, inputSTR, patternSTR):
                posSTR = _getPosSTR(inputSTR)

                refDICT["utterance"][inputSTR] = {
                    "pos": posSTR,
                    "pattern": patternSTR
                }

        refPATH = outputDIR / f"{verbVarKey}_{verbSTR}.ref"
        with open(refPATH, "w", encoding="utf-8") as f:
            json.dump(refDICT, f, ensure_ascii=False, indent=4)

    # 寫出 pattern 中，沒有 V2 的 intent
    BATCH_SIZE = 10 # 每 10 句為一個 intent
    batchesINT = ceil(len(noV2LIST) / BATCH_SIZE) # 計算要送幾批
    print(f"沒有 V2 的句型：總共 {len(kaLIST)} 筆，分成 {batchesINT} 批")

    for i in range(batchesINT):
        start = i * BATCH_SIZE
        end = start + BATCH_SIZE
        intentLIST = noV2LIST[start:end]

        print(f"寫出意圖：noV2_{i}")
        refDICT = {
            "language": "en-us",
            "type": "advance",
            "version": {
                "atk": "v102",
                "intent": "1.0"
                },
            "utterance": {}
        }

        for item_l in intentLIST:
            inputSTR = item_l[0]
            patternSTR = item_l[1]
            posSTR = _getPosSTR(inputSTR)

            refDICT["utterance"][inputSTR] = {
                            "pos": posSTR,
                            "pattern": patternSTR
                        }

        refPATH = outputDIR / f"noV2_{i}.ref"
        with open(refPATH, "w", encoding="utf-8") as f:
            json.dump(refDICT, f, ensure_ascii=False, indent=4)

def updateRegexVar(projectSTR):
    """
    Align regex var in three projects (Relativizer, Complementizer, Coordinator).
    """
    varPATH = Path(f"{Path.cwd().parent.parent}/data/{projectSTR}_var.json")
    with open(varPATH, "r", encoding="utf-8") as f:
        varDICT = json.load(f)

    payload = {
      "username": accountDICT["username"],
      "loki_key": accountDICT[projectSTR],
      # Reset Var
      "func": "reset_var",
      "data": {},
      # Update var
      "func": "update_var",
      "data": {
          "var": varDICT
      }
    }

    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
        print(f"更新 {projectSTR} 變數：{resultDICT}")
    except:
        print(response.status_code)
        print(response.text)

def updateUd(projectSTR):
    """
    Align ud in three projects (Relativizer, Complementizer, Coordinator).
    """
    payload = {
        "username": accountDICT["username"],
        "loki_key": accountDICT[projectSTR],
        "func": "reset_userdefined",
        "data": {},
        "func": "update_userdefined",
        "data": {
            "user_defined": G_udDICT
        }
    }

    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
        print(f"更新 {projectSTR} 自定義辭典：{resultDICT}")
    except:
        print(response.status_code)
        print(response.text)

def importRef(projectSTR):
    refDIR = Path(f"{Path.cwd()}/{projectSTR}/optimized/")
    refLIST = [file for file in refDIR.rglob("*.ref")]

    for idx, refFILE in enumerate(refLIST, start=1):
        refDICT = json.load(open(refFILE, encoding="utf-8"))
        intentSTR = refFILE.stem.replace(".", "_").replace("-", "_")

        payload = {
          "username": accountDICT["username"],
          "loki_key": accountDICT[projectSTR],
          "intent": intentSTR,
          "func": "import_ref",
          "data": {"ref": refDICT}
        }

        try:
            response = post(G_lokiCallURL, json=payload)
            resultDICT = response.json()
            print(f"匯入意圖 {idx}：{resultDICT}")
        except ValueError:
            logging.warning(f"non-JSON response:{intentSTR}")
            logging.warning(f"status={response.status_code}")
            logging.warning(response.text)
            return None

def deployModel(projectSTR):
    payload = {
        "username" : accountDICT["username"],
        "loki_key" : accountDICT[projectSTR],
        "func": "deploy_model",
        "data": {}
    }

    try:
        response = post(G_lokiCallURL, json=payload)
        resultDICT = response.json()
        print(f"部署模型：{resultDICT}")
    except ValueError:
        logging.warning(f"non-JSON response: Deploy Model")
        logging.warning(f"status={response.status_code}")
        logging.warning(response.text)
        return None

def main():
    verbVarKey = "V2"
    projectLIST = ["Coordinator_Dep", "Relativizer_Dep"]

    for projectSTR in projectLIST:
        createRef(verbVarKey, projectSTR)
        updateRegexVar(projectSTR)
        updateUd(projectSTR)
        importRef(projectSTR)
        deployModel(projectSTR)

if __name__ == "__main__":
    main()