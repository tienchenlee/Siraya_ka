# Table of Contents

1. 提示詞測試 Gemini
2. 計算覆蓋率

- - - 

# 1. 提示詞測試 Gemini
1. 使用 `LLM_testing/askLLM.py` 對 Gemini 進行測試。  
2. 調整 phase (1 / 2 / 3)，選擇此次的測試階段。  
4. 結果產生至 `LLM_testing/results/`。

# 2. 計算覆蓋率
1. 使用 `LLM_testing/evaluation.py` 。
2. 調整 PHASE (1 / 2 / 3)，選擇此次的測試階段。
3. 產生「正解」及「預測」檔案至 `LLM_testing/answer/`, `LLM_testing/prediction/`。
4. 執行程式會顯示此階段之 Recall, Precision, Accuracy。
