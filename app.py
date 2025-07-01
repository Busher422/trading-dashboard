
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import ta

st.set_page_config(page_title="Buy Low, Sell High", layout="wide")

st.title("📉 Buy Low, Sell High - Trading Strategy Dashboard")

def load_data(ticker):
    df = yf.download(ticker, period="1mo", interval="1d")
    df.dropna(inplace=True)
    return df

def run_strategy(ticker):
    df = load_data(ticker)
    df["sma20"] = ta.trend.SMAIndicator(close=df["Close"], window=20).sma_indicator().iloc[:, 0]
    df["sma50"] = ta.trend.SMAIndicator(close=df["Close"], window=50).sma_indicator().iloc[:, 0]

    df["Signal"] = 0
    df.loc[df["sma20"] > df["sma50"], "Signal"] = 1
    df.loc[df["sma20"] < df["sma50"], "Signal"] = -1

    stats = df.describe()
    trades = df[df["Signal"].diff() != 0]

    return df, stats, trades

try:
    ticker = st.text_input("Enter Stock Symbol", "AAPL")

    if ticker:
        df, stats, trades = run_strategy(ticker)

        st.subheader("📊 Stats Summary")
        st.dataframe(stats)

        st.subheader("📈 Trades")
        st.dataframe(trades)

        st.subheader("📉 Price Chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
        fig.add_trace(go.Scatter(x=df.index, y=df["sma20"], mode="lines", name="SMA 20"))
        fig.add_trace(go.Scatter(x=df.index, y=df["sma50"], mode="lines", name="SMA 50"))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
