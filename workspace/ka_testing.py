#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json

from Loki_AND.Coordinator.main import askLoki as askLokiAND
from Loki_REL.Relativizer.main import askLoki as askLokiREL

def main():
    """"""
    return None


if __name__ == "__main__":
    andLIST = []
    relLIST = []
    compLIST = []

    with open("evaluation_data/kaLIST.json", encoding="utf-8") as kaFILE:
        mixedLIST = json.load(kaFILE)

    devMixedLIST = ["yet woe you .PL ka scribe OBL Pharisees also ka different -PV OBL heart OBL word"]


    refDICT = {"inputSTR":[], "ka_index":[], "utter_index":[], "COMP":[], "and":[], "REL":[]}
    for ka_S in devMixedLIST:
        #andResult = askLokiAND(ka_S, refDICT=refDICT)
        relResult = askLokiREL(ka_S, refDICT=refDICT)


    print("AND:")
    #print(andResult)

    print("===")
    print(relResult)