#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V2_and_VP

    Input:
        inputSTR      str,
        utterance     str,
        args          str[],
        resultDICT    dict,
        refDICT       dict,
        pattern       str

    Output:
        resultDICT    dict
"""

from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from random import sample
import json
import os
import re
from pathlib import Path
from requests import post
import sys

G_mainPath = Path(sys.argv[0]).resolve()
if G_mainPath.name in ["ka_testing.py", "ka_identifier.py"]:
    try:
        from Loki_and.Coordinator.intent.kaCaptureTool import kaCapture, getKaCharIdx
    except:
        from .Loki_and.Coordinator.intent.kaCaptureTool import kaCapture, getKaCharIdx
else:
    try:
        from kaCaptureTool import kaCapture, getKaCharIdx
    except:
        from .kaCaptureTool import kaCapture, getKaCharIdx

INTENT_NAME = "V2_and_VP"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))
G_notVerbPAT = r"(?<=<UserDefined>)([a-zA-Z\-\.]{1,19})$"
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
    response = post(url="https://nlu.droidtown.co/Loki_EN/Call/", json=payload)
    print(f"getIntent:{response}")
    #response = response.json()["result"]["intent"].keys()
    try:
        response = response.json()
        if response["status_code"] == "200":
            intentLIST = response["result"]["intent"].keys()
        else:
            print(response)
            return None
    except:
        print(response["msg"])

    #intentLIST = [i for i in intentLIST]
    print(intentLIST)

    resultLIST = []

    for intent_s in intentLIST:
        payload = {
            "project": accDICT["loki_project"],
            "input_str": inputSTR,
            "intent": intent_s
        }

        response = post(url, json=payload)
        print(f"askLoki:{response}")
        response = response.json()
        resultLIST.append(response)

        if response["results"] != []:
            break

    return resultLIST

with open(f"{CWD_PATH}/USER_DEFINED.json", "r", encoding="utf-8") as f:
    udDICT = json.load(f)

verbLIST = udDICT["_asVerb_"]
nounLIST = udDICT["ENTITY_noun"]

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

MODULE_DICT = {
    "Account": import_from_path("Coordinator_lib_Account", os.path.join(os.path.dirname(CWD_PATH), "lib/Account.py")),
    "LLM": import_from_path("Coordinator_lib_LLM", os.path.join(os.path.dirname(CWD_PATH), "lib/LLM.py"))
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

# userDefinedDICT (Deprecated)
# Replace with USER_DEFINED_DICT of Account variable.
#userDefinedDICT = {}
#try:
#    userDefinedDICT = json.load(open(os.path.join(CWD_PATH, "USER_DEFINED.json"), encoding="utf-8"))
#except:
#    pass

replyDICT = {}
replyPathSTR = os.path.join(REPLY_PATH, "reply_{}.json".format(INTENT_NAME))
if os.path.exists(replyPathSTR):
    try:
        replyDICT = json.load(open(replyPathSTR, encoding="utf-8"))
    except Exception as e:
        print("[ERROR] reply_{}.json => {}".format(INTENT_NAME, str(e)))
CHATBOT = True if replyDICT else False

# Debug message
def debugInfo(inputSTR, utterance):
    if ACCOUNT_DICT["debug"]:
        print("[{}] {} ===> {}".format(INTENT_NAME, inputSTR, utterance))

def getReply(utterance, args):
    replySTR = ""
    try:
        replySTR = sample(replyDICT[utterance], 1)[0]
        if args:
            replySTR = replySTR.format(*args)
    except:
        pass

    return replySTR

getResponse = getReply
def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern="", toolkitDICT={}):
    debugInfo(inputSTR, utterance)
    if utterance == "PAST- find .PV he .GEN NOM one OBL stone ka worthy .AV go -LV he .GEN PC. all .AV sell .AV OBL things his ka buy -LV he .GEN NOM it":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- plait .PV they .GEN NOM crown ka PART thorn PAST- cause.on.head -PV they .GEN him -OBL NOM it put .AV OBL reed also LOC hand ka right his ka when fall.on.kneel .AV LOC front him -OBL":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PC. quick -LV .IRR you .PL .GEN find .AV NOM large.animal ka carry.on.back ka female.animal ka PAST tie ka have-together .AV OBL youngling":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "anyone NOM swear .AV -IRR -PFV OBL PART gift ka PAST- put.on -PV ka debt -LV .IRR NOM he":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "anyone NOM swear .AV -IRR -PFV OBL word PC- temple .AV OBL worship -PV OBL God ka nothing NOM it":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "cause.resemble -PV you .PL .NOM OBL graves ka whitewash -PV ka appear .AV beautiful .AV LOC surface":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "die .AV NOM someone ka not.have OBL children then marry .AV -IRR NOM brother his OBL PAST- wife -PV his ka cause.rise .AV -IRR OBL seed OBL brother his":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "do -PV .IRR also he .GEN ka PC. more .AV -IRR still OBL those":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "give.birth .AV -IRR OBL child ka man ka give.name .AV -IRR you .SG .NOM OBL name his Emmanuel":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "not .AV NOM anyone ka put.upon .AV OBL cloth ka not .AV yet OBL fold ka new .AV still LOC garment ka be.torn .AV ka old .AV for rend .AV NOM PART cloth OBL garment ka PC. bottom .AV -IRR rend .AV NOM rent":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "strain -PV you .PL .GEN NOM mosquito ka swallow -PV you .PL .GEN NOM large.animal ka camel":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                #<ka_capture_test>

                for i in range(0, len(args)):
                    if args[i] == "ka":
                        utterPat = re.compile(pattern)
                        kaIdx = getKaCharIdx(inputSTR=inputSTR, utterPat=utterPat, targetArgINT=i)
                        tmpInputSTR = inputSTR[:kaIdx]
                        #tmpRefDICT = {"inputSTR":[inputSTR], "utterance": [], "ka_index":[], "utter_index":[0], "COMP":[], "and":[], "REL":[]}
                        tmpLokiResultLIST = tmpAskLoki(tmpInputSTR)
                        if all(tmpLokiDICT["results"] == [] for tmpLokiDICT in tmpLokiResultLIST):
                            if Cord:
                                resultDICT["and"].append({INTENT_NAME: True})
                                resultDICT["utterance"].append(utterance)
                        else:
                            pass
                #</ka_capture_test>


    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("do -PV .IRR also he .GEN ka PC. more .AV -IRR still OBL those", "do -PV .IRR also he .GEN ka PC. more .AV -IRR still OBL those", [], {}, {})
    pprint(resultDICT)