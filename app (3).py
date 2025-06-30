
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.title("📈 Buy Low, Sell High - Trading Strategy Dashboard")

ticker_list = st.multiselect("Choose stock symbols:", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"], default=["AAPL", "MSFT"])
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

CASH = 10000
POSITION_SIZE = 1

def run_strategy(ticker):
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d")

    if df.empty or 'Close' not in df.columns:
        st.warning(f"No data available for {ticker}. Please check the symbol or date range.")
        return None, None, None

    df.dropna(inplace=True)
    df['sma20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    df['shares'] = 0
    df['cash'] = CASH
    df['portfolio'] = CASH

    in_position = False
    entry_price = 0
    trades = []

    for i in range(20, len(df)):
        price = df.iloc[i]['Close']
        rsi = df.iloc[i]['rsi']
        sma20 = df.iloc[i]['sma20']

        if not in_position and rsi < 30 and price < sma20:
            in_position = True
            entry_price = price
            df.at[df.index[i], 'shares'] = POSITION_SIZE
            df.at[df.index[i], 'cash'] -= POSITION_SIZE * price
            trades.append(('BUY', df.index[i], price))

        elif in_position and (rsi > 70 or price > sma20):
            in_position = False
            df.at[df.index[i], 'cash'] += POSITION_SIZE * price
            df.at[df.index[i], 'shares'] = 0
            trades.append(('SELL', df.index[i], price))

        df.at[df.index[i], 'portfolio'] = df.at[df.index[i], 'cash'] + df.at[df.index[i], 'shares'] * price

    return df, df['portfolio'].iloc[-1] - CASH, trades

for ticker in ticker_list:
    st.subheader(ticker)
    df, profit, trades = run_strategy(ticker)

    if df is not None:
        st.line_chart(df[['Close', 'sma20']])
        st.line_chart(df['portfolio'])
        st.metric(label="Net Profit ($)", value=f"{profit:.2f}")
        st.write("Trade Log:")
        st.write(trades)
