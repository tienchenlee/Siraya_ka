#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for unsolved

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
import sys

G_mainPath = Path(sys.argv[0]).resolve()
if G_mainPath.name in ["ka_testing.py", "ka_identifier.py"]:
    try:
        from Loki_and.Coordinator.intent.kaCaptureTool import kaCapture
    except:
        from .Loki_and.Coordinator.intent.kaCaptureTool import kaCapture
else:
    try:
        from kaCaptureTool import kaCapture
    except:
        from .kaCaptureTool import kaCapture

INTENT_NAME = "unsolved"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))
G_notVerbPAT = r"(?<=<UserDefined>)([a-zA-Z\-\.]{1,19})$"

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
    if utterance == "Jerusalem Jerusalem, ka kill you .SG .NOM OBL prophet ka attack .AV you .SG .NOM OBL PART stone OBL send.forth -PV cause.come .AV you .SG -OBL":
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

    if utterance == "LOC last FOC PAST- come .AV NOM two OBL witness ka false .AV ka PAST- say .AV he this NOM PAST- say .AV PC. able -PV I .GEN destroy NOM temple OBL worship -PV OBL God ka PC. return .AV build .AV OBL it LOC three OBL day":
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

    if utterance == "PAST- PC. self .AV you .SG .NOM gird .AV you .SG OBL ka PAST- walk .AV LOC any.place ka want -PV you .SG .GEN":
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

    if utterance == "all.things ka ask -LV .IRR you .PL .GEN DET father -OBL LOC name my ka give .AV -IRR OBL it you .PL -OBL":
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

    if utterance == "exceeding .AV angry .AV NOM he ka when PAST- send.forth .AV PAST- kill .AV OBL all OBL boys ka LOC Bethlehem LOC all-also OBL borders its ka from.two .AV OBL year ka under .AV also PART obey -LV OBL time ka PAST- ask .AV OBL wise cause.see those":
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

    if utterance == "gardener or PAST- consider she .GEN ka PAST- say .AV NOM she him -OBL sir if PAST- take .AV you .SG .NOM him -OBL cause.away .AV tell -LV .IRR I .NOM PAST- place.where .AV you .SG .NOM him -OBL ka take -PV .IRR I .GEN NOM he":
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

    if utterance == "have .AV -also -I OBL sheep ka other ka not PART corral this":
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

    if utterance == "he ka PAST- sow .PV LOC stony.place ka mix .AV OBL dirt he NOM DET that ka hear .AV OBL word ka PC. quick .AV PC. joyful .AV OBL it accept .AV":
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

    if utterance == "not distant .AV them -OBL NOM land two or hundred OBL PART measurement OBL arm ka drag -PV they .GEN NOM net":
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

    if utterance == "one OBL man ka have-son .AV OBL two ka when come -LV he .GEN OBL first PAST- say .AV":
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

    if utterance == "ought ka fulfill -PV .IRR NOM this ka NEG not.willing -LV .IRR NOM that":
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

    if utterance == "when ka dark .AV -PFV LOC one OBL day that ka first .AV OBL crossing OBL sabbath when PAST- shut .PV NOM door LOC PAST- assemble -LV OBL disciple because OBL fear -LV they .GEN OBL Jew PAST- come .AV NOM DET Jesus stand .AV in.the.midst .AV ka PAST- say .AV them -OBL have-peace .AV you .PL -OBL":
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

    if utterance == "would you .PL .NOM not only do .AV -IRR ka PAST- do .PV OBL fig then if speak -LV .IRR you .PL .GEN OBL mountain this lift.up -PV .IRR ka cast -IV .IRR":
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

    if utterance == "you .SG .NOM ka DET Peter you .SG .NOM ka LOC top OBL Petra this PC. surely -LV .IRR I .GEN build .AV -IRR OBL church my ka not prevail .AV -IRR OBL it NOM door OBL hell":
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

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("have .AV -also -I OBL sheep ka other ka not PART corral this", "have .AV -also -I OBL sheep ka other ka not PART corral this", [], {}, {})
    pprint(resultDICT)