# 📊 US Stock Option Probability Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**미국 주식 옵션의 달성 가능성을 분석하는 웹 애플리케이션**

[English](#english) | [한국어](#korean)

</div>

---

## <a name="korean"></a>🇰🇷 한국어

### 📌 프로젝트 소개

미국 주식 옵션의 만기 시 달성 가능성을 **블랙-숄즈 모델**과 **몬테카를로 시뮬레이션**으로 분석하는 웹 기반 도구입니다. 투자자들이 데이터 기반의 객관적인 의사결정을 할 수 있도록 돕습니다.

### ✨ 주요 기능

- 🎯 **블랙-숄즈 모델**: 옵션 가격 결정의 표준 모델을 사용한 이론적 확률 계산
- 🎲 **몬테카를로 시뮬레이션**: 10,000회 시뮬레이션을 통한 실증적 확률 추정
- 📊 **시각화**: 6가지 차트로 분석 결과를 직관적으로 표시
- 💰 **수익 예측**: 예상 페이오프 및 가격 분포 계산
- 🌐 **웹 인터페이스**: Streamlit 기반의 사용하기 쉬운 UI
- 📈 **실시간 분석**: 입력 즉시 분석 결과 확인

### 🚀 빠른 시작

#### 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/yourusername/option-analyzer.git
cd option-analyzer

# 필요한 패키지 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

#### Streamlit Cloud 배포

1. GitHub 저장소 생성 및 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. 'New app' 클릭
4. GitHub 저장소 연결
5. `app.py` 파일 선택 후 Deploy

### 📖 사용 방법

1. **사이드바에서 옵션 정보 입력**
   - 티커 심볼 (예: TSLA, AAPL, NVDA)
   - 옵션 타입 (Call 또는 Put)
   - 현재가 및 행사가
   - 만기일

2. **시장 지표 설정 (선택)**
   - 연간 변동성
   - 베타 계수

3. **'분석 시작' 버튼 클릭**

4. **결과 확인**
   - 달성 가능성 확률
   - 예상 수익
   - 가격 분포 예측
   - 시각화 차트

### 📊 분석 예시

**테슬라 $300 콜옵션 (2025-11-26 만기)**

```
현재가: $404.42
행사가: $300.00
달성 가능성: 99.70%
상태: 내가치 (ITM)
예상 페이오프: $105.36
```

### 📂 프로젝트 구조

```
option-analyzer/
├── app.py                 # Streamlit 웹 앱
├── option_analyzer.py     # 핵심 분석 로직 (CLI 버전)
├── requirements.txt       # 의존성 패키지
├── README.md             # 프로젝트 문서
├── .gitignore            # Git 제외 파일
└── docs/                 # 추가 문서
    └── 사용가이드.md      # 상세 사용 설명서
```

### 🛠️ 기술 스택

- **Python 3.8+**
- **Streamlit**: 웹 인터페이스
- **NumPy & Pandas**: 데이터 처리
- **Matplotlib**: 시각화
- **SciPy**: 통계 계산

### 📈 분석 방법론

#### 1. 블랙-숄즈 모델
- 옵션 가격 결정의 표준 이론 모델
- 정규분포 가정 하에서 확률 계산
- d₂ 값을 이용한 만기 시 ITM 확률 산출

#### 2. 몬테카를로 시뮬레이션
- 기하 브라운 운동(GBM) 모델 사용
- 10,000개의 가격 경로 생성
- 실증적 확률 분포 추정

### ⚠️ 면책 조항

본 프로그램은 **교육 및 분석 목적**으로만 제공됩니다.
- 투자 권유나 추천이 아닙니다
- 과거 데이터와 통계 모델에 기반한 추정치입니다
- 실제 시장 결과는 예측과 다를 수 있습니다
- **모든 투자 결정은 본인의 책임**입니다

### 🤝 기여하기

기여를 환영합니다! Pull Request를 보내주세요.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📝 라이센스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

### 📧 연락처

프로젝트 링크: [https://github.com/yourusername/option-analyzer](https://github.com/yourusername/option-analyzer)

---

## <a name="english"></a>🇺🇸 English

### 📌 Project Overview

A web-based tool that analyzes the probability of achieving US stock option targets at expiration using **Black-Scholes Model** and **Monte Carlo Simulation**. Helps investors make data-driven, objective decisions.

### ✨ Key Features

- 🎯 **Black-Scholes Model**: Theoretical probability calculation using the standard option pricing model
- 🎲 **Monte Carlo Simulation**: Empirical probability estimation through 10,000 simulations
- 📊 **Visualization**: Intuitive display of analysis results with 6 different charts
- 💰 **Profit Forecasting**: Calculate expected payoff and price distribution
- 🌐 **Web Interface**: Easy-to-use UI powered by Streamlit
- 📈 **Real-time Analysis**: Instant analysis results upon input

### 🚀 Quick Start

#### Local Execution

```bash
# Clone repository
git clone https://github.com/yourusername/option-analyzer.git
cd option-analyzer

# Install required packages
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

Access `http://localhost:8501` in your browser

#### Streamlit Cloud Deployment

1. Create GitHub repository and push code
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Click 'New app'
4. Connect GitHub repository
5. Select `app.py` file and Deploy

### 📖 How to Use

1. **Enter option information in sidebar**
   - Ticker symbol (e.g., TSLA, AAPL, NVDA)
   - Option type (Call or Put)
   - Current price and strike price
   - Expiration date

2. **Set market indicators (optional)**
   - Annual volatility
   - Beta coefficient

3. **Click 'Analyze' button**

4. **Check results**
   - Probability of success
   - Expected profit
   - Price distribution forecast
   - Visualization charts

### 📊 Analysis Example

**Tesla $300 Call Option (Expiring 2025-11-26)**

```
Current Price: $404.42
Strike Price: $300.00
Success Probability: 99.70%
Status: In-The-Money (ITM)
Expected Payoff: $105.36
```

### 📂 Project Structure

```
option-analyzer/
├── app.py                 # Streamlit web app
├── option_analyzer.py     # Core analysis logic (CLI version)
├── requirements.txt       # Dependencies
├── README.md             # Project documentation
├── .gitignore            # Git exclude files
└── docs/                 # Additional documentation
    └── 사용가이드.md      # Detailed user guide
```

### 🛠️ Technology Stack

- **Python 3.8+**
- **Streamlit**: Web interface
- **NumPy & Pandas**: Data processing
- **Matplotlib**: Visualization
- **SciPy**: Statistical calculations

### 📈 Methodology

#### 1. Black-Scholes Model
- Standard theoretical model for option pricing
- Probability calculation under normal distribution assumption
- ITM probability at expiration using d₂ value

#### 2. Monte Carlo Simulation
- Uses Geometric Brownian Motion (GBM) model
- Generates 10,000 price paths
- Estimates empirical probability distribution

### ⚠️ Disclaimer

This program is provided for **educational and analytical purposes only**.
- Not investment advice or recommendation
- Estimates based on historical data and statistical models
- Actual market results may differ from predictions
- **All investment decisions are your own responsibility**

### 🤝 Contributing

Contributions are welcome! Please send Pull Requests.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

### 📧 Contact

Project Link: [https://github.com/yourusername/option-analyzer](https://github.com/yourusername/option-analyzer)

---

<div align="center">

**Made with ❤️ for Options Traders**

⭐ Star this repository if you find it helpful!

</div>
