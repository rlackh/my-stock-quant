import streamlit as st
import datetime

# 1. 모바일 뷰 최적화 설정
st.set_page_config(
    page_title="throneinvest.ai",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 이미지 UI 완벽 복제 스타일 CSS 주입
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 480px;
    }
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0px 20px 0px;
    }
    .menu-icon {
        font-size: 24px;
        color: #1a1a1a;
        cursor: pointer;
    }
    .main-hero-title {
        font-size: 26px;
        font-weight: 800;
        color: #111827;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 24px;
        letter-spacing: -0.5px;
    }
    .recommend-item {
        margin-bottom: 18px;
        padding: 4px 0;
    }
    .recommend-title {
        font-size: 15px;
        font-weight: 500;
        color: #374151;
        margin-bottom: 6px;
        cursor: pointer;
    }
    .recommend-tags {
        font-size: 13px;
        color: #4b5563;
    }
    .tag-up {
        color: #e11d48;
        font-weight: 600;
        margin-right: 8px;
    }
    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 28px;
        margin-bottom: 12px;
    }
    .history-title {
        font-size: 17px;
        font-weight: 700;
        color: #111827;
    }
    .history-more {
        font-size: 13px;
        color: #9ca3af;
        cursor: pointer;
        text-decoration: underline;
    }
    .history-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .history-left {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        color: #374151;
    }
    .history-right {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 12px;
        color: #9ca3af;
    }
    div.stButton > button {
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        color: #374151;
        font-size: 13px;
        padding: 8px 12px;
        text-align: left;
    }
    div.stButton > button:hover {
        border-color: #111827;
        color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# 3. 4대 원칙 마스터 베이스 프롬프트 정의
MASTER_PRINCIPLES = """너는 20년 경력의 글로벌 자산운용사 수석 주식 애널리스트야. 아래 4가지 원칙을 반드시 지켜서 답해줘.
1. 거대 자금을 운용해 온 전문가답게 신뢰감 있고 권위 있는 말투를 사용할 것
2. 최근 6개월 이내의 데이터와 오늘(2026년) 기준의 실시간 정보를 바탕으로 분석할 것
3. 차트 중심의 기술적 분석과 기업 가치 중심의 기본적 분석을 함께 고려할 것
4. 장점뿐 아니라 리스크도 충분히 설명하고, 어려운 용어는 초보자도 이해할 수 있게 일상적인 비유로 풀어줄 것
---"""

# 4. 5대 전문 분석 프레임워크 템플릿 생성 함수
def generate_framework_prompt(mode_index: int, target="삼성전자", peer="SK하이닉스", sector="반도체/AI", news_text="실적 발표"):
    if mode_index == 1:
        return f"""{MASTER_PRINCIPLES}
너는 냉철한 주식 시장 분석가야. 방금 나온 '{target}'의 뉴스 [{news_text}]을 분석해 줘. 
1. 이 뉴스가 단기 및 중장기적으로 주가에 긍정적인지 부정적인지 판단하고, 그 핵심 이유를 3가지로 명확히 요약해 줘.
2. 마지막으로 이 뉴스를 해석할 때 개인 투자자가 흔히 범할 수 있는 오류나 주의해야 할 리스크도 함께 짚어줘."""

    elif mode_index == 2:
        return f"""{MASTER_PRINCIPLES}
너는 가치투자 전문가야. '{target}'와(과) '{peer}'를 비교 분석하려고 해. 
두 회사의 최근 분기 기준 실적 추이와 PER, PBR, ROE, 영업이익률 수치를 표로 깔끔하게 정리해서 비교해 줘. 
이를 바탕으로 현재 시점에서 어떤 종목이 더 저평가되어 매력적인지, 수익성 측면에서는 누가 더 우위에 있는지 투자 초보자도 이해하기 쉽게 설명해줘."""

    elif mode_index == 3:
        return f"""{MASTER_PRINCIPLES}
어제 미국 증시에서 '{sector}' 지수와 주요 ETF의 흐름이 어땠는지 요약해 줘. 
특히 글로벌 대장주(예: 엔비디아, 테슬라 등)와 관련된 최신 핵심 뉴스 중에서, 오늘 한국 시장의 '{target}' 주가 흐름에 직접적인 영향을 줄 만한 요인만 3문장 이내로 짧고 강렬하게 브리핑해 줘."""

    elif mode_index == 4:
        return f"""{MASTER_PRINCIPLES}
너는 글로벌 헤지펀드의 데이터 분석가야. 최근 한 달간 '{target}'에 대한 외국인과 기관의 누적 수급 동향을 기반으로 이들의 매매 패턴을 분석해 줘. 
최근 발생한 대량 거래량을 동반한 매수/매도 주체가 누구인지 파악하고, 이것이 단기 차익 실현 성격인지 장기적 관점의 비중 확대인지 너의 논리적인 추론을 제시해 줘. 
또한 향후 주가조정 시 강력한 지지선 역할을 할 가격대도 예측해 줘."""

    elif mode_index == 5:
        return f"""{MASTER_PRINCIPLES}
너는 20년 경력의 톱티어 자산운용사 수석 애널리스트야. 2026년 현재의 금리 기조와 환율, 그리고 '{sector}' 산업의 구조적 변화를 종합적으로 반영해서 분석 리포트를 작성해 줘. 
향후 6개월에서 1년간 주식 시장의 상승을 주도할 가장 유망한 세부 업종 3가지를 선정하고, 각 업종 내에서 기술력과 시장 점유율을 독점하고 있는 확실한 대장주를 하나씩 추천해 줘. 
추천 근거는 구체적인 데이터나 예상 시나리오를 바탕으로 작성해."""

# 5. 세션 상태 관리
if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = ""

# --- 화면 렌더링 ---
st.markdown("""
<div class="nav-bar">
    <div class="menu-icon">☰</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-hero-title">어떤 투자 판단을 도와드릴까요?</div>', unsafe_allow_html=True)

user_input = st.text_input(
    label="투자 판단 질문 입력",
    placeholder="투자 판단에 필요한 질문을 입력하세요",
    label_visibility="collapsed"
)

tool_col1, tool_col2 = st.columns([1, 1])
with tool_col1:
    selected_mode = st.selectbox(
        "분석 프레임워크 선택",
        ["1. 뉴스 정밀 해부", "2. 가치투자 비교", "3. 미국 증시 브리핑", "4. 수급/차트 추적", "5. 구조적 주도주 3선"],
        label_visibility="collapsed"
    )
with tool_col2:
    if st.button("🚀 전문 분석 프롬프트 생성", use_container_width=True):
        mode_num = int(selected_mode[0])
        target_name = user_input.strip() if user_input.strip() else "삼성전자"
        st.session_state.generated_prompt = generate_framework_prompt(mode_num, target=target_name)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="recommend-item">
    <div class="recommend-title">미국 7월 생산자물가지수 발표 결과와 시장의 반응은?</div>
    <div class="recommend-tags">
        🇺🇸 S&P500 <span class="tag-up">+0.10%</span> 🇺🇸 나스닥100 <span class="tag-up">+0.35%</span>
    </div>
</div>
<div class="recommend-item">
    <div class="recommend-title">다음 주 중요한 이벤트는?</div>
    <div class="recommend-tags">
        🇰🇷 코스피 <span class="tag-up">+2.42%</span> 🇺🇸 S&P500 <span class="tag-up">+0.10%</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.generated_prompt:
    st.markdown("---")
    st.markdown("##### 📋 생성된 4대 원칙 융합 프롬프트")
    st.info(st.session_state.generated_prompt)
    if st.button("✂️ 프롬프트 전체 복사", use_container_width=True):
        st.success("프롬프트가 복사되었습니다. AI에게 질문을 입력하여 보고서를 생성하십시오.")

st.markdown("""
<div class="history-header">
    <div class="history-title">대화</div>
    <div class="history-more">더 보기</div>
</div>

<div class="history-card">
    <div class="history-left">💬 오늘 외국인과 연기금 자금...</div>
    <div class="history-right">2026. 8. 3. &nbsp; 🔖 &nbsp; ⋯</div>
</div>

<div class="history-card">
    <div class="history-left">💬 손실 난 종목, 더 살지 정리할...</div>
    <div class="history-right">2026. 8. 2. &nbsp; 🔖 &nbsp; ⋯</div>
</div>

<div class="history-card">
    <div class="history-left">💬 금리·유가·VIX 중 지금 가장 ...</div>
    <div class="history-right">2026. 8. 1. &nbsp; 🔖 &nbsp; ⋯</div>
</div>
""", unsafe_allow_html=True)
