import pandas as pd
from pykrx import stock
import matplotlib.pyplot as plt

# 1. 데이터 불러오기
# 삼성전자 티커: 005930
ticker = "005930"
start_date = "2023-01-01"
end_date = "2023-12-31"

# 데이터 불러오기
df = stock.get_market_ohlcv(start_date, end_date, ticker)

# 2. 변동성 돌파 전략 적용
# 전일 고가와 저가의 차이를 이용하여 변동성을 계산하고, 이를 통해 매수 기준 가격을 설정합니다.
df['volatility'] = df['고가'] - df['저가']
df['buy_price'] = df['시가'] + df['volatility'].shift(1) * 0.5  # K값은 0.5로 설정

# 매수 조건: 당일 시가가 매수기준가보다 높을 때
df['buy_signal'] = df['시가'] > df['buy_price']

# 3. 백테스팅
initial_balance = 1000000  # 초기 자본금 1백만원
balance = initial_balance
num_shares = 0
df['balance'] = 0  # 잔고 기록
df['portfolio_value'] = 0  # 포트폴리오 가치 기록
df['daily_return'] = 0  # 일별 수익률 기록

for i in range(1, len(df)):
    if df['buy_signal'].iloc[i]:  # 매수 조건 충족 시
        num_shares = balance // df['시가'].iloc[i]  # 매수할 주식 수
        balance -= num_shares * df['시가'].iloc[i]  # 매수 후 남은 현금
        daily_profit = num_shares * (df['종가'].iloc[i] - df['시가'].iloc[i])  # 당일 매수 후 매도 수익
        df.at[df.index[i], 'daily_return'] = daily_profit / initial_balance  # 일별 수익률 기록
        balance += daily_profit  # 잔고 업데이트
    df.at[df.index[i], 'balance'] = balance
    df.at[df.index[i], 'portfolio_value'] = balance + num_shares * df['종가'].iloc[i]

final_balance = balance
profit = final_balance - initial_balance
print(f"Final Balance: {final_balance:.2f} KRW")
print(f"Profit: {profit:.2f} KRW")

# 4. 결과 시각화
plt.figure(figsize=(14, 7))

# 시가와 종가를 시각화
plt.plot(df.index, df['종가'], label='Close Price', color='blue')

# 매수 신호 시각화
plt.scatter(df.index[df['buy_signal']], df['종가'][df['buy_signal']], marker='^', color='green', label='Buy Signal')

# 일별 수익률 막대 그래프
plt.bar(df.index, df['daily_return'], label='Daily Return', color='orange', alpha=0.5)

plt.xlabel('Date')
plt.ylabel('Price / Daily Return')
plt.title('Volatility Breakout Strategy Backtesting Result')
plt.legend()
plt.grid()
plt.show()
