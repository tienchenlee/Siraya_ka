#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
from Loki_COMP.COMP_identifier import main as askCOMP
from Loki_and.and_identifier import main as askAnd
from Loki_REL.REL_identifier import main as askREL
from preLokiTool import udFilter
from time import sleep

def main(inputSTR, utterIdx):
    """"""
    askLokiDICT = {
        "COMP": askCOMP,
        "and": askAnd,
        "REL": askREL
    }

    #stop = False

    for keySTR, askLoki in askLokiDICT.items():
        #if stop:
            #break

        attempts = 0
        success = False

        while attempts < 3 and not success:
            lokiResultDICT = askLoki(inputSTR, utterIdx)
            sleep(0.5)

            if "status" in lokiResultDICT.keys():   # Server Error 會回傳 status
                attempts += 1
                logging.warning(f"第 {attempts} 次嘗試: {inputSTR}")
            else:
                success = True

                if lokiResultDICT[keySTR] == []:
                    pass
                else:
                    #stop = True
                    #return lokiResultDICT
                    print(lokiResultDICT)
        if not success:
            logging.error(f"連續 3 次嘗試失敗，跳過此函數: {keySTR}")

if __name__ == "__main__":
    #<單筆測試>
    inputSTR ="when ka see-LV they.GEN NOM star then PAST-joyful.AV NOM they OBL joy ka exceeding.AV great.AV"

    filterSTR = udFilter(inputSTR)
    resultDICT = main(filterSTR, 0)  # 預設句子 index = 0
    print()
    print(resultDICT)
    #</單筆測試>

