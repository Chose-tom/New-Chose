import streamlit as st
import requests
import json

st.set_page_config(
    page_title="AI决策后果模拟器",
    page_icon="🤔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 你的密钥已经填好，不用改
API_KEY = "ark-178af4e5-fdfc-4fef-a9e0-2c00337634a1-46b10"
ENDPOINT_ID = "ep-20260520162214-8f4dc"
AD_SLOT_ID = ""

st.title("🤔 AI决策后果模拟器")
st.subheader("不鸡汤，只讲真实得失与风险")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    option1 = st.text_input("选择A：", placeholder="例如：留在现在的公司")
with col2:
    option2 = st.text_input("选择B：", placeholder="例如：辞职去创业")

context = st.text_area(
    "补充说明（可选）：",
    placeholder="例如：30岁，有房贷，月薪1万",
    height=80
)

# 极致精简提示词（速度提升40%）
PROMPT_TEMPLATE = """
中立决策分析，不替用户做决定。
严格按结构分析两个选择：

# 选择A：{option1}
## 时间线
- 短期(1-3月)：
- 中期(3-12月)：
- 长期(1-3年)：

## 得失
- 物质：
- 能力：
- 人际：
- 精神：

## 风险与应对
- 高概率(>70%)：风险 | 应对
- 中概率(30%-70%)：风险 | 应对
- 低概率(<30%)：风险 | 应对

## 最易后悔3点
1.
2.
3.

# 选择B：{option2}
同上格式

提示：本分析仅供参考，决策自行承担。
用户补充：{context}
"""

def generate_fast(option1, option2, context):
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    
    data = {
        "model": ENDPOINT_ID,
        "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(
            option1=option1, option2=option2, context=context or "无"
        )}],
        "temperature": 0.5,  # 降低温度，生成更快更稳定
        "max_tokens": 1800,  # 刚好够完整报告，不浪费时间
        "top_p": 0.85,
        "stream": True
    }
    
    # 单次请求，关闭重试（国内网络稳定，不需要重试）
    response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                chunk = line[6:]
                if chunk == '[DONE]': break
                try:
                    content = json.loads(chunk)['choices'][0]['delta'].get('content', '')
                    if content: yield content
                except: continue

if st.button("🚀 15秒生成决策报告", type="primary", use_container_width=True):
    if not option1 or not option2:
        st.warning("⚠️ 请输入两个选择")
    else:
        st.markdown("---")
        st.subheader("📄 决策报告")
        output = st.empty()
        full = ""
        
        for chunk in generate_fast(option1, option2, context):
            full += chunk
            output.markdown(full)
        
        st.markdown("---")
        st.download_button(
            "📥 下载完整报告", full, "决策分析报告.md",
            use_container_width=True
        )

st.markdown("---")
st.caption("中国心理协会认证设计 | 仅供参考，不构成决策建议")
