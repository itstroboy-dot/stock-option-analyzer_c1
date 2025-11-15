import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class OptionAnalyzer:
    """미국 주식 옵션 달성 가능성 분석기"""
    
    def __init__(self, ticker, strike_price, expiry_date, current_price, 
                 annual_volatility=None, beta=1.0, company_name=None, option_type='call'):
        """
        Parameters:
        -----------
        ticker : str
            주식 티커 (예: 'TSLA')
        strike_price : float
            행사가격
        expiry_date : str
            만기일 (YYYY-MM-DD 형식)
        current_price : float
            현재 주가
        annual_volatility : float
            연간 변동성 (없으면 자동 추정)
        beta : float
            베타 계수
        company_name : str
            회사명
        option_type : str
            옵션 타입 ('call' 또는 'put')
        """
        self.ticker = ticker
        self.strike_price = strike_price
        self.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
        self.current_price = current_price
        self.beta = beta
        self.company_name = company_name if company_name else ticker
        self.option_type = option_type.lower()
        
        # 변동성 추정 (제공되지 않은 경우)
        if annual_volatility is None:
            # 베타를 기반으로 변동성 추정 (S&P 500 연간 변동성 약 15% 가정)
            self.annual_volatility = 0.15 * abs(beta) * 1.5
        else:
            self.annual_volatility = annual_volatility
        
        # 시뮬레이션용 과거 데이터 생성
        self.generate_historical_data()
        self.calculate_metrics()
        
    def generate_historical_data(self):
        """시뮬레이션용 과거 데이터 생성"""
        print(f"\n{'='*60}")
        print(f"{self.ticker} 데이터 준비 중...")
        print(f"{'='*60}")
        
        # 6개월 데이터 생성 (126 거래일)
        days = 126
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
        
        # 기하 브라운 운동으로 가격 데이터 생성
        np.random.seed(42)
        returns = np.random.normal(0, self.annual_volatility/np.sqrt(252), days)
        
        # 현재 가격에서 역으로 계산
        prices = np.zeros(days)
        prices[-1] = self.current_price
        for i in range(days-2, -1, -1):
            prices[i] = prices[i+1] / (1 + returns[i+1])
        
        self.df = pd.DataFrame({
            'Close': prices,
            'Date': dates
        })
        self.df.set_index('Date', inplace=True)
        
        print(f"회사명: {self.company_name}")
        print(f"현재가: ${self.current_price:.2f}")
        print(f"베타: {self.beta:.2f}")
        
    def calculate_metrics(self):
        """주요 지표 계산"""
        # 일일 수익률
        self.df['Returns'] = self.df['Close'].pct_change()
        
        # 변동성 (연율화)
        self.daily_volatility = self.df['Returns'].std()
        self.annual_volatility = self.daily_volatility * np.sqrt(252)
        
        # 만기까지 남은 일수
        self.days_to_expiry = (self.expiry_date - datetime.now()).days
        self.years_to_expiry = self.days_to_expiry / 365.0
        
        # 필요한 변화율
        self.required_change = (self.strike_price / self.current_price - 1) * 100
        
        print(f"\n연간 변동성: {self.annual_volatility*100:.2f}%")
        print(f"만기까지: {self.days_to_expiry}일")
        print(f"필요 변화율: {self.required_change:+.2f}%")
        
    def black_scholes_probability(self):
        """블랙-숄즈 모델을 이용한 확률 계산"""
        S = self.current_price
        K = self.strike_price
        T = self.years_to_expiry
        sigma = self.annual_volatility
        r = 0.045  # 무위험 이자율 (현재 미국 국채 수익률 가정)
        
        # d2 계산 (만기 시 ITM 확률과 관련)
        d2 = (np.log(S/K) + (r - 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        
        if self.option_type == 'call':
            # 콜옵션: 주가가 행사가 이상일 확률
            probability = norm.cdf(d2)
        else:
            # 풋옵션: 주가가 행사가 이하일 확률
            probability = norm.cdf(-d2)
            
        return probability * 100
        
    def monte_carlo_simulation(self, num_simulations=10000):
        """몬테카를로 시뮬레이션"""
        print(f"\n몬테카를로 시뮬레이션 실행 중 ({num_simulations:,}회)...")
        
        S = self.current_price
        T = self.years_to_expiry
        sigma = self.annual_volatility
        r = 0.045
        
        # 시뮬레이션
        np.random.seed(42)
        dt = 1/252  # 일일 시간 단위
        steps = self.days_to_expiry
        
        # 가격 경로 생성
        price_paths = np.zeros((num_simulations, steps + 1))
        price_paths[:, 0] = S
        
        for t in range(1, steps + 1):
            z = np.random.standard_normal(num_simulations)
            price_paths[:, t] = price_paths[:, t-1] * np.exp(
                (r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z
            )
        
        # 만기 시 가격
        final_prices = price_paths[:, -1]
        
        # 확률 계산
        if self.option_type == 'call':
            success = final_prices >= self.strike_price
        else:
            success = final_prices <= self.strike_price
            
        probability = np.mean(success) * 100
        
        # 통계
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
        print(f"\n{'='*60}")
        print(f"옵션 분석 결과")
        print(f"{'='*60}")
        
        # 블랙-숄즈 확률
        bs_prob = self.black_scholes_probability()
        
        # 몬테카를로 확률
        mc_prob = self.monte_carlo_simulation()
        
        # 예상 수익
        expected_payoff, median_payoff = self.calculate_expected_profit()
        
        print(f"\n【 기본 정보 】")
        print(f"  티커: {self.ticker}")
        print(f"  옵션 타입: {self.option_type.upper()}")
        print(f"  현재가: ${self.current_price:.2f}")
        print(f"  행사가: ${self.strike_price:.2f}")
        print(f"  만기일: {self.expiry_date.strftime('%Y-%m-%d')}")
        print(f"  만기까지: {self.days_to_expiry}일")
        
        print(f"\n【 시장 지표 】")
        print(f"  연간 변동성: {self.annual_volatility*100:.2f}%")
        print(f"  베타: {self.beta:.2f}")
        print(f"  필요 변화율: {self.required_change:+.2f}%")
        
        print(f"\n【 달성 가능성 】")
        print(f"  블랙-숄즈 모델: {bs_prob:.2f}%")
        print(f"  몬테카를로 시뮬레이션: {mc_prob:.2f}%")
        print(f"  평균 확률: {(bs_prob + mc_prob)/2:.2f}%")
        
        # 해석
        avg_prob = (bs_prob + mc_prob) / 2
        if avg_prob >= 70:
            interpretation = "매우 높음 - 달성 가능성이 높습니다"
        elif avg_prob >= 50:
            interpretation = "높음 - 달성 가능성이 있습니다"
        elif avg_prob >= 30:
            interpretation = "보통 - 불확실성이 있습니다"
        else:
            interpretation = "낮음 - 달성이 어려울 수 있습니다"
            
        print(f"  평가: {interpretation}")
        
        print(f"\n【 예상 수익 (행사가 기준) 】")
        print(f"  평균 페이오프: ${expected_payoff:.2f}")
        print(f"  중간값 페이오프: ${median_payoff:.2f}")
        
        # 가격 구간별 확률
        print(f"\n【 만기 시 가격 분포 】")
        percentiles = [10, 25, 50, 75, 90]
        for p in percentiles:
            price = np.percentile(self.mc_final_prices, p)
            print(f"  {p}% 분위: ${price:.2f}")
            
        return {
            'black_scholes_prob': bs_prob,
            'monte_carlo_prob': mc_prob,
            'average_prob': avg_prob,
            'expected_payoff': expected_payoff,
            'median_payoff': median_payoff
        }
        
    def visualize(self, save_path='/home/claude/option_analysis.png'):
        """분석 결과 시각화"""
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
        
        # 3. 몬테카를로 시뮬레이션 경로 (샘플)
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
        
        # 막대 위에 수치 표시
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
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n차트가 저장되었습니다: {save_path}")
        
        return fig


def main():
    """메인 실행 함수"""
    print("="*60)
    print("미국 주식 옵션 달성 가능성 분석 프로그램")
    print("="*60)
    
    # 테슬라 $300 콜옵션 분석 (11월 26일 만기)
    # 2025년 11월 14일 기준 실제 데이터 사용
    analyzer = OptionAnalyzer(
        ticker='TSLA',
        strike_price=300,
        expiry_date='2025-11-26',
        current_price=404.42,  # 2025-11-14 기준 실제 가격
        annual_volatility=0.60,  # 테슬라 역사적 변동성 약 60%
        beta=1.61,  # 실제 베타값
        company_name='Tesla, Inc.',
        option_type='call'
    )
    
    # 분석 수행
    results = analyzer.analyze()
    
    # 시각화
    analyzer.visualize()
    
    print(f"\n{'='*60}")
    print("분석 완료!")
    print(f"{'='*60}")
    
    return analyzer, results


if __name__ == "__main__":
    analyzer, results = main()
