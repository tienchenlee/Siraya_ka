# Table of Contents

1. 部署模型
2. 測試 / 評估模型
3. 計算覆蓋率

- - - 

# 1. 部署模型  
## 1.1 Loki pattern 調整
 - 調整 utterance，部署該 intent。(不需做 1.2)
 - 新增 utterance，部署該 intent，將該句 utterance 加進 intent.py。(不需做 1.2)
 - 調整 ud/var，需要部署所有 intent，並將 ud 下載，更新到 `workspace/Loki_and/Coordinator/intent`, `workspace/Loki_REL/Relativizer/intent`, `workspace/Loki_COMP/Complementizer/intent`。
 - 調整 var 時，如果 var 有使用 trie 加速，利用 `workspace/generalTool/regex_speedup_tools.py` 在相對應的 var 增減內容，並執行程式碼，拿到 trie 結果，更新至 Loki 介面。

## 1.2 三個專案同步更新 ud / var
ud/var 會是三個 Project 共用，一次調整好某一個 Project 的 ud/var 後，要將三個專案同步更新。  

#### 1.2.1 檔案更新 
下載 ud/var，更新到 `data/userDefined.json` 和 `data/VARIABLE.json` 。  
#### 1.2.2 執行 ud / var 更新工具
使用 `workspace/generalTool/envBuilder.py` ，調整更新之專案 (PROJECT) 及設定模型之版本 (mode) 為線上或 docker。
#### 1.2.3 Loki 介面調整
在 Loki 介面調整 ka 的捕獲組，並部署所有 intent。  

- Complementizer 專案的 CP 中要抓 (ka)，RC 不抓 ka
- Relativizer 專案的 RC 中要抓 (ka)，CP 不抓 ka
- Coordinator 則是 CP 和 RC 都不抓 ka。

## 1.3 github 更新
將本機更動 git push。
## 1.4 atm 更新
下載 Loki_bk 將 atm 更新到遠端主機，git pull 所有更動後，確認 Loki Project 的 account.info 中 server 是遠端主機，即部署完成。

# 2. 測試 / 評估模型
1. 使用 `workspace/ka_identifier.py` 進行模型測試或評估。  
2. 調整 MODE (test / evaluation)，選擇此次為「測試」或「評估」階段。  
3. 調整 KA (REL / COMP / and)，選擇此次檢驗的 ka 句法功能。
4. 結果產生至 `data/results/`

# 3. 計算覆蓋率
1. 使用 `workspace/generalTool/evaluation.py` 。
2. 調整 PHASE (test / eval)，選擇此次為「測試」或「評估」階段。
3. 產生「正解」及「預測」檔案至 `data/answer/`, `data/prediction/`。
4. 執行程式會顯示三個獨立句型模型 (Relativizer, Complementizer, Coordinator) 之 Recall, Precision, Accuracy, Coverage。
