import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="미국 주식 옵션 분석기",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class OptionAnalyzer:
    """미국 주식 옵션 달성 가능성 분석기"""
    
    def __init__(self, ticker, strike_price, expiry_date, current_price, 
                 annual_volatility=None, beta=1.0, company_name=None, option_type='call'):
        self.ticker = ticker
        self.strike_price = strike_price
        self.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
        self.current_price = current_price
        self.beta = beta
        self.company_name = company_name if company_name else ticker
        self.option_type = option_type.lower()
        
        if annual_volatility is None:
            self.annual_volatility = 0.15 * abs(beta) * 1.5
        else:
            self.annual_volatility = annual_volatility
        
        self.generate_historical_data()
        self.calculate_metrics()
        
    def generate_historical_data(self):
        """시뮬레이션용 과거 데이터 생성"""
        days = 126
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
        
        np.random.seed(42)
        returns = np.random.normal(0, self.annual_volatility/np.sqrt(252), days)
        
        prices = np.zeros(days)
        prices[-1] = self.current_price
        for i in range(days-2, -1, -1):
            prices[i] = prices[i+1] / (1 + returns[i+1])
        
        self.df = pd.DataFrame({
            'Close': prices,
            'Date': dates
        })
        self.df.set_index('Date', inplace=True)
        
    def calculate_metrics(self):
        """주요 지표 계산"""
        self.df['Returns'] = self.df['Close'].pct_change()
        self.daily_volatility = self.df['Returns'].std()
        self.annual_volatility = self.daily_volatility * np.sqrt(252)
        
        self.days_to_expiry = (self.expiry_date - datetime.now()).days
        self.years_to_expiry = self.days_to_expiry / 365.0
        self.required_change = (self.strike_price / self.current_price - 1) * 100
        
    def black_scholes_probability(self):
        """블랙-숄즈 모델을 이용한 확률 계산"""
        S = self.current_price
        K = self.strike_price
        T = self.years_to_expiry
        sigma = self.annual_volatility
        r = 0.045
        
        d2 = (np.log(S/K) + (r - 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        
        if self.option_type == 'call':
            probability = norm.cdf(d2)
        else:
            probability = norm.cdf(-d2)
            
        return probability * 100
        
    def monte_carlo_simulation(self, num_simulations=10000):
        """몬테카를로 시뮬레이션"""
        S = self.current_price
        T = self.years_to_expiry
        sigma = self.annual_volatility
        r = 0.045
        
        np.random.seed(42)
        dt = 1/252
        steps = self.days_to_expiry
        
        price_paths = np.zeros((num_simulations, steps + 1))
        price_paths[:, 0] = S
        
        for t in range(1, steps + 1):
            z = np.random.standard_normal(num_simulations)
            price_paths[:, t] = price_paths[:, t-1] * np.exp(
                (r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z
            )
        
        final_prices = price_paths[:, -1]
        
        if self.option_type == 'call':
            success = final_prices >= self.strike_price
        else:
            success = final_prices <= self.strike_price
            
        probability = np.mean(success) * 100
        
        self.mc_final_prices = final_prices
        self.mc_price_paths = price_paths
        self.mc_probability = probability
        
        return probability
        
    def calculate_expected_profit(self):
        """예상 수익 계산"""
        if self.option_type == 'call':
            payoffs = np.maximum(self.mc_final_prices - self.strike_price, 0)
        else:
            payoffs = np.maximum(self.strike_price - self.mc_final_prices, 0)
            
        expected_payoff = np.mean(payoffs)
        median_payoff = np.median(payoffs)
        
        return expected_payoff, median_payoff
        
    def analyze(self):
        """종합 분석"""
        bs_prob = self.black_scholes_probability()
        mc_prob = self.monte_carlo_simulation()
        expected_payoff, median_payoff = self.calculate_expected_profit()
        
        avg_prob = (bs_prob + mc_prob) / 2
        
        if avg_prob >= 70:
            interpretation = "매우 높음 - 달성 가능성이 높습니다"
        elif avg_prob >= 50:
            interpretation = "높음 - 달성 가능성이 있습니다"
        elif avg_prob >= 30:
            interpretation = "보통 - 불확실성이 있습니다"
        else:
            interpretation = "낮음 - 달성이 어려울 수 있습니다"
            
        return {
            'black_scholes_prob': bs_prob,
            'monte_carlo_prob': mc_prob,
            'average_prob': avg_prob,
            'expected_payoff': expected_payoff,
            'median_payoff': median_payoff,
            'interpretation': interpretation
        }
        
    def create_charts(self):
        """차트 생성"""
        fig = plt.figure(figsize=(16, 10))
        
        # 1. 주가 추이
        ax1 = plt.subplot(2, 3, 1)
        ax1.plot(self.df.index, self.df['Close'], linewidth=2, color='#2E86AB')
        ax1.axhline(y=self.strike_price, color='red', linestyle='--', 
                    linewidth=2, label=f'Strike: ${self.strike_price}')
        ax1.axhline(y=self.current_price, color='green', linestyle='--', 
                    linewidth=1.5, alpha=0.7, label=f'Current: ${self.current_price:.2f}')
        ax1.set_title(f'{self.ticker} Price History (6 Months)', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 일일 수익률 분포
        ax2 = plt.subplot(2, 3, 2)
        returns_percent = self.df['Returns'].dropna() * 100
        ax2.hist(returns_percent, bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
        ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
        ax2.set_title('Daily Returns Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Returns (%)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # 3. 몬테카를로 시뮬레이션 경로
        ax3 = plt.subplot(2, 3, 3)
        sample_paths = np.random.choice(len(self.mc_price_paths), 200, replace=False)
        for path_idx in sample_paths:
            ax3.plot(self.mc_price_paths[path_idx], alpha=0.1, color='gray', linewidth=0.5)
        ax3.axhline(y=self.strike_price, color='red', linestyle='--', 
                    linewidth=2, label=f'Strike: ${self.strike_price}')
        ax3.axhline(y=self.current_price, color='green', linestyle='--', 
                    linewidth=1.5, label=f'Current: ${self.current_price:.2f}')
        ax3.set_title('Monte Carlo Simulation (200 Sample Paths)', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Days to Expiry')
        ax3.set_ylabel('Price ($)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 만기 시 가격 분포
        ax4 = plt.subplot(2, 3, 4)
        ax4.hist(self.mc_final_prices, bins=50, color='#F18F01', alpha=0.7, 
                 edgecolor='black', density=True)
        ax4.axvline(x=self.strike_price, color='red', linestyle='--', 
                    linewidth=2, label=f'Strike: ${self.strike_price}')
        ax4.axvline(x=self.current_price, color='green', linestyle='--', 
                    linewidth=1.5, label=f'Current: ${self.current_price:.2f}')
        ax4.set_title('Final Price Distribution at Expiry', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Price ($)')
        ax4.set_ylabel('Probability Density')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 달성 가능성 비교
        ax5 = plt.subplot(2, 3, 5)
        bs_prob = self.black_scholes_probability()
        methods = ['Black-Scholes\nModel', 'Monte Carlo\nSimulation', 'Average']
        probabilities = [bs_prob, self.mc_probability, (bs_prob + self.mc_probability)/2]
        colors = ['#2E86AB', '#A23B72', '#F18F01']
        bars = ax5.bar(methods, probabilities, color=colors, alpha=0.8, edgecolor='black')
        
        for bar, prob in zip(bars, probabilities):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{prob:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax5.set_title('Probability of Success', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Probability (%)')
        ax5.set_ylim(0, 100)
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 요약 정보
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
OPTION ANALYSIS SUMMARY
{'='*40}

Ticker: {self.ticker}
Option Type: {self.option_type.upper()}
Current Price: ${self.current_price:.2f}
Strike Price: ${self.strike_price:.2f}
Expiry Date: {self.expiry_date.strftime('%Y-%m-%d')}
Days to Expiry: {self.days_to_expiry}

MARKET METRICS
Annual Volatility: {self.annual_volatility*100:.2f}%
Beta: {self.beta:.2f}
Required Change: {self.required_change:+.2f}%

PROBABILITY ANALYSIS
Black-Scholes: {bs_prob:.2f}%
Monte Carlo: {self.mc_probability:.2f}%
Average: {(bs_prob + self.mc_probability)/2:.2f}%

PRICE FORECAST (Percentiles)
10%: ${np.percentile(self.mc_final_prices, 10):.2f}
25%: ${np.percentile(self.mc_final_prices, 25):.2f}
50%: ${np.percentile(self.mc_final_prices, 50):.2f}
75%: ${np.percentile(self.mc_final_prices, 75):.2f}
90%: ${np.percentile(self.mc_final_prices, 90):.2f}
        """
        
        ax6.text(0.1, 0.95, summary_text, transform=ax6.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        return fig


def main():
    # 헤더
    st.title("📊 미국 주식 옵션 달성 가능성 분석기")
    st.markdown("---")
    
    # 사이드바 입력
    st.sidebar.header("⚙️ 옵션 정보 입력")
    
    # 기본 정보
    ticker = st.sidebar.text_input("티커 심볼", value="TSLA", help="예: TSLA, AAPL, NVDA")
    company_name = st.sidebar.text_input("회사명 (선택)", value="Tesla, Inc.")
    
    # 옵션 타입
    option_type = st.sidebar.selectbox(
        "옵션 타입",
        options=["Call (콜)", "Put (풋)"],
        index=0
    )
    option_type = "call" if "Call" in option_type else "put"
    
    # 가격 정보
    col1, col2 = st.sidebar.columns(2)
    with col1:
        current_price = st.number_input("현재가 ($)", value=404.42, min_value=0.01, step=0.01)
    with col2:
        strike_price = st.number_input("행사가 ($)", value=300.0, min_value=0.01, step=0.01)
    
    # 만기일
    min_date = datetime.now().date()
    max_date = (datetime.now() + timedelta(days=365)).date()
    expiry_date = st.sidebar.date_input(
        "만기일",
        value=datetime(2025, 11, 26).date(),
        min_value=min_date,
        max_value=max_date
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("📈 시장 지표 (선택)")
    
    # 변동성
    use_custom_vol = st.sidebar.checkbox("변동성 직접 입력", value=True)
    if use_custom_vol:
        annual_volatility = st.sidebar.slider(
            "연간 변동성 (%)",
            min_value=10,
            max_value=150,
            value=60,
            step=5,
            help="역사적 변동성 또는 내재변동성"
        ) / 100
    else:
        annual_volatility = None
    
    # 베타
    beta = st.sidebar.slider(
        "베타 계수",
        min_value=0.0,
        max_value=3.0,
        value=1.61,
        step=0.01,
        help="시장 대비 민감도"
    )
    
    st.sidebar.markdown("---")
    
    # 분석 버튼
    analyze_button = st.sidebar.button("🔍 분석 시작", type="primary", use_container_width=True)
    
    # 메인 컨텐츠
    if analyze_button:
        with st.spinner("분석 중입니다... 잠시만 기다려주세요."):
            try:
                # 분석 수행
                analyzer = OptionAnalyzer(
                    ticker=ticker,
                    strike_price=strike_price,
                    expiry_date=expiry_date.strftime('%Y-%m-%d'),
                    current_price=current_price,
                    annual_volatility=annual_volatility,
                    beta=beta,
                    company_name=company_name,
                    option_type=option_type
                )
                
                results = analyzer.analyze()
                
                # 결과 표시
                st.success("✅ 분석 완료!")
                
                # 주요 지표 카드
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("달성 가능성", f"{results['average_prob']:.2f}%")
                
                with col2:
                    st.metric("만기까지", f"{analyzer.days_to_expiry}일")
                
                with col3:
                    st.metric("필요 변화율", f"{analyzer.required_change:+.2f}%")
                
                with col4:
                    st.metric("연간 변동성", f"{analyzer.annual_volatility*100:.2f}%")
                
                st.markdown("---")
                
                # 탭으로 결과 구분
                tab1, tab2, tab3 = st.tabs(["📊 분석 결과", "📈 차트", "📋 상세 정보"])
                
                with tab1:
                    # 해석
                    if results['average_prob'] >= 70:
                        st.success(f"### ✅ {results['interpretation']}")
                    elif results['average_prob'] >= 50:
                        st.info(f"### ℹ️ {results['interpretation']}")
                    elif results['average_prob'] >= 30:
                        st.warning(f"### ⚠️ {results['interpretation']}")
                    else:
                        st.error(f"### ❌ {results['interpretation']}")
                    
                    # 확률 비교
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("확률 분석")
                        prob_df = pd.DataFrame({
                            '모델': ['블랙-숄즈', '몬테카를로', '평균'],
                            '확률 (%)': [
                                f"{results['black_scholes_prob']:.2f}",
                                f"{results['monte_carlo_prob']:.2f}",
                                f"{results['average_prob']:.2f}"
                            ]
                        })
                        st.dataframe(prob_df, use_container_width=True, hide_index=True)
                    
                    with col2:
                        st.subheader("예상 수익")
                        payoff_df = pd.DataFrame({
                            '지표': ['평균 페이오프', '중간값 페이오프'],
                            '금액 ($)': [
                                f"${results['expected_payoff']:.2f}",
                                f"${results['median_payoff']:.2f}"
                            ]
                        })
                        st.dataframe(payoff_df, use_container_width=True, hide_index=True)
                    
                    # 가격 분포
                    st.subheader("만기 시 가격 예측 분포")
                    percentiles = [10, 25, 50, 75, 90]
                    price_forecast = pd.DataFrame({
                        '분위수': [f"{p}%" for p in percentiles],
                        '예상 가격 ($)': [f"${np.percentile(analyzer.mc_final_prices, p):.2f}" 
                                       for p in percentiles]
                    })
                    st.dataframe(price_forecast, use_container_width=True, hide_index=True)
                
                with tab2:
                    # 차트 표시
                    fig = analyzer.create_charts()
                    st.pyplot(fig)
                    plt.close()
                
                with tab3:
                    # 상세 정보
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("기본 정보")
                        st.write(f"**티커**: {ticker}")
                        st.write(f"**회사명**: {company_name}")
                        st.write(f"**옵션 타입**: {option_type.upper()}")
                        st.write(f"**현재가**: ${current_price:.2f}")
                        st.write(f"**행사가**: ${strike_price:.2f}")
                        st.write(f"**만기일**: {expiry_date}")
                        st.write(f"**만기까지**: {analyzer.days_to_expiry}일")
                    
                    with col2:
                        st.subheader("시장 지표")
                        st.write(f"**연간 변동성**: {analyzer.annual_volatility*100:.2f}%")
                        st.write(f"**베타**: {beta:.2f}")
                        st.write(f"**필요 변화율**: {analyzer.required_change:+.2f}%")
                        
                        # 내가치/외가치 판단
                        if option_type == 'call':
                            if current_price > strike_price:
                                st.write("**상태**: 🟢 내가치 (ITM)")
                            elif current_price == strike_price:
                                st.write("**상태**: 🟡 등가격 (ATM)")
                            else:
                                st.write("**상태**: 🔴 외가치 (OTM)")
                        else:
                            if current_price < strike_price:
                                st.write("**상태**: 🟢 내가치 (ITM)")
                            elif current_price == strike_price:
                                st.write("**상태**: 🟡 등가격 (ATM)")
                            else:
                                st.write("**상태**: 🔴 외가치 (OTM)")
                
            except Exception as e:
                st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
    
    else:
        # 초기 화면 안내
        st.info("👈 왼쪽 사이드바에서 옵션 정보를 입력하고 '분석 시작' 버튼을 클릭하세요.")
        
        # 사용 예시
        st.subheader("📚 사용 방법")
        st.markdown("""
        1. **티커 심볼** 입력 (예: TSLA, AAPL, NVDA)
        2. **옵션 타입** 선택 (Call 또는 Put)
        3. **현재가**와 **행사가** 입력
        4. **만기일** 선택
        5. 필요시 **변동성**과 **베타** 조정
        6. **분석 시작** 버튼 클릭
        
        ### 🎯 분석 내용
        - 블랙-숄즈 모델을 이용한 이론적 확률
        - 몬테카를로 시뮬레이션을 통한 실증적 확률
        - 만기 시 가격 분포 예측
        - 예상 수익 계산
        - 시각화 차트
        
        ### ⚠️ 주의사항
        본 프로그램은 교육 및 분석 목적으로만 사용되며, 투자 권유나 추천이 아닙니다.
        모든 투자 결정은 본인의 책임입니다.
        """)

if __name__ == "__main__":
    main()
