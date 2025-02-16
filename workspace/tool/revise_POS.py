#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

NounPAT = re.compile(r"(?<=ENTITY_)nouny|nounHead|oov")
VerbPAT = re.compile(r"(PAST-)?<ACTION_verb>(-PV|-IV|.AV(.IRR)?|-LV(.IRR)?)?")


def revise_POS(contentLIST) -> list:    #contentLIST 是一個 jsonFILE 的內容
    for resultDICT in contentLIST:
        glossLIST = resultDICT["g"].split(" ")
        posLIST = resultDICT["p"].split(" ")
        for i in range(len(posLIST)):
            posLIST[i] = re.sub(NounPAT, "noun", posLIST[i])
            if glossLIST[i] == "whatever":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_pronoun>")
            if glossLIST[i] == "other":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_pronoun>")
            if glossLIST[i] == "another":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_pronoun>")               
            if glossLIST[i] == "fish":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_noun>")               
            if glossLIST[i] == "reed":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_noun>")            
            if glossLIST[i] == "chief":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_noun>")            
            if glossLIST[i] == "silver":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_noun>")            
            if glossLIST[i] == "weed":
                posLIST[i] = posLIST[i].replace("<MODIFIER>", "<ENTITY_noun>")                
            if glossLIST[i] == "beginning":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "mourning":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "work":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "seed":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "light":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "wind":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "grave":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "guard":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "drink":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<ENTITY_noun>")
            if glossLIST[i] == "instruct":
                posLIST[i] = posLIST[i].replace("<ENTITY_noun>", "<ACTION_verb>")
            if glossLIST[i] == "nod":
                posLIST[i] = posLIST[i].replace("<ENTITY_noun>", "<ACTION_verb>")
            if glossLIST[i] == "testify":
                posLIST[i] = posLIST[i].replace("<ENTITY_noun>", "<ACTION_verb>")     
            if glossLIST[i] == "rejoice":
                posLIST[i] = posLIST[i].replace("<ENTITY_noun>", "<ACTION_verb>")
            if glossLIST[i] == "exceeding":
                posLIST[i] = posLIST[i].replace("<ACTION_verb>", "<MODIFIER>") 
            #if glossLIST[i] == "when":
                #posLIST[i] = posLIST[i].replace("<ENTITY_pronoun>", "<CLAUSE_WhenQ>")
            #if glossLIST[i] == "why":
                #posLIST[i] = posLIST[i].replace("<ENTITY_pronoun>", "<CLAUSE_WhyQ>")
            #if glossLIST[i] == "what":
                #posLIST[i] = posLIST[i].replace("<ENTITY_pronoun>", "<CLAUSE_WhatQ>")
            #if glossLIST[i] == "who":
                #posLIST[i] = posLIST[i].replace("<ENTITY_pronoun>", "<CLAUSE_WhoQ>")
            #if glossLIST[i] == "where":
                #posLIST[i] = posLIST[i].replace("<ENTITY_pronoun>", "<CLAUSE_WhereQ>")
            #if glossLIST[i] == "how":
                #posLIST[i] = posLIST[i].replace("<ENTITY_pronoun>", "<CLAUSE_HowQ>")                   
            # put the verb back in resultDICT["p"]，給 ka_in_Matthew_arg 和 ka_in_John_arg 使用
            if re.search(VerbPAT, posLIST[i]):
                posLIST[i] = glossLIST[i]
        resultDICT["p"] = " ".join(posLIST)        
    return contentLIST
  


if __name__ == "__main__":
    #folder_path = ["./ka_in_Matthew", "ka_in_John"]
    folder_path = ["./ka_in_Matthew_arg", "ka_in_John_arg"]    
    for folder in folder_path:
        jsonFILES = [file for file in os.listdir(folder) if file.endswith(".json")]        
        for jsonFILE in jsonFILES:
            file_path = os.path.join(folder, jsonFILE)                
            with open(file_path, "r", encoding="utf-8") as f:
                contentLIST = json.load(f)
                
            revise_contentLIST = revise_POS(contentLIST)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(revise_contentLIST, f, ensure_ascii=False, indent=4)              