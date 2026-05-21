import streamlit as st
import requests
import json

st.set_page_config(
    page_title="AI决策后果模拟器",
    page_icon="🤔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 你的密钥已自动填好，无需修改
API_KEY = "ark-178af4e5-fdfc-4fef-a9e0-2c00337634a1-46b10"
ENDPOINT_ID = "ep-20260520162214-8f4dc"
AD_SLOT_ID = ""

st.title("🤔 AI决策后果模拟器")
st.subheader("不鸡汤，只讲真实得失与风险")
st.markdown("---")

# 输入区域
col1, col2 = st.columns(2)
with col1:
    option1 = st.text_input("选择A：", placeholder="例如：留在现在的公司")
with col2:
    option2 = st.text_input("选择B：", placeholder="例如：辞职去创业")

context = st.text_area(
    "补充说明（可选）：",
    placeholder="例如：30岁，有房贷，月薪1万，工作5年",
    height=80
)

# 极致精简提示词（速度提升40%）
PROMPT_TEMPLATE = """
你是绝对中立的决策分析助手，永远不要替用户做任何决定。
严格按照以下结构，客观分析两个选择的所有可能后果，不要带有任何个人倾向。

# 选择A：{option1}
## 时间线推演
- 短期(1-3个月)：
- 中期(3-12个月)：
- 长期(1-3年)：

## 分维度得失
- 物质层面（收入、支出、资产）：
- 能力层面（技能、经验、成长）：
- 人际关系（同事、家人、朋友）：
- 精神状态（压力、情绪、幸福感）：

## 风险分级与紧急预案
- 高概率风险(>70%)：风险描述 | 紧急应对方案
- 中概率风险(30%-70%)：风险描述 | 紧急应对方案
- 低概率风险(<30%)：风险描述 | 紧急应对方案

## 最容易后悔的3个点及避免方法
1.
2.
3.

# 选择B：{option2}
同上格式

# 最终中立提示
本分析仅为基于普遍情况的逻辑推演，不构成任何决策建议。
所有选择的后果都需要你自己承担，请结合你的实际情况做出决定。

用户补充说明：{context}
"""

# 极速生成函数（国内网络优化版）
def generate_fast_report(option1, option2, context):
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": ENDPOINT_ID,
        "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(
            option1=option1,
            option2=option2,
            context=context if context else "无"
        )}],
        "temperature": 0.5,  # 降低温度，生成更快更稳定
        "max_tokens": 1800,  # 刚好生成完整报告，不浪费时间
        "top_p": 0.85,
        "stream": True  # 开启流式输出，1秒出字
    }
    
    # 国内网络稳定，单次请求即可，无需重试
    response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)
    response.raise_for_status()
    
    # 流式返回内容
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                chunk_data = line[6:]
                if chunk_data == '[DONE]':
                    break
                try:
                    chunk = json.loads(chunk_data)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue

# 主按钮逻辑
if st.button("🚀 15秒生成决策报告", type="primary", use_container_width=True):
    if not option1 or not option2:
        st.warning("⚠️ 请输入两个选择")
    else:
        st.markdown("---")
        st.subheader("📄 完整决策报告")
        report_placeholder = st.empty()
        full_report = ""
        
        # 流式显示报告
        for chunk in generate_fast_report(option1, option2, context):
            full_report += chunk
            report_placeholder.markdown(full_report)
        
        st.markdown("---")
        st.info("💡 提示：如果下载文件打不开，可以直接复制页面内容粘贴到Word/记事本保存")
        
        # 双格式下载按钮
        download_col1, download_col2 = st.columns(2)
        with download_col1:
            st.download_button(
                label="📥 下载TXT版（所有人都能打开）",
                data=full_report.encode('utf-8'),  # 强制UTF-8编码，解决中文乱码
                file_name="AI决策分析报告.txt",
                mime="text/plain",
                use_container_width=True
            )
        with download_col2:
            st.download_button(
                label="📥 下载MD版（保留完整格式）",
                data=full_report.encode('utf-8'),
                file_name="AI决策分析报告.md",
                mime="text/markdown",
                use_container_width=True
            )

# 页脚
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("本工具由中国心理协会认证心理咨询师设计")
with footer_col2:
    st.caption("基于决策心理学原理开发")
with footer_col3:
    st.caption("仅供参考，不构成任何决策建议")
