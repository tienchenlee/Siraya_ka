#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from time import sleep

#from Loki_AND.Coordinator.main import askLoki as askLokiAND
from Loki_REL.Relativizer.main import askLoki as askLokiREL

def main():
    """"""
    return None


if __name__ == "__main__":
    andLIST = []
    relLIST = []
    compLIST = []
    attempts = 0
    success = False

    #with open("evaluation_data/kaLIST.json", encoding="utf-8") as kaFILE:
        #mixedLIST = json.load(kaFILE)

    devMixedLIST = ["PAST- give .AV NOM DET Moses you .PL -OBL OBL bread ka from-heaven .AV"]


    refDICT = {"inputSTR":[], "ka_index":[], "utter_index":[], "COMP":[], "and":[], "REL":[]}
    for ka_S in devMixedLIST:
        attempts = 0
        success = False

        while attempts < 3 and not success:
            relResult = askLokiREL(ka_S, filterLIST=["V3_AV"], refDICT=refDICT)
            sleep(0.8)

            if "msg" in relResult.keys():
                attempts += 1
                print(f"第 {attempts} 次嘗試，{relResult['msg']}: {relResult}")
                sleep(5)
            else:
                success = True
                print(relResult)

        #andResult = askLokiAND(ka_S, refDICT=refDICT)
        #relResult = askLokiREL(ka_S, refDICT=refDICT)


    print("AND:")
    #print(andResult)

    print("===")
    print(relResult)