#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Loki_and.Coordinator.main import askLoki
#from preLokiTool import udFilter

def main(inputSTR, filterLIST, utterIdx):
    """"""
    refDICT = {"inputSTR": [inputSTR],
               "and": [],
               "ka_index": [],
               "utter_index": [utterIdx]}


    resultDICT = askLoki(inputSTR, filterLIST=filterLIST, refDICT=refDICT)
    return resultDICT

if __name__ == "__main__":
    #<單筆測試>
    inputSTR ="when ka see-LV they.GEN NOM star then PAST-joyful.AV NOM they OBL joy ka exceeding.AV great.AV"

    filterSTR = udFilter(inputSTR)
    resultDICT = main(filterSTR, 0)  # 預設句子 index = 0
    print(resultDICT)
    #</單筆測試>