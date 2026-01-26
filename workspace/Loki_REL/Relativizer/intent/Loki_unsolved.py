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
if G_mainPath.name == "ka_testing.py":
    try:
        from Loki_REL.Relativizer.intent.kaCaptureTool import kaCapture
    except:
        from .Loki_REL.Relativizer.intent.kaCaptureTool import kaCapture
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
    if utterance == "Jerusalem Jerusalem, ka kill you .SG .NOM OBL prophet":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PART write.on.surface also ka inscription":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "Truly .AV say .PV I .GEN you .PL .NOM FOC not you .SG .NOM come.out .AV -IRR there LOC time until that ka PC. already you .SG .NOM give.finish .AV -IRR OBL most .AV ka small .AV OBL price ka small.coin":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "for truly .AV say .PV I .GEN you .PL .NOM FOC ka many .AV OBL PART prophet OBL PART righteous .AV also NOM PAST- want .AV see .AV ka see -LV you .PL .GEN yet not they .GEN PAST- see -LV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "from.where .AV ka have-herb .AV ka not good .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "ka most .AV small .AV NOM it OBL all OBL seed":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "when ka PAST- move.on .AV NOM he from .AV there PAST- look -LV he .GEN NOM two OBL be.brothers .AV ka other NOM DET Jakobus REL-child GEN Zebedeus DET John also ka brother his be.together .AV DET father their ka DET Zebedee LOC ship mend .AV OBL dragnet their ka PAST- call .PV he .GEN NOM he":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "yet they ka righteous .AV LOC life ka always .AV be.lasting .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "you .PL ka foolish .AV ka blind .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "ka see -LV .IRR PAST- have.man .AV ka PAST- wither -PV OBL hand ka PAST- ask .AV NOM they him -OBL say .AV allow -PV Q heal .AV LOC day OBL sabbath":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "all-also OBL city OBL house or ka divide.city .AV divide.house .AV them -OBL one.self .AV not remain .AV -IRR NOM it however":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "yet revile -LV curse .AV ka against .AV OBL spirit not forgive -LV .IRR OBL man":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "weed or ka shake -PV OBL wind":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "human or ka wear .AV -PFV OBL soft .AV ka cloth":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "father.LV our .EXC ka at.far.above you.SG.NOM OBL heaven":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "forgive .AV -IRR OBL own.debt -PV you .SG .GEN us .EXC -OBL same .AV ka forgive .AV we .EXC .NOM NOM we .EXCL OBL own.debt -PV -we .EXCL .GEN":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "DET Barabbas Q DET Jesus Q ka be.nicknamed DET Christ":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PAST- mock .AV him -OBL say .AV Greetings ruler ka chief OBL Jews":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "ka PAST- force -PV they .GEN cause.carry .AV OBL cross his":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "yet only him -OBL ka obey .AV OBL will GEN father my ka at-far.above OBL heaven":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "DET James ka son GEN Zebedeus DET John also ka brother his":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "DET Thomas DET Matthew also ka PART tax.collector":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "DET James ka son GEN Alpheus DET Lebbaeus also ka cause.nicknamed -LV Thaddaeus":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "DET Simon Canaanite DET Judas Iscariot also ka PAST- PC. hand.over .AV betray .AV him -OBL":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "FOC PAST- answer .AV NOM DET Jesus say .AV them -OBL Truly .AV say .PV I .GEN you .PL .NOM FOC if have .AV you .PL .NOM OBL faith FOC LOC not have.doubt -PV OBL heart would you .PL .NOM not only do .AV -IRR ka PAST- do .PV OBL fig":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "only ka belong man FOC":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("you .PL ka foolish .AV ka blind .AV", "you .PL ka foolish .AV ka blind .AV", [], {}, {})
    pprint(resultDICT)