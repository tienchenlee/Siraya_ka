#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki 4.0 Template For Python3

    [URL] https://nlu.droidtown.co/Loki_EN/BulkAPI/

    Request:
        {
            "username": "your_username",
            "input_list": ["your_input_1", "your_input_2"],
            "loki_key": "your_loki_key",
            "filter_list": ["intent_filter_list"] # optional
        }

    Response:
        {
            "status": True,
            "msg": "Success!",
            "version": "v223",
            "result_list": [
                {
                    "status": True,
                    "msg": "Success!",
                    "results": [
                        {
                            "intent": "intentName",
                            "pattern": "matchPattern",
                            "utterance": "matchUtterance",
                            "argument": ["arg1", "arg2", ... "argN"]
                        },
                        ...
                    ]
                },
                {
                    "status": False,
                    "msg": "No matching intent."
                }
            ]
        }
"""

from copy import deepcopy
from glob import glob
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from pathlib import Path
from requests import codes
from requests import get
from requests import post
import math
import os
import re

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

PROJECT_NAME = "Siraya_ka"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_DICT = {
    "Account": import_from_path("{}_lib_Account".format(PROJECT_NAME), os.path.join(CWD_PATH, "Account.py")),
    "ChatbotMaker": import_from_path("{}_lib_ChatbotMaker".format(PROJECT_NAME), os.path.join(CWD_PATH, "ChatbotMaker.py")),
    "LLM": import_from_path("{}_lib_LLM".format(PROJECT_NAME), os.path.join(CWD_PATH, "LLM.py")),
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
INTENT_PATH = MODULE_DICT["Account"].INTENT_PATH
ACCOUNT_DICT = MODULE_DICT["Account"].ACCOUNT_DICT
ARTICUT = MODULE_DICT["Account"].ARTICUT
USER_DEFINED_FILE = MODULE_DICT["Account"].USER_DEFINED_FILE
COLOR_DICT = MODULE_DICT["ChatbotMaker"].COLOR_DICT
setColor = MODULE_DICT["ChatbotMaker"].setColor
callLLM = MODULE_DICT["LLM"].callLLM
getCosineSimilarityUtterance = MODULE_DICT["LLM"].getCosineSimilarityUtterance

lokiIntentDICT = {}
for modulePath in glob("{}/Loki_*.py".format(INTENT_PATH)):
    moduleNameSTR = Path(modulePath).stem[5:]
    lokiIntentDICT[moduleNameSTR] = import_from_path("{}_intent_{}".format(PROJECT_NAME, moduleNameSTR), modulePath)

# Filter descrption
# INTENT_FILTER = []        => All intents (Default)
# INTENT_FILTER = [intentN] => Only use intent of INTENT_FILTER
INTENT_FILTER = []
INPUT_LIMIT = 20


class LokiResult():
    status = False
    message = ""
    version = ""
    balance = -1
    lokiResultLIST = []

    def __init__(self, inputLIST, filterLIST):
        self.status = False
        self.message = ""
        self.version = ""
        self.balance = -1
        self.lokiResultLIST = []
        # Default: INTENT_FILTER
        if filterLIST == []:
            filterLIST = INTENT_FILTER

        try:
            url = "{}/Loki_EN/BulkAPI/".format(ACCOUNT_DICT["server"])
            result = post(url, json={
                "username": ACCOUNT_DICT["username"],
                "input_list": inputLIST,
                "loki_key": ACCOUNT_DICT["loki_key"],
                "filter_list": filterLIST
            })

            if result.status_code == codes.ok:
                result = result.json()
                self.status = result["status"]
                self.message = result["msg"]
                if result["status"]:
                    self.version = result["version"]
                    if "word_count_balance" in result:
                        self.balance = result["word_count_balance"]
                    self.lokiResultLIST = result["result_list"]
            else:
                self.message = "{} Connection failed.".format(result.status_code)
        except Exception as e:
            self.message = str(e)

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message

    def getVersion(self):
        return self.version

    def getBalance(self):
        return self.balance

    def getLokiStatus(self, index):
        rst = False
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["status"]
        return rst

    def getLokiMessage(self, index):
        rst = ""
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["msg"]
        return rst

    def getLokiLen(self, index):
        rst = 0
        if index < len(self.lokiResultLIST):
            if self.lokiResultLIST[index]["status"]:
                rst = len(self.lokiResultLIST[index]["results"])
        return rst

    def getLokiResult(self, index, resultIndex):
        lokiResultDICT = None
        if resultIndex < self.getLokiLen(index):
            lokiResultDICT = self.lokiResultLIST[index]["results"][resultIndex]
        return lokiResultDICT

    def getIntent(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["intent"]
        return rst

    def getPattern(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["pattern"]
        return rst

    def getUtterance(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["utterance"]
        return rst

    def getArgs(self, index, resultIndex):
        rst = []
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["argument"]
        return rst

def runLoki(inputLIST, filterLIST=[], refDICT={}, toolkitDICT={}):
    resultDICT = deepcopy(refDICT)
    lokiRst = LokiResult(inputLIST, filterLIST)
    if lokiRst.getStatus():
        for index, key in enumerate(inputLIST):
            lokiResultDICT = {k: [] for k in refDICT}
            for resultIndex in range(0, lokiRst.getLokiLen(index)):
                if lokiRst.getIntent(index, resultIndex) in lokiIntentDICT:
                    lokiResultDICT = lokiIntentDICT[lokiRst.getIntent(index, resultIndex)].getResult(
                        key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex),
                        lokiResultDICT, refDICT, pattern=lokiRst.getPattern(index, resultIndex), toolkitDICT=toolkitDICT)

            # save lokiResultDICT to resultDICT
            for k in lokiResultDICT:
                if k not in resultDICT:
                    resultDICT[k] = []
                if type(resultDICT[k]) != list:
                    resultDICT[k] = [resultDICT[k]] if resultDICT[k] else []
                if type(lokiResultDICT[k]) == list:
                    resultDICT[k].extend(lokiResultDICT[k])
                else:
                    resultDICT[k].append(lokiResultDICT[k])
    else:
        resultDICT["msg"] = lokiRst.getMessage()
    return resultDICT

def execLoki(content, filterLIST=[], splitLIST=[], refDICT={}, toolkitDICT={}):
    resultDICT = deepcopy(refDICT)
    if resultDICT is None:
        resultDICT = {}

    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    if contentLIST:
        if splitLIST:
            # split by splitLIST
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            inputLIST = []
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # remove empty
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # don't split
            inputLIST = contentLIST

        # batch with limitation of INPUT_LIMIT
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST=filterLIST, refDICT=resultDICT, toolkitDICT=toolkitDICT)
            if "msg" in resultDICT:
                break

    if ACCOUNT_DICT["chatbot_mode"]:
        if "response" not in resultDICT:
            resultDICT["response"] = []
        if "source" not in resultDICT:
            resultDICT["source"] = []

        for i, content in enumerate(contentLIST):
            if i < len(resultDICT["response"]) and resultDICT["response"][i]:
                responseSTR = resultDICT["response"][i]
                sourceSTR = "reply"
            else:
                responseSTR = ""
                if ACCOUNT_DICT["utterance_count"]:
                    scoreDICT = getCosineSimilarityUtterance(content, ACCOUNT_DICT["utterance_count"])
                    if scoreDICT["utterance"] and scoreDICT["score"] >= ACCOUNT_DICT["utterance_threshold"]:
                        responseSTR = lokiIntentDICT[scoreDICT["intent"]].getReply(scoreDICT["utterance"], [])
                        if responseSTR:
                            responseSTR = "Do you mean「{}」?\n{}".format(scoreDICT["utterance"], responseSTR)
                            sourceSTR = "SIM_reply"

                if not responseSTR:
                    responseSTR, sourceSTR = callLLM(content)

            if i < len(resultDICT["response"]):
                resultDICT["response"][i] = responseSTR
            else:
                resultDICT["response"].append(responseSTR)

            if i < len(resultDICT["source"]):
                resultDICT["source"][i] = sourceSTR
            else:
                resultDICT["source"].append(sourceSTR)

    return resultDICT

def cosSimilarLoki(content, splitLIST=[], featureLIST=[]):
    resultDICT = {}

    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    if not featureLIST:
        featureLIST = ACCOUNT_DICT["utterance_feature"]

    if contentLIST:
        inputLIST = []
        if splitLIST:
            # split by splitLIST
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # remove empty
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # don't split
            inputLIST = contentLIST

        for inputSTR in inputLIST:
            inputSTR = inputSTR.strip()
            scoreDICT = getCosineSimilarityUtterance(inputSTR, ACCOUNT_DICT["utterance_count"])
            if scoreDICT["intent"] and scoreDICT["score"] >= ACCOUNT_DICT["utterance_threshold"]:
                if scoreDICT["intent"] not in resultDICT:
                    resultDICT[scoreDICT["intent"]] = {}
                resultDICT[scoreDICT["intent"]][inputSTR] = {
                    "utterance": scoreDICT["utterance"],
                    "score": scoreDICT["score"]
                }

    return resultDICT

def testLoki(inputLIST, filterLIST):
    for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
        resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)

    return resultDICT

def testIntent():
    from pprint import pprint

    # COMP_use
    print("[TEST] COMP_use")
    inputLIST = ['so .AV .IRR .PFV ka','good .AV -IRR you .SG -OBL ka','PAST- hear -PV you .PL .GEN ka','this NOM will OBL father ka PAST- send.forth .AV me -OBL ka','PAST- see -LV we .EXCL .GEN you .SG -OBL ka hungry .AV ka thirsty .AV ka be.stranger .AV']
    pprint(testLoki(inputLIST, ['COMP_use']))
    print("")

    # REL_use
    print("[TEST] REL_use")
    inputLIST = ['lord ka DET son GEN David','NOM swear .AV -IRR -PFV PC- gold .AV ka','whatever ka go.into.mouth .AV ka go.into.belly .AV','OBL PART plants ka not PAST-plant.PV OBL father my REL LOC heaven']
    pprint(testLoki(inputLIST, ['REL_use']))
    print("")

    # and_use
    print("[TEST] and_use")
    inputLIST = ['eat .AV ka drink .AV','six ten NOM another ka three ten NOM some FOC','take -PV .IRR NOM one ka leave.alone -PV .IRR NOM one','speak .AV NOM dumb .AV ka well .AV NOM maimed .AV ka walk .AV NOM lame .AV ka see .AV NOM blind .AV']
    pprint(testLoki(inputLIST, ['and_use']))
    print("")


def COMM_TEST(inputSTR):
    if not inputSTR and "utterance_count" in ACCOUNT_DICT and ACCOUNT_DICT["utterance_count"]:
        intentSTR = list(ACCOUNT_DICT["utterance_count"])[0]
        inputSTR = list(ACCOUNT_DICT["utterance_count"][intentSTR])[0]
        inputSTR = re.sub("[\[\]]", "", inputSTR)

    print(setColor("========== COMM_TEST Start ==========", COLOR_DICT["PURPLE"]))

    # Input
    print("\nInput: {}".format(inputSTR))

    # Server
    print(setColor("\nTest Server", COLOR_DICT["CYAN"]))
    print("Server: {}".format(ACCOUNT_DICT["server"]))
    try:
        r = get(ACCOUNT_DICT["server"])
        if r.status_code == 200:
            print("[Status] {}".format(setColor("Connection test successful.", COLOR_DICT["GREEN"])))
        else:
            print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
            print("[Hint] {}".format(setColor("Please check if the server field in account.info is a valid URL.", COLOR_DICT["YELLOW"])))
            return
    except:
        print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
        print("[Hint] {}".format(setColor("Please check if the server field in account.info is a valid URL.", COLOR_DICT["YELLOW"])))
        return

    # Articut
    print(setColor("\nTest Articut", COLOR_DICT["CYAN"]))
    print("Username: {}".format(ACCOUNT_DICT["username"]))
    print("API Key: {}".format(ACCOUNT_DICT["api_key"]))
    atkResult = ARTICUT.parse(inputSTR, userDefinedDictFILE=USER_DEFINED_FILE)
    if atkResult["status"]:
        print("[Status] {}".format(setColor("Connection test successful.", COLOR_DICT["GREEN"])))
    else:
        print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
        if atkResult["msg"] == "Insufficient quota.":
            print("[Hint] {}".format(setColor("Insufficient quota of Articut. Please purchase Articut from the official website.", COLOR_DICT["YELLOW"])))
        else:
            print("[Hint] {}".format(setColor("Please check if the username and api_key fields in account.info are correct.", COLOR_DICT["YELLOW"])))

    # Loki
    print(setColor("\nTest Loki", COLOR_DICT["CYAN"]))
    print("Username: {}".format(ACCOUNT_DICT["username"]))
    print("Loki Key: {}".format(ACCOUNT_DICT["loki_key"]))
    lokiResult = LokiResult([inputSTR], [])
    if lokiResult.getStatus():
        print("[Status] {}".format(setColor("Connection test successful.", COLOR_DICT["GREEN"])))
    else:
        print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
        if lokiResult.getMessage() == "Insufficient quota.":
            print("[Hint] {}".format(setColor("Insufficient quota of Loki. Please purchase Loki from the official website.", COLOR_DICT["YELLOW"])))
        else:
            print("[Hint] {}".format(setColor("Please check if the username and api_key fields in account.info are correct.", COLOR_DICT["YELLOW"])))
            print("[Hint] {}".format(setColor("Please check if the Loki model has been deployed.", COLOR_DICT["YELLOW"])))

    print(setColor("\n========== COMM_TEST End ==========", COLOR_DICT["PURPLE"]))


if __name__ == "__main__":
    from pprint import pprint

    # Test all intents
    #testIntent()

    # Test sentence
    contentSTR = ""
    if not contentSTR and "utterance_count" in ACCOUNT_DICT and ACCOUNT_DICT["utterance_count"]:
        intentSTR = list(ACCOUNT_DICT["utterance_count"])[0]
        contentSTR = list(ACCOUNT_DICT["utterance_count"][intentSTR])[0]
        contentSTR = re.sub("[\[\]]", "", contentSTR)

    filterLIST = []
    splitLIST = ["!", ",", ".", "\n", "\u3000", ";"]
    # set references
    refDICT = { # value is a list
        #"key": []
    }

    # Run Loki
    resultDICT = execLoki(contentSTR, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    pprint(resultDICT)