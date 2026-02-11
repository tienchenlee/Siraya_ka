#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from requests import post
from pathlib import Path
import json
import logging
import os
import re

CWD_PATH = os.path.dirname(os.path.abspath(__file__))

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

MODULE_DICT = {
    "Account": import_from_path("Relativizer_lib_Account", os.path.join(os.path.dirname(CWD_PATH), "lib/Account.py")),
    "LLM": import_from_path("Relativizer_lib_LLM", os.path.join(os.path.dirname(CWD_PATH), "lib/LLM.py"))
}
"""
Account Variables
[Variable] BASE_PATH         => path of root
[Variable] LIB_PATH          => path of lib folder
[Variable] INTENT_PATH       => path of intent folder
[Variable] REPLY_PATH        => path of reply folder
[Variable] ACCOUNT_DICT      => account.info
[Variable] ARTICUT           => ArticutAPI (Usage: ARTICUT.parse()。 #ArticutAPI Required.)
[Variable] USER_DEFINED_FILE => path of UserDefined
[Variable] USER_DEFINED_DICT => UserDefined data
"""
REPLY_PATH = MODULE_DICT["Account"].REPLY_PATH
ACCOUNT_DICT = MODULE_DICT["Account"].ACCOUNT_DICT
ARTICUT = MODULE_DICT["Account"].ARTICUT
USER_DEFINED_FILE = MODULE_DICT["Account"].USER_DEFINED_FILE
USER_DEFINED_DICT = MODULE_DICT["Account"].USER_DEFINED_DICT
getLLM = MODULE_DICT["LLM"].getLLM
accDICT = json.load(open(f"{Path(CWD_PATH).parent}/account.info", "r", encoding="utf-8"))

def tmpAskLoki(inputSTR):
    url = accDICT["server"]
    intentLIST = []
    payload = {
        "username" : accDICT["username"],
        "loki_key": accDICT["loki_key"],
        "project": accDICT["loki_project"],
        "func": "get_info",
        "data": {}
    }
    #print("getIntent")
    response = post(url="https://nlu.droidtown.co/Loki_EN/Call/", json=payload)
    try:
        response = response.json()
        if response["status"] == True:
            intentDICT = response["result"]["intent"]
            intentLIST = [intent for intent in intentDICT.keys()]
            print(intentLIST)
        else:
            print(f"getIntent:{response}")
            return None
    except:
        print(response["msg"])

    resultLIST = []

    for intent_s in intentLIST:
        payload = {
            "project": accDICT["loki_project"],
            "input_str": inputSTR,
            "intent": intent_s
        }
        #print("askLoki")
        response = post(f"{url}/Loki_EN/API/", json=payload)

        try:
            response = response.json()
            resultLIST.append(response)

            if response.get("results"):
                breakkaCaptureTool.py

        except Exception as e:
            print(e)
            print(payload)
            print(f"askLoki:{response}")
            raise

    return resultLIST

def getKaCharIdx(inputSTR, utterPat, targetArgINT):
    """"""
    engArticut = ARTICUT.parse(inputSTR, USER_DEFINED_FILE)
    if engArticut["status"] == True:
        if "," in engArticut["result_pos"]:
            posSTR = ",".join(engArticut["result_pos"]).replace(",", "")
            engArticut["result_pos"] = [posSTR]
kaCaptureTool.py
        inputPosSTR = engArticut["result_pos"][0].replace("> <", "><")

    for k_t in [(k.start(targetArgINT+1), k.end(targetArgINT+1), k.group(targetArgINT+1)) for k in utterPat.finditer(inputPosSTR)]:
        if k_t[2] == "ka":
            kaCharIdx = k_t[0]

    return kaCharIdx

def _getKaIdx(inputSTR, utterPat, targetArgINT):
    """
    1. Articut inputSTR
    2. Get the string that before the target 'ka'
    3. Count the index of 'ka'
    4. Return the index
    """
    engArticut = ARTICUT.parse(inputSTR, USER_DEFINED_FILE)
    if engArticut["status"] == True:
        if "," in engArticut["result_pos"]:
            posSTR = ",".join(engArticut["result_pos"]).replace(",", "")
            engArticut["result_pos"] = [posSTR]

        inputPosSTR = engArticut["result_pos"][0].replace("> <", "><")

    kaIdxLIST = []

    for k_t in [(k.start(targetArgINT+1), k.end(targetArgINT+1), k.group(targetArgINT+1)) for k in utterPat.finditer(inputPosSTR)]:
        kaIdxLIST.append(k_t)

    kaIdxLIST = [kaIdx_t for kaIdx_t in kaIdxLIST if kaIdx_t[2] == "ka"]
    if kaIdxLIST:
        targetKaIdx = inputPosSTR[:kaIdxLIST[0][0]].count("</")
        # 一個字會被 articut 切成兩個字
        if re.search(r"<MODAL>do</MODAL><FUNC_negation>not</FUNC_negation>.*?<UserDefined>ka</UserDefined>", inputPosSTR[:kaIdxLIST[0][1]+1]):
            targetKaIdx -= 1
        # 如果 ud 內的單字含空格，要補加一個 idx
        if re.search(r"(?<=>)[^>]+\s.*?<UserDefined>ka<", inputPosSTR[:kaIdxLIST[0][1]+1]):
            targetKaIdx += 1
    else:
        logging.error(f"找不到 kaIdxLIST: {inputSTR}")
        return -1

    return targetKaIdx

def kaCapture(args, pattern, inputSTR, resultDICT):
    targetArgLIST = []     # 在 Loki 上為第幾個 arg

    for i in range(0, len(args)):
        if args[i] == "ka":
            targetArgLIST.append(i)

    REL = False

    for targetArgINT in targetArgLIST:
        utterPat = re.compile(pattern)
        targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
        resultDICT["ka_index"].append(targetKaIdx)
        REL = True

    return REL
