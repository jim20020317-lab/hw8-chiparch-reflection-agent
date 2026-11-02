import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import aisuite as ai
import gradio as gr

# 設定模型與服務提供商
provider = "groq"
model = "openai/gpt-oss-120b"

def reply(system, prompt):
    client = ai.Client()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=f"{provider}:{model}",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content

# 讀取預算好的範例推論結果（供展示預設值）
default_query = "我想設計一個支援 70B 大模型推論的 8-Chiplet 加速系統，第一版打算在所有 Chiplet 間採用全廣播（Broadcast）同步每一層的權重與中間特徵圖，以最大化計算並行度。"
default_v1 = ""
default_v2 = ""
default_v3 = ""
res_file = r"C:\生成式AI\HW8_Agent\test_reflection_result.txt"
if os.path.exists(res_file):
    with open(res_file, "r", encoding="utf-8") as f:
        c = f.read()
        p1 = c.find("=== 第一版初稿 ===")
        p2 = c.find("=== 紅隊反思審查 ===")
        p3 = c.find("=== 第二版優化方案 ===")
        if p1 != -1 and p2 != -1 and p3 != -1:
            default_v1 = c[p1+len("=== 第一版初稿 ==="):p2].strip()
            default_v2 = c[p2+len("=== 紅隊反思審查 ==="):p3].strip()
            default_v3 = c[p3+len("=== 第二版優化方案 ==="):].strip()

# 1. 設計師 Agent（Designer Agent）人設
system_designer = """你是一位熱情且富有創意的「AI 晶片硬體架構初級設計師」。
當使用者提出一個 AI 模型加速或晶片規格需求時，請提出初步的硬體架構方案（第一版初稿）。
內容需包含：
1. 核心架構概述（PE 陣列、記憶體配置、計算數據流）
2. 預期效能與吞吐量分析
3. 互連拓撲設計（NoC、D2D 或晶圓級匯流排）
請使用台灣習慣的繁體中文，行文自信樂觀，條理分明。"""

# 2. 紅隊審查員 Agent（Red-Team Reviewer Agent）人設
system_reviewer = """你是一位在頂尖半導體與 AI 晶片廠任職超過 20 年的「資深首席晶片架構師兼紅隊審查員（Red-Team Reviewer）」。
你的任務是針對初級設計師提交的硬體架構初稿進行極度嚴格、犀利且直擊痛點的【批判性反思與可行性審查】。
請著重於找出初稿中過度樂觀、忽略物理極限或隱藏死鎖的致命缺陷，並給出具體改進指標：
1. 【電路物理極限】：SRAM Subarray 的 RC 延遲、Wordline/Bitline 過長、讀寫衝突、記憶體牆。
2. 【互連與通信瓶頸】：NoC 拓撲是否會發生死鎖？跨 Chiplet 的 D2D 封裝頻寬是否過度承載？Partial Sum (psum) 是否跨晶片搬移造成巨額能耗？
3. 【散熱與面積 PPA 權衡】：封裝熱點（Thermal Hotspot）、晶片面積與良率折損。
請條列出 3 大關鍵致命漏洞，並給出明確、具工程可行性的修改指引。請用台灣繁體中文回應。"""

# 3. 反思改進 Agent（Refined Designer Agent）人設
system_refiner = """你是一位謙遜、注重工程嚴謹性並具備深度自我反思能力的「資深 AI 晶片架構修正師」。
你剛剛閱讀了資深紅隊審查員針對你第一版提案的嚴格批評與建議。
你的任務是進行深刻的【自我反思（Self-Reflection）】，徹底摒棄第一版中過度理想化的假設，並結合審查員的具體建議產出「第二版優化架構方案」。
輸出內容需包含：
1. 【反思自我檢討】：誠實點出第一版在底層物理與通訊網路上的盲點。
2. 【具體架構改進設計】：針對審查員指出的 3 大痛點提出具體解決方案（例如引入 Ping-Pong Relay Buffer、兩階段 BQP 映射、WS 權重原地保留）。
3. 【改進效益量化對比表】：以 Markdown 表格對比第一版與第二版在延遲、頻寬壓力、散熱風險與工程可行性上的具體改善。
請用台灣習慣的繁體中文回應。"""

def reflect_architecture(user_query, focus_mode="⚖️ 標準 PPA 平衡審查"):
    if not user_query.strip():
        return "請輸入有效的晶片設計需求！", "", ""

    # Step 1: Designer 生成第一版方案
    prompt_step1 = f"使用者晶片設計需求：{user_query}\n請針對此需求設計初步硬體加速架構方案。"
    first_version = reply(system_designer, prompt_step1)

    # Step 2: Reviewer 進行紅隊批判與反思檢驗
    prompt_step2 = f"審查重點取向：{focus_mode}\n\n這是初級設計師提出的架構提案：\n{first_version}\n\n請以資深架構師的紅隊視角進行嚴厲審查，點出三大致命破綻並給予具體工程改善要求。"
    suggestion = reply(system_reviewer, prompt_step2)

    # Step 3: Refiner 根據批判進行 Reflection，改進並產出第二版
    prompt_step3 = f"這是你的第一版提案：\n{first_version}\n\n這是紅隊審查員的犀利批評與改進建議：\n{suggestion}\n\n請進行深刻的【自我反思（Self-Reflection）】，修正錯誤假設，產出第二版優化架構方案與改善對照表。"
    second_version = reply(system_refiner, prompt_step3)

    return first_version, suggestion, second_version

# 預設晶片架構題目
example_cases = [
    [
        "我想設計一個支援 70B 大模型推論的 8-Chiplet 加速系統，第一版打算在所有 Chiplet 間採用全廣播（Broadcast）同步每一層的權重與中間特徵圖，以最大化計算並行度。",
        "⚖️ 標準 PPA 平衡審查"
    ],
    [
        "我想在 SRAM DCIM（數位存算一體）Macro 內部直接切跨層流水線（Interlayer Pipelining），以減少層間乒乓搬移並壓縮晶片面積。",
        "⚡ 極致低能耗與封裝散熱審查"
    ],
    [
        "設計一個晶圓級晶片（Wafer-Scale）的 CNN 加速架構，在數萬個 PE 間採用簡單的單向環狀拓撲傳遞 Partial Sum，不使用額外的 Relay Buffer。",
        "🚀 片上網路頻寬與防死鎖審查"
    ],
    [
        "多小晶片加速器中，直接採用貪婪演算法（Greedy Search）動態分配各層任務節點，以期達到最佳即時負載平衡。",
        "⚖️ 標準 PPA 平衡審查"
    ]
]

custom_css = """
body, .gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: #f8fafc;
}
.header-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.header-card h1 {
    color: #38bdf8;
    margin-bottom: 6px;
    font-size: 26px;
}
.header-card p {
    color: #cbd5e1;
    font-size: 14px;
    margin: 4px 0;
}
"""

with gr.Blocks(title="ChipArch Red-Team Reflection Agent", css=custom_css) as demo:
    gr.HTML("""
    <div class="header-card">
        <h1>🧠 ChipArch Red-Team Reflection Agent</h1>
        <p><strong>專題主題</strong>：AI 晶片與小晶片 (Chiplet) 設計提案之自我反思優化系統（Reflection Agent 實作）</p>
        <p><strong>學生資訊</strong>：中央大學 電子組碩二 114521045 楊荏鈞 ｜ <strong>課程</strong>：生成式 AI 實作作業（AI Agent）</p>
        <p style="font-size: 13px; color: #93c5fd; margin-top: 8px;">
            🔄 Agent 運作機制：【初級架構師提案】➔【資深首席架構師紅隊批判反思】➔【反思優化與工程落地版方案】
        </p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=8):
            user_input = gr.Textbox(
                value=default_query,
                label="💡 請輸入您的 AI 晶片或小晶片硬體架構構想：",
                placeholder="例如：我想設計一個 8-Chiplet 系統，第一版打算在所有晶片間全廣播權重以最大化並行度...",
                lines=3
            )
        with gr.Column(scale=4):
            focus_mode = gr.Radio(
                choices=["⚖️ 標準 PPA 平衡審查", "⚡ 極致低能耗與封裝散熱審查", "🚀 片上網路頻寬與防死鎖審查"],
                value="⚖️ 標準 PPA 平衡審查",
                label="🎯 紅隊反思審查焦點（Agent 行為調整）："
            )
            submit_btn = gr.Button("🚀 啟動 Reflection Agent 反思推論", variant="primary", size="lg")

    gr.Markdown("### 🔍 點擊以下推薦晶片架構提案進行快速測試：")
    gr.Examples(examples=example_cases, inputs=[user_input, focus_mode])

    gr.Markdown("---")
    gr.Markdown("## 🔄 Reflection 三階段推論進程展示")

    with gr.Row():
        out1 = gr.Textbox(
            value=default_v1,
            label="💡 [階段一] Designer Agent 初版提案（未經反思的直覺構想）",
            lines=16,
            show_copy_button=True
        )
        out2 = gr.Textbox(
            value=default_v2,
            label="🚨 [階段二] Red-Team Reviewer 批判審查（直擊物理/時序/頻寬致命缺陷）",
            lines=16,
            show_copy_button=True
        )
        out3 = gr.Textbox(
            value=default_v3,
            label="✨ [階段三] Refiner Agent 反思優化成果（自我反思檢討＋具體工程修正＋改善對比表）",
            lines=16,
            show_copy_button=True
        )

    submit_btn.click(
        reflect_architecture,
        inputs=[user_input, focus_mode],
        outputs=[out1, out2, out3]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
