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
from requests import post
from time import sleep


from Loki_and.Coordinator.main import askLoki as askLokiAND

def _varPacker(refFILE, inputLIST):
    """
    read *.ref file and shrink down the size of all var.
    """
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
                var[k] = "|".join(varDICT[k])
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
    if mode == "offline":
        url = dockerurl
        payload = {
            "project": "debugger_ka",
            "func": "deploy_model",
            "data": {}
        }
    else:
        url = "https://nlu.droidtown.co/Loki_EN/Call/"  #英文版線上 URL
        payload = {
            "username" : username,
            "loki_key" : loki_key,
            "func": "deploy_model",
            "data": {}
        }
    try:
        response = post(url, json=payload).json()
        if response["status"] == True:
            return response
        else:
            return response["msg"]
    except Exception as e:
        return e

def _checkModel(mode="offline", dockerurl=None, username="", loki_key=""):
    if mode == "offline":
        url = dockerurl
        payload = {
            "project": "debugger_ka",
            "func": "check_model",
            "data": {}
        }
    else:
        payload = {
            "username" : username,
            "loki_key" : loki_key,
            "func": "check_model",
            "data": {}
        }
    try:
        response = post(url, json=payload).json()
        if response["status"] == True:
            return response
        else:
            return response["msg"]
    except Exception as e:
        return e

#=======
def debEnvBuilder(refFILE, refDIR, inputLIST, mode, username):
    varDICT = _varPacker(refFILE, inputLIST)
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
    deployResult = _deployModel(mode=MODE, username=USERNAME, loki_key=loki_key)

    #counter = 3
    #sleep(1)
    #if deployResult == True:
    ENDTIME = datetime.now()
    print(deployResult)
    if "504 Gateway Time-out" in deployResult:
        pause = input("還…還在部署中，請稍候… [Enter to continue.]")
        sleep(60)

    print(f"總共花了：{ENDTIME-STARTTIME} 時間完成部署。")
    return loki_key

def findUtterAND(inputSTR):
    refDICT = {"utterance":[], "intent":[], "pattern":[], "and":[]}
    resultDICT = askLokiAND(inputSTR, refDICT=refDICT)
    return resultDICT


if __name__ == "__main__":

    MODE = "online"
    USERNAME = "peter.w@droidtown.co"

    refFILE = "./ka_Backups/Loki_Backup/Coordinator/ref/CP_taking_Verb.ref"
    refDIR =  "./ka_Backups/Loki_Backup/Coordinator/ref/"
    inputLIST = json.load(open("./ka_Backups/data/andFP_relTP.json", encoding="utf-8"))

    #debEnvBuilder(refFILE, refDIR, inputLIST)
    #=======

    debugData = "./ka_Backups/data/andFP_relTP.json"
    inputLIST = json.load(open(debugData, encoding="utf-8"))
    inputSTR = inputLIST[0]
    print("除錯:", inputSTR)
    debugResult = findUtterAND(inputSTR)
    print(debugResult)