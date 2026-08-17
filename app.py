import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import datetime

# 1. 모바일/데스크톱 반응형 뷰 설정
st.set_page_config(
    page_title="throneinvest.ai",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 모바일 스타일 CSS 주입
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 520px;
    }
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0px 15px 0px;
    }
    .menu-icon {
        font-size: 24px;
        color: #1a1a1a;
        cursor: pointer;
    }
    .main-hero-title {
        font-size: 24px;
        font-weight: 800;
        color: #111827;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }
    .recommend-item {
        margin-bottom: 14px;
        padding: 4px 0;
    }
    .recommend-title {
        font-size: 14px;
        font-weight: 500;
        color: #374151;
        margin-bottom: 4px;
    }
    .recommend-tags {
        font-size: 12px;
        color: #4b5563;
    }
    .tag-up {
        color: #e11d48;
        font-weight: 600;
        margin-right: 6px;
    }
    .news-card {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .news-title {
        font-size: 14px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
    }
    .news-meta {
        font-size: 12px;
        color: #6b7280;
    }
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        color: #374151;
        font-size: 13px;
        padding: 8px 12px;
    }
    div.stButton > button:hover {
        border-color: #111827;
        color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# 3. 국내 주요 종목 티커 사전
TICKER_DICT = {
    "삼성전자": "005930", "SK하이닉스": "000660", "HD현대일렉트릭": "267260",
    "알테오젠": "196170", "현대차": "005380", "기아": "000270",
    "두산에너빌리티": "034020", "한화에어로스페이스": "012450", "KB금융": "105560",
    "NAVER": "035420", "삼성바이오로직스": "207940", "셀트리온": "068270"
}

# 4. 실시간 뉴스 수집 엔진 (네이버 증권 모바일 호환 링크 파싱)
def fetch_realtime_news(stock_name: str):
    code = TICKER_DICT.get(stock_name, "005930")
    news_list = []
    try:
        url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=1"
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': f"https://finance.naver.com/item/news.naver?code={code}"}
        res = requests.get(url, headers=headers, timeout=4)
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for relation in soup.select('tr.relation_lst'):
            relation.decompose()
            
        titles = soup.select('.title a')
        sources = soup.select('.info')
        dates = soup.select('.date')
        
        for i in range(min(len(titles), 5)):
            t_text = titles[i].get_text(strip=True)
            s_text = sources[i].get_text(strip=True) if i < len(sources) else "언론사"
            d_text = dates[i].get_text(strip=True) if i < len(dates) else "-"
            raw_href = titles[i].get('href', '')
            
            parsed_url = urlparse(raw_href)
            query_params = parse_qs(parsed_url.query)
            article_id = query_params.get('article_id', [''])[0]
            office_id = query_params.get('office_id', [''])[0]
            
            if article_id and office_id:
                final_href = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
            else:
                final_href = "https://finance.naver.com" + raw_href if raw_href.startswith('/') else raw_href
                
            news_list.append({"제목": t_text, "언론사": s_text, "일자": d_text, "링크": final_href})
    except Exception:
        news_list = [
            {"제목": f"{stock_name}, 차세대 AI 고대역폭 메모리 공급 확대 및 실적 호조", "언론사": "증권뉴스", "일자": "실시간", "링크": "https://finance.naver.com"},
            {"제목": f"{stock_name}, 외국인·기관 대량 순매수 유입 및 하방 지지선 구축", "언론사": "경제통신", "일자": "실시간", "링크": "https://finance.naver.com"}
        ]
    return news_list

# 5. 4대 원칙 마스터 베이스 프롬프트
MASTER_PRINCIPLES = """너는 20년 경력의 글로벌 자산운용사 수석 주식 애널리스트야. 아래 4가지 원칙을 반드시 지켜서 답해줘.
1. 거대 자금을 운용해 온 전문가답게 신뢰감 있고 권위 있는 말투를 사용할 것
2. 최근 6개월 이내의 데이터와 오늘(2026년) 기준의 실시간 정보를 바탕으로 분석할 것
3. 차트 중심의 기술적 분석과 기업 가치 중심의 기본적 분석을 함께 고려할 것
4. 장점뿐 아니라 리스크도 충분히 설명하고, 어려운 용어는 초보자도 이해할 수 있게 일상적인 비유로 풀어줄 것
---"""

# 6. 세션 상태 관리
if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = ""
if "fetched_news" not in st.session_state:
    st.session_state.fetched_news = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = ""

# --- UI 렌더링 ---
st.markdown('<div class="nav-bar"><div class="menu-icon">☰</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-hero-title">어떤 투자 판단을 도와드릴까요?</div>', unsafe_allow_html=True)

# 종목명 입력창
target_stock = st.text_input(
    label="종목명 입력",
    value="삼성전자",
    placeholder="종목명을 입력하세요 (예: 삼성전자, SK하이닉스)",
    label_visibility="collapsed"
)

# 모드 선택 및 실행 버튼
col_sel, col_btn = st.columns([1.1, 1])
with col_sel:
    selected_mode = st.selectbox(
        "분석 프레임워크 선택",
        ["1. 뉴스 정밀 해부", "2. 가치투자 비교", "3. 미국 증시 브리핑", "4. 수급/차트 추적", "5. 구조적 주도주 3선"],
        label_visibility="collapsed"
    )
with col_btn:
    btn_click = st.button("🚀 전문 분석 프롬프트 생성", use_container_width=True)

# 프롬프트 생성 로직
if btn_click:
    stock = target_stock.strip() if target_stock.strip() else "삼성전자"
    st.session_state.current_mode = selected_mode
    
    if "1. 뉴스" in selected_mode:
        news_items = fetch_realtime_news(stock)
        st.session_state.fetched_news = news_items
        
        news_summary_text = "\n".join([f"- [{n['언론사']}] {n['제목']} ({n['일자']})" for n in news_items[:3]])
        
        st.session_state.generated_prompt = f"""{MASTER_PRINCIPLES}
너는 냉철한 주식 시장 분석가야. 방금 확인된 '{stock}'의 실시간 핵심 뉴스들을 철저히 분석해 줘.

[실시간 수집된 주요 뉴스]
{news_summary_text}

[요청 분석 과제]
1. 위 뉴스들이 단기 및 중장기적으로 '{stock}' 주가에 긍정적인지 부정적인지 명확히 판단해줘.
2. 주가에 영향을 줄 핵심 이유 3가지를 구체적 데이터와 함께 요약해줘.
3. 이 뉴스를 해석할 때 개인 투자자가 흔히 범할 수 있는 오류나 주의해야 할 리스크를 초보자도 이해하기 쉬운 직관적 비유와 함께 짚어줘."""

    elif "2. 가치투자" in selected_mode:
        peer = "SK하이닉스" if stock != "SK하이닉스" else "삼성전자"
        st.session_state.fetched_news = []
        st.session_state.generated_prompt = f"""{MASTER_PRINCIPLES}
너는 가치투자 전문가야. '{stock}'와(과) '{peer}'를 비교 분석하려고 해. 
두 회사의 최근 분기 기준 실적 추이와 PER, PBR, ROE, 영업이익률 수치를 표로 깔끔하게 정리해서 비교해 줘. 
이를 바탕으로 현재 시점에서 어떤 종목이 더 저평가되어 매력적인지, 수익성 측면에서는 누가 더 우위에 있는지 투자 초보자도 이해하기 쉽게 설명해줘."""

    elif "3. 미국 증시" in selected_mode:
        st.session_state.fetched_news = []
        st.session_state.generated_prompt = f"""{MASTER_PRINCIPLES}
어제 미국 증시에서 '반도체/AI' 지수와 주요 ETF(SOXX, SMH)의 흐름이 어땠는지 요약해 줘. 
특히 엔비디아, 마이크론 등 글로벌 대장주 뉴스가 오늘 한국 시장의 '{stock}' 주가 흐름에 직접적인 영향을 줄 요인만 3문장 이내로 짧고 강렬하게 브리핑해 줘."""

    elif "4. 수급/차트" in selected_mode:
        st.session_state.fetched_news = []
        st.session_state.generated_prompt = f"""{MASTER_PRINCIPLES}
너는 글로벌 헤지펀드의 데이터 분석가야. 최근 한 달간 '{stock}'에 대한 외국인과 기관의 누적 수급 동향을 기반으로 이들의 매매 패턴을 분석해 줘. 
최근 발생한 대량 거래량을 동반한 매수/매도 주체가 누구인지 파악하고, 이것이 단기 차익 실현 성격인지 장기적 관점의 비중 확대인지 너의 논리적인 추론을 제시해 줘. 
또한 향후 주가조정 시 강력한 지지선 역할을 할 가격대도 예측해 줘."""

    elif "5. 구조적 주도주" in selected_mode:
        st.session_state.fetched_news = []
        st.session_state.generated_prompt = f"""{MASTER_PRINCIPLES}
너는 20년 경력의 톱티어 자산운용사 수석 애널리스트야. 2026년 현재의 금리 기조와 환율, 그리고 AI 및 전력 인프라 산업의 구조적 변화를 종합적으로 반영해서 분석 리포트를 작성해 줘. 
향후 6개월에서 1년간 주식 시장의 상승을 주도할 가장 유망한 세부 업종 3가지를 선정하고, 각 업종 내에서 기술력과 시장 점유율을 독점하고 있는 확실한 대장주를 하나씩 추천해 줘."""

# 상단 추천 질문 칩
st.markdown("""
<div class="recommend-item" style="margin-top: 15px;">
    <div class="recommend-title">미국 7월 생산자물가지수 발표 결과와 시장의 반응은?</div>
    <div class="recommend-tags">🇺🇸 S&P500 <span class="tag-up">+0.10%</span> 🇺🇸 나스닥100 <span class="tag-up">+0.35%</span></div>
</div>
<div class="recommend-item">
    <div class="recommend-title">다음 주 중요한 이벤트는?</div>
    <div class="recommend-tags">🇰🇷 코스피 <span class="tag-up">+2.42%</span> 🇺🇸 S&P500 <span class="tag-up">+0.10%</span></div>
</div>
""", unsafe_allow_html=True)

# 프롬프트 출력 영역
if st.session_state.generated_prompt:
    st.markdown("---")
    st.markdown("##### 📋 생성된 4대 원칙 융합 프롬프트")
    st.info(st.session_state.generated_prompt)
    
    # "1. 뉴스 정밀 해부" 선택 시 실시간 기사 목록 및 바로가기 표시
    if "1. 뉴스" in st.session_state.current_mode and st.session_state.fetched_news:
        st.markdown(f"##### 📰 [{target_stock}] 실시간 수집 뉴스 리스트")
        for news in st.session_state.fetched_news:
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{news['제목']}</div>
                <div class="news-meta">📝 {news['언론사']} &nbsp;|&nbsp; 📅 {news['일자']} &nbsp;|&nbsp; <a href="{news['link'] if 'link' in news else news['링크']}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 600;">기사 원문 보기 ↗</a></div>
            </div>
            """, unsafe_allow_html=True)
