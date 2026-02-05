#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Loki_REL.Relativizer.main import askLoki
#from preLokiTool import udFilter

def main(inputSTR, filterLIST, utterIdx):
    """"""
    refDICT = {"inputSTR": [inputSTR],
               "REL": [],
               "ka_index": [],
               "utter_index": [utterIdx]}


    resultDICT = askLoki(inputSTR, filterLIST=filterLIST, refDICT=refDICT)
    return resultDICT

if __name__ == "__main__":
    #<單筆測試>
    inputSTR ="PAST- say .AV NOM they him -OBL why ka PAST- instruct -PV GEN Moses ka give -IV .IRR NOM scripture OBL divorcement ka cause.leave -PV .IRR NOM she ka wife OBL man"

    #filterSTR = udFilter(inputSTR)
    resultDICT = main(inputSTR, 0)  # 預設句子 index = 0
    print(resultDICT)
    #</單筆測試>