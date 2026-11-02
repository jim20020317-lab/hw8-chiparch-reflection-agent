# 🧠 ChipArch Red-Team Reflection Agent —— AI 晶片硬體架構紅隊反思優化系統

國立中央大學 生成式 AI 實作課程 第八週作業：用程式做一個簡單的 AI Agent
- **學校**：中央大學（中大）
- **學號**：114521045
- **系級**：電子組碩二（電子碩二）
- **姓名**：楊荏鈞
- **選用 Agent 類型**：**Reflection（自我反思代理）**
- **專題主題**：AI 晶片與小晶片 (Chiplet) 硬體架構紅隊反思優化系統

---

## 🌟 專案核心任務與設計理念
在高效能 AI 晶片與多小晶片（Multi-Chiplet / DCIM）架構設計中，初級工程師常提出理論算力很高、但忽略電路物理限制（SRAM Subarray RC 延遲、Wordline/Bitline 長度限制、NoC 頻寬瓶頸、跨 Chiplet D2D 封裝功耗與熱熱點）的過度樂觀方案。

本專案參考老師【Demo07a】的 Reflection 架構，實作三階段協作反思系統：
1. **Designer Agent（初級架構師）**：提出初步 PE 陣列與資料流提案。
2. **Red-Team Reviewer Agent（資深首席架構師兼紅隊審查員）**：直擊三大底層物理與通訊致命破綻，給出嚴厲批判與工程改善指標。
3. **Refiner Agent（反思優化架構師）**：進行深度自我反思（Self-Reflection），誠實檢討盲點並提出落地工程防護方案與改善量化對比表。
4. **Agent 行為動態調節（9~10 分進階設計）**：支援使用者切換審查焦點（標準 PPA、極致低能耗、NoC 頻寬防死鎖），動態改變審查員批判權重。

---

## 📂 專案架構
```
hw8-chiparch-reflection-agent/
├── HW8_AI_Agent_Reflection_晶片架構紅隊審查.ipynb   # Colab 筆記本（含重點 MarkDown 註記）
├── app.py                                         # 本機與 Colab 共通 Gradio WebApp
├── gradio_agent_screenshot.png                    # Gradio 實機對話成果截圖
├── test_reflection_result.txt                     # 完整三階段對話文本記錄
└── 作業繳交內容說明.md                             # 完整的作業繳交說明
```
