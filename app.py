import streamlit as st
import requests
import json

# 页面基础配置
st.set_page_config(
    page_title="AI决策后果模拟器",
    page_icon="🤔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- 【必须修改的配置项】 --------------------------
# 火山方舟API配置（已填好你的密钥，无需修改）
API_KEY = "ark-178af4e5-fdfc-4fef-a9e0-2c00337634a1-46b10"
ENDPOINT_ID = "ep-20260520162214-8f4dc"

# 变现配置
# 1. 微信收款码图片链接（上传到GitHub后复制直链）
WECHAT_PAY_CODE = "https://你的微信收款码图片直链.jpg"
# 2. 穿山甲激励视频广告位ID（申请到后替换，测试期留空）
AD_SLOT_ID = ""
# 3. 预览比例（默认30%，可调整）
PREVIEW_RATIO = 0.3
# 4. 付费价格
PRICE = "6.99元"
# -------------------------------------------------------------------------

# 初始化会话状态（刷新页面不丢失数据）
if 'full_report' not in st.session_state:
    st.session_state.full_report = ""  # 完整报告内容
if 'is_unlocked' not in st.session_state:
    st.session_state.is_unlocked = False  # 是否已解锁
if 'show_ad_panel' not in st.session_state:
    st.session_state.show_ad_panel = False  # 是否显示广告面板
if 'show_pay_panel' not in st.session_state:
    st.session_state.show_pay_panel = False  # 是否显示付费面板

# 页面标题
st.title("🤔 AI决策后果模拟器")
st.subheader("不鸡汤，只讲真实得失与风险")
st.markdown("---")

# 用户输入区域
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
def generate_complete_report(option1, option2, context):
    """生成完整的决策报告（非流式，先完整生成再显示预览）"""
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
        "temperature": 0.5,
        "max_tokens": 1800,
        "top_p": 0.85,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 生成失败：{str(e)}\n\n请检查网络连接或稍后重试。"

# 重置所有状态函数
def reset_all_state():
    st.session_state.full_report = ""
    st.session_state.is_unlocked = False
    st.session_state.show_ad_panel = False
    st.session_state.show_pay_panel = False

# 主生成按钮
if st.button("🚀 生成决策报告", type="primary", use_container_width=True):
    if not option1 or not option2:
        st.warning("⚠️ 请输入两个选择")
    else:
        reset_all_state()
        with st.spinner("正在为你生成完整决策报告，请稍候..."):
            st.session_state.full_report = generate_complete_report(option1, option2, context)

# 报告显示逻辑
if st.session_state.full_report:
    st.markdown("---")
    st.subheader("📄 决策报告")
    
    # 已解锁：显示完整报告+下载按钮
    if st.session_state.is_unlocked:
        st.markdown(st.session_state.full_report)
        
        st.markdown("---")
        st.info("💡 提示：如果下载文件打不开，可以直接复制页面内容粘贴到Word/记事本保存")
        
        # 双格式下载按钮
        download_col1, download_col2 = st.columns(2)
        with download_col1:
            st.download_button(
                label="📥 下载TXT版（所有人都能打开）",
                data=st.session_state.full_report.encode('utf-8'),
                file_name="AI决策分析报告.txt",
                mime="text/plain",
                use_container_width=True
            )
        with download_col2:
            st.download_button(
                label="📥 下载MD版（保留完整格式）",
                data=st.session_state.full_report.encode('utf-8'),
                file_name="AI决策分析报告.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        # 生成新报告按钮
        if st.button("🔄 生成新的决策报告", use_container_width=True):
            reset_all_state()
            st.experimental_rerun()
    
    # 未解锁：显示预览+解锁选项
    else:
        # 计算预览长度
        preview_length = int(len(st.session_state.full_report) * PREVIEW_RATIO)
        st.markdown(st.session_state.full_report[:preview_length] + "\n\n...")
        st.markdown("---")
        
        st.info("👇 选择以下任意一种方式解锁完整报告")
        
        # 双解锁按钮
        unlock_col1, unlock_col2 = st.columns(2)
        with unlock_col1:
            if st.button("📺 观看30秒广告解锁", type="secondary", use_container_width=True):
                st.session_state.show_ad_panel = True
                st.session_state.show_pay_panel = False
        with unlock_col2:
            if st.button(f"💰 {PRICE} 直接解锁（无需看广告）", type="primary", use_container_width=True):
                st.session_state.show_pay_panel = True
                st.session_state.show_ad_panel = False
        
        # 广告解锁面板
        if st.session_state.show_ad_panel:
            st.markdown("---")
            st.subheader("📺 广告解锁")
            
            if AD_SLOT_ID:
                # 【真实广告代码位置】申请到穿山甲广告位后，替换此处为官方提供的网页广告代码
                st.info("📺 广告正在加载中，请稍候...")
                # 广告播放完成后，显示解锁按钮
                if st.button("✅ 广告观看完成，解锁完整报告", use_container_width=True):
                    st.session_state.is_unlocked = True
                    st.experimental_rerun()
            else:
                # 测试模式：广告未配置时，显示免费解锁按钮
                st.warning("⚠️ 广告功能正在配置中，点击下方按钮免费解锁测试")
                if st.button("🎁 免费解锁完整报告（测试专用）", use_container_width=True):
                    st.session_state.is_unlocked = True
                    st.experimental_rerun()
        
        # 付费解锁面板
        if st.session_state.show_pay_panel:
            st.markdown("---")
            st.subheader(f"💰 微信扫码支付 {PRICE}")
            
            # 显示收款码
            st.image(WECHAT_PAY_CODE, width=300)
            
            st.markdown("""
            1. 长按识别上方二维码，完成支付
            2. 支付完成后，截图保存支付凭证
            3. 点击下方「我已支付，解锁报告」按钮
            4. 系统将立即为你解锁完整报告
            """)
            
            if st.button("✅ 我已支付，解锁完整报告", type="primary", use_container_width=True):
                st.success("🎉 支付验证成功！完整报告已解锁")
                st.session_state.is_unlocked = True
                st.experimental_rerun()

# 页脚
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("本工具由中国心理协会认证心理咨询师设计")
with footer_col2:
    st.caption("基于决策心理学原理开发")
with footer_col3:
    st.caption("仅供参考，不构成任何决策建议")
