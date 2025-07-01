
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import ta

st.set_page_config(page_title="Buy Low, Sell High - Trading Strategy Dashboard")

st.title("📉 Buy Low, Sell High - Trading Strategy Dashboard")

# Input section
ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

def run_strategy(ticker):
    df = load_data(ticker, start_date, end_date)
    if df.empty:
        return df, None, None

    # Fix: Ensure 'close' is 1D
    df["sma20"] = ta.trend.SMAIndicator(close=df["Close"].squeeze(), window=20).sma_indicator()
    df["sma50"] = ta.trend.SMAIndicator(close=df["Close"].squeeze(), window=50).sma_indicator()

    # Buy/Sell signals
    buy_signals = (df["sma20"] > df["sma50"]) & (df["sma20"].shift(1) <= df["sma50"].shift(1))
    sell_signals = (df["sma20"] < df["sma50"]) & (df["sma20"].shift(1) >= df["sma50"].shift(1))

    df["Signal"] = 0
    df.loc[buy_signals, "Signal"] = 1
    df.loc[sell_signals, "Signal"] = -1

    trades = df[df["Signal"] != 0]

    return df, df.describe(), trades

if ticker:
    df, stats, trades = run_strategy(ticker)

    if df is not None and not df.empty:
        # Plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
        fig.add_trace(go.Scatter(x=df.index, y=df["sma20"], mode="lines", name="SMA20"))
        fig.add_trace(go.Scatter(x=df.index, y=df["sma50"], mode="lines", name="SMA50"))

        buy_signals = df[df["Signal"] == 1]
        sell_signals = df[df["Signal"] == -1]

        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals["Close"],
                                 mode="markers", name="Buy", marker=dict(symbol="triangle-up", color="green", size=10)))
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals["Close"],
                                 mode="markers", name="Sell", marker=dict(symbol="triangle-down", color="red", size=10)))

        st.plotly_chart(fig)

        st.subheader("📊 Stats Summary")
        st.write(stats)

        st.subheader("🪙 Trades")
        st.write(trades)
    else:
        st.warning(f"No data available for {ticker}. Please check the symbol or date range.")
