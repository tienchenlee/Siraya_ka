#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from datetime import datetime
from requests import post
from pathlib import Path
from time import sleep

accountPATH = Path.cwd().parent / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def updateRegexVar():
    """
    Align regex var in three projects (Relativizer, Complementizer, Coordinator).
    """
    varPATH = Path.cwd().parent.parent / "data" / "VARIABLE.json"
    with open(varPATH, "r", encoding="utf-8") as f:
        varDICT = json.load(f)

    url = "https://nlu.droidtown.co/Loki_EN/Call/"
    loki_keys = ["Complementizer", "Coordinator", "Relativizer"]
    for loki_key in loki_keys:
        payload = {
          "username": accountDICT["username"],
          "loki_key": accountDICT[loki_key],
          # Reset Var
          "func": "reset_var",
          "data": {},
          # Update var
          "func": "update_var",
          "data": {
              "var": varDICT
          }
        }

        resultDICT = post(url, json=payload).json()
        print(f"Update regex Var with {loki_key}:")
        print(resultDICT)
        print()

def updateUd():
    """
    Align ud in three projects (Relativizer, Complementizer, Coordinator).
    """
    udPATH = Path.cwd().parent.parent / "data" / "userDefined.json"
    with open(udPATH, "r", encoding="utf-8") as f:
        udDICT = json.load(f)

    url = "https://nlu.droidtown.co/Loki_EN/Call/"
    loki_keys = ["Complementizer", "Coordinator", "Relativizer"]
    for loki_key in loki_keys:

        payload = {
            "username": accountDICT["username"],
            "loki_key": accountDICT[loki_key],
            "func": "reset_userdefined",
            "data": {},
            "func": "update_userdefined",
            "data": {
                "user_defined": udDICT
            }
        }

        resultDICT = post(url, json=payload).json()
        print(f"Update UD with {loki_key}:")
        print(resultDICT)
        print()

def _deployModel(mode="offline", dockerurl=None, username="", loki_key=""):
    print("[Deploy Model]")
    print("mode =", mode)
    if mode == "offline":
        url = dockerurl
        payload = {
            "project": "",
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
            "project": "",
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
    except Exception as e:
        return e

def envBuilder(mode, username, loki_key):
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

if __name__ == "__main__":
    #updateRegexVar()
    #updateUd()
    #print(f"記得更新 ka 在不同 project 的 capturing group!")
    #print(f"記得更新各個 Loki_project/intent/USER_DEFINED.json")

    # deploy model
    PROJECT = "Relativizer" #Complementizer, Coordinator, Relativizer
    envBuilder(mode="online", username=accountDICT["username"], loki_key=accountDICT[PROJECT])

