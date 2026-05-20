import streamlit as st
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

st.set_page_config(
    page_title="AI决策后果模拟器",
    page_icon="🤔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- 只需要修改这里的3个值 --------------------------
API_KEY = "ark-178af4e5-fdfc-4fef-a9e0-2c00337634a1-46b10"
ENDPOINT_ID = "ep-20260520162214-8f4dc"
AD_SLOT_ID = ""
# -------------------------------------------------------------------------

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
    placeholder="例如：我今年30岁，有房贷，月薪1万，工作5年",
    height=100
)

PROMPT_TEMPLATE = """
你是一个绝对中立的决策分析助手，永远不要替用户做任何决定。
请严格按照以下结构，客观分析两个选择的所有可能后果，不要带有任何个人倾向。

# 选择A：{option1}
## 时间线推演
- 短期（1-3个月）：
- 中期（3-12个月）：
- 长期（1-3年）：

## 分维度得失
- 物质层面（收入、支出、资产）：
- 能力层面（技能、经验、成长）：
- 人际关系（同事、家人、朋友）：
- 精神状态（压力、情绪、幸福感）：

## 风险分级与紧急预案
- 高概率风险（>70%）：
  风险描述：
  紧急应对方案：
- 中概率风险（30%-70%）：
  风险描述：
  紧急应对方案：
- 低概率风险（<30%）：
  风险描述：
  紧急应对方案：

## 最容易后悔的3个点及避免方法
1. 
2. 
3. 

# 选择B：{option2}
## 时间线推演
- 短期（1-3个月）：
- 中期（3-12个月）：
- 长期（1-3年）：

## 分维度得失
- 物质层面（收入、支出、资产）：
- 能力层面（技能、经验、成长）：
- 人际关系（同事、家人、朋友）：
- 精神状态（压力、情绪、幸福感）：

## 风险分级与紧急预案
- 高概率风险（>70%）：
  风险描述：
  紧急应对方案：
- 中概率风险（30%-70%）：
  风险描述：
  紧急应对方案：
- 低概率风险（<30%）：
  风险描述：
  紧急应对方案：

## 最容易后悔的3个点及避免方法
1. 
2. 
3. 

# 最终中立提示
本分析仅为基于普遍情况的逻辑推演，不构成任何决策建议。
所有选择的后果都需要你自己承担，请结合你的实际情况做出决定。

用户补充说明：{context}
"""

def generate_report(option1, option2, context):
    if not API_KEY or not ENDPOINT_ID:
        return "❌ 请先在代码顶部填写你的API密钥和模型端点"
    
    try:
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        prompt = PROMPT_TEMPLATE.format(
            option1=option1,
            option2=option2,
            context=context if context else "无"
        )
        
        data = {
            "model": ENDPOINT_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 3000,
            "stream": False
        }

        # 增加重试机制
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        
        # 超时时间从60秒改成120秒
        response = session.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        return f"❌ 生成失败：{str(e)}\n\n请稍后重试，或检查网络连接。"

if st.button("🚀 开始模拟决策", type="primary", use_container_width=True):
    if not option1 or not option2:
        st.warning("⚠️ 请输入两个选择")
    else:
        with st.spinner("正在为你生成完整决策报告，请稍候..."):
            report = generate_report(option1, option2, context)
            
            preview_length = int(len(report) * 0.3)
            st.markdown(report[:preview_length] + "\n\n...")
            
            st.markdown("---")
            st.info("👇 观看30秒广告，解锁完整报告")
            
            if AD_SLOT_ID:
                if st.button("📺 观看广告解锁完整报告", use_container_width=True):
                    st.markdown("---")
                    st.markdown(report)
            else:
                st.warning("⚠️ 广告功能正在配置中，目前可以免费查看完整报告")
                st.markdown("---")
                st.markdown(report)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("本工具由中国心理协会认证心理咨询师设计")
with col2:
    st.caption("基于决策心理学原理开发")
with col3:
    st.caption("仅供参考，不构成任何决策建议")
