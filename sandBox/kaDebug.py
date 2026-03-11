#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from copy import deepcopy
import glob
import json
import re
import shutil
import sys
import os

from datetime import datetime
from pathlib import Path
from requests import post
from time import sleep


from Loki_and.Coordinator.main import askLoki as askLokiAND
from Loki_REL.Relativizer.main import askLoki as askLokiREL
from Loki_COMP.Complementizer.main import askLoki as askLokiCOMP

accountPATH = Path.cwd() / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def _getInfo(mode="offline", dockerurl=None, username="", loki_key=""):
    """"""
    print("getInfo")
    print("mode =", mode)

    if mode == "offline":
        url = dockerurl
        payload = {
            "project": "debugger_ka",
            "func": "get_info",
            "data": {}
        }
    else:
        url = "https://nlu.droidtown.co/Loki_EN/Call/"
        payload = {
            "username" : username,
            "loki_key": loki_key,
            "func": "get_info",
            "data": {}
        }
    response = post(url, json=payload)
    print(f"status of getting info:{response.status_code}")

    try:
        resultDICT = response.json()
        return resultDICT
    except:
        print(response.status_code)
        print(response.text)

def _varPacker(refFILE, inputLIST, mode, username, loki_key):
    """
    read *.ref file and shrink down the size of all var.
    """

    resultDICT = _getInfo(mode=mode, username=username, loki_key=loki_key)
    intentDICT = resultDICT["result"]["intent"]

    for valueLIST in intentDICT.values():
        inputLIST.extend(valueLIST)

    jFILE = json.load(open(refFILE, encoding="utf-8"))
    varDICT = jFILE["var"]
    resultDICT = {}
    for k in varDICT:
        resultDICT[k] = []
        pat = re.compile(varDICT[k])
        for i_s in inputLIST:
            resultDICT[k].extend([p.group() for p in pat.finditer(i_s)])
        resultDICT[k] = list(set(resultDICT[k]))
    for v in resultDICT:
        if resultDICT[v] == [""]:
            resultDICT[v] = []

    return resultDICT

def _refCreator(refDIR, varDICT):
    try:
        shutil.rmtree("./debug_ref", ignore_errors=True)
    except:
        pass
    os.mkdir("./debug_ref")
    for ref_F in glob.glob(f"{refDIR}/*.ref"):
        refDICT = json.load(open(ref_F))
        var = refDICT["var"]
        for k in refDICT["var"]:
            if k in varDICT and varDICT[k] != []:
                var[k] = "(?:" + "|".join(varDICT[k]) + ")"
            else:
                var[k] = refDICT["var"][k]
        refDICT["var"] = var
        fileName = f"./debug_ref/{ref_F.split('/')[-1]}"
        with open(fileName, "w", encoding="utf-8") as f:
            json.dump(refDICT, f, ensure_ascii=False)

def _createProject(mode="offline", dockerurl=None, username=""):
    if mode == "offline":
        url = dockerurl
        payload = {
            "func": "create_project",
            "data": {
                "name": "debugger_ka",
        }
    }
    else:
        url = "https://nlu.droidtown.co/Loki_EN/Call/"  #英文版線上 URL
        payload = {
            "username" : username, # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。
            "func": "create_project",
            "data": {
                "name": "debugger_ka",
        }
    }
    try:
        response = post(url, json=payload).json()
        if response["status"] == True:
            return response
        else:
            return response["msg"]
    except Exception as e:
        return e

def _deployModel(mode="offline", dockerurl=None, username="", loki_key=""):
    print("[Deploy Model]")
    print("mode =", mode)
    if mode == "offline":
        url = dockerurl
        payload = {
            "project": "debugger_ka",
            "func": "deploy_big_model",
            "data": {}
        }
    else:
        url = "https://nlu.droidtown.co/Loki_EN/Call/"  #英文版線上 URL
        payload = {
            "username" : username,
            "loki_key" : loki_key,
            "func": "deploy_big_model",
            "data": {}
        }

    response = post(url, json=payload)
    print(f"status of deploy model:{response.status_code}")
    if response.status_code == 504:
        return response.status_code

    try:
        response = response.json()
        print(f"response of deploy model:{response}")
        if response["status"] == True:
            return True
        else:
            return response["msg"]
    except Exception as e:
        return e

def _checkModel(mode="offline", dockerurl=None, username="", loki_key=""):
    print("[Check Model]")
    print("mode =", mode)
    if mode == "offline":
        url = dockerurl
        payload = {
            "project": "debugger_ka",
            "func": "check_model",
            "data": {}
        }
    else:
        url = "https://nlu.droidtown.co/Loki_EN/Call/"  #英文版線上 URL
        payload = {
            "username" : username,
            "loki_key" : loki_key,
            "func": "check_model",
            "data": {}
        }

    response = post(url, json=payload)
    print(f"status of checking model:{response.status_code}")

    try:
        response = response.json()
        print(response)
        return response
        #if response["status"] == True:
            #print(f"reponse of checking model:{response}")
            #return response
        #else:
            #return response["msg"]
    except Exception as e:
        return e

#=======
def debEnvBuilder(refFILE, refDIR, inputLIST, mode, username, kaFunction):
    varDICT = _varPacker(refFILE, inputLIST, mode=mode, username=username, loki_key=accountDICT[kaFunction])
    _refCreator(refDIR, varDICT)

    createResult = _createProject(mode=mode, username=username)
    if createResult["status"] == True:
        pause = input("[Action Required]: 請先打開 debug_ref 目錄，將其中的  *.ref 檔匯入 debugger_ka 專案！")
    else:
        print(createResult)
        sys.exit(0)

    loki_key = createResult["loki_key"]
    pause = input("按下 Enter 開始部署模型！[Enter to continue.]")
    pause = input("模型部署中，請稍候… [Enter to continue.]")
    STARTTIME = datetime.now()
    deployResult = _deployModel(mode=mode, username=username, loki_key=loki_key)

    if deployResult == True or deployResult == 504:
        print("[Deployment Succeed]")

        while True:
            checkResult = _checkModel(mode=mode, username=username, loki_key=loki_key)

            if checkResult["status"] == True:
                if checkResult["progress_status"] == "completed":
                    ENDTIME = datetime.now()
                    print(f"Model is ready")
                    break

            print(f"Model is not ready....")
            sleep(5)

    print(f"總共花了：{ENDTIME-STARTTIME} 時間完成部署。")

def findUtterAND(inputSTR, mode, username):
    refDICT = {"inputSTR":[], "utterance":[], "and":[], "ka_index": []}
    intentLIST = []

    resultDICT = _getInfo(mode=mode, username=username, loki_key=accountDICT["Coordinator"])
    intentDICT = resultDICT["result"]["intent"]

    for keySTR in intentDICT.keys():
        intentLIST.append(keySTR)

    resultLIST = []

    for intent_s in intentLIST:
        print(f"intent: {intent_s}")
        attempts = 0
        success = False

        while attempts < 3 and not success:
            lokiResultDICT = askLokiAND(inputSTR, filterLIST=[intent_s], refDICT=refDICT)
            print(lokiResultDICT)
            print()
            sleep(0.8)

            if "msg" in lokiResultDICT.keys():   # Server Error 會回傳 status
                attempts += 1
                sleep(5)
            else:
                success = True

                if lokiResultDICT["ka_index"] and lokiResultDICT["and"]:
                    resultLIST.append(lokiResultDICT)   # 跑單一 project 的結果

    return resultLIST

def findUtterREL(inputSTR, mode, username):
    refDICT = {"inputSTR":[], "utterance":[], "REL": [], "ka_index": []}
    intentLIST = []

    resultDICT = _getInfo(mode=mode, username=username, loki_key=accountDICT["Relativizer"])
    intentDICT = resultDICT["result"]["intent"]

    for keySTR in intentDICT.keys():
        intentLIST.append(keySTR)

    resultLIST = []

    for intent_s in intentLIST:
        print(f"intent: {intent_s}")
        attempts = 0
        success = False

        while attempts < 3 and not success:
            lokiResultDICT = askLokiREL(inputSTR, filterLIST=[intent_s], refDICT=refDICT)
            print(lokiResultDICT)
            print()
            sleep(0.8)

            if "msg" in lokiResultDICT.keys():   # Server Error 會回傳 status
                attempts += 1
                sleep(5)
            else:
                success = True

                if lokiResultDICT["ka_index"] and lokiResultDICT["REL"]:
                    resultLIST.append(lokiResultDICT)   # 跑單一 project 的結果

    return resultLIST

def findUtterCOMP(inputSTR, mode, username):
    refDICT = {"inputSTR":[inputSTR], "utterance":[], "COMP": [], "ka_index": [], "debug_info": []}
    intentLIST = []

    resultDICT = _getInfo(mode=mode, username=username, loki_key=accountDICT["Complementizer"])
    intentDICT = resultDICT["result"]["intent"]

    for keySTR in intentDICT.keys():
        intentLIST.append(keySTR)

    resultLIST = []

    for intent_s in intentLIST:
        print(f"intent: {intent_s}")
        attempts = 0
        success = False

        while attempts < 3 and not success:
            lokiResultDICT = askLokiCOMP(inputSTR, filterLIST=[intent_s], refDICT=refDICT)
            print(lokiResultDICT)
            print()
            sleep(0.8)

            if "msg" in lokiResultDICT.keys():   # Server Error 會回傳 status
                attempts += 1
                sleep(5)
            else:
                success = True

                if lokiResultDICT["ka_index"] and lokiResultDICT["COMP"]:
                    resultLIST.append(lokiResultDICT)   # 跑單一 project 的結果

    return resultLIST


if __name__ == "__main__":

    MODE = "online"
    USERNAME = "appielee4305@gmail.com"
    kaFUNCTION = "Complementizer" #Relativizer, Complementizer, Coordinator

    refFILE = f"./ka_Backups/Loki_Backup/{kaFUNCTION}/ref/V2.ref"    # Complementizer: V2
    refDIR =  f"./ka_Backups/Loki_Backup/{kaFUNCTION}/ref/"
    inputLIST = json.load(open("./ka_Backups/data/kaLIST.json", encoding="utf-8"))

    #debEnvBuilder(refFILE, refDIR, inputLIST, mode=MODE, username=USERNAME, kaFunction=kaFUNCTION)
    #=======

    debugData = "./ka_Backups/data/kaLIST.json"
    inputLIST = json.load(open(debugData, encoding="utf-8"))
    #inputSTR = inputLIST[1]
    #inputSTR = "LOC hear -PV OBL this OBL disciple his greatly .AV PAST- marvel .AV NOM they ka PAST- say .AV who NOM PC. able -LV .IRR if that save .AV"

    resultLIST = []
    for inputSTR in inputLIST:
        print("除錯:", inputSTR)
        debugResult = findUtterCOMP(inputSTR, mode=MODE, username=USERNAME)
        resultLIST.extend(debugResult)
    #debugResult = findUtterREL(inputSTR, mode=MODE, username=USERNAME)
    #debugResult = findUtterAND(inputSTR, mode=MODE, username=USERNAME)
    print(resultLIST)

    predictionDIR = Path(f"{Path.cwd()}/ka_Backups/data/prediction")
    predictionDIR.mkdir(exist_ok=True, parents=True)
    with open(f"{predictionDIR}/COMP.json", "w", encoding="utf-8") as f:
        json.dump(resultLIST, f, ensure_ascii=False, indent=4)