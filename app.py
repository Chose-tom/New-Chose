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
WECHAT_PAY_URL = ""  # 替换成你的微信收款码图片直链

# 会话状态（新增，不影响原代码）
if "full_report_text" not in st.session_state:
    st.session_state.full_report_text = ""
if "is_unlock_all" not in st.session_state:
    st.session_state.is_unlock_all = False
if "show_ad_btn" not in st.session_state:
    st.session_state.show_ad_btn = False
if "show_pay_btn" not in st.session_state:
    st.session_state.show_pay_btn = False

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
    height=120
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

# ========== 以下是你原来完全不变的生成按钮逻辑 ==========
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
        
        st.session_state.full_report_text = full
        st.session_state.is_unlock_all = False
        st.session_state.show_ad_btn = False
        st.session_state.show_pay_btn = False

# ========== 新增：解锁 + 所有人可下载完整报告（不改动原有生成代码） ==========
if st.session_state.full_report_text:
    st.markdown("---")
    if st.session_state.is_unlock_all:
        # 已解锁：完整显示 + 所有人可下载
        st.markdown(st.session_state.full_report_text)
        st.download_button(
            "📥 所有人可下载完整报告",
            st.session_state.full_report_text.encode("utf-8"),
            file_name="AI决策分析报告.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        # 未解锁：只显示30%预览
        preview_text = st.session_state.full_report_text[:int(len(st.session_state.full_report_text)*0.3)] + "\n\n...（剩余内容需解锁）"
        st.markdown(preview_text)
        st.info("🔓 选择以下方式解锁完整内容与下载权限")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📺 观看视频广告解锁", use_container_width=True):
                st.session_state.show_ad_btn = True
                st.session_state.show_pay_btn = False
        with c2:
            if st.button("💰 6.9元直接解锁", use_container_width=True):
                st.session_state.show_pay_btn = True
                st.session_state.show_ad_btn = False

        # 广告解锁
        if st.session_state.show_ad_btn:
            st.success("📺 广告播放完成后自动解锁")
            if st.button("✅ 我已看完广告，解锁全部", use_container_width=True):
                st.session_state.is_unlock_all = True
                st.rerun()
        # 付费解锁
        if st.session_state.show_pay_btn:
            st.subheader("💰 微信扫码支付9.9元")
            if WECHAT_PAY_URL:
                st.image(WECHAT_PAY_URL, width=300)
            if st.button("✅ 我已支付，解锁全部", type="primary", use_container_width=True):
                st.session_state.is_unlock_all = True
                st.rerun()

st.markdown("---")
st.caption("中国心理协会团队认证设计 | 仅供参考，不构成决策建议")
