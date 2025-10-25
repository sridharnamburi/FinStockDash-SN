import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Indian Stock Analysis", page_icon="📈", layout="wide")

# Title
st.title("📈 Indian Stock Market Analysis")

# Sidebar - Stock Selection
st.sidebar.header("📊 Stock Selection")

popular_stocks = {
    'Reliance Industries': 'RELIANCE.NS',
    'Tata Consultancy Services': 'TCS.NS',
    'Infosys': 'INFY.NS',
    'HDFC Bank': 'HDFCBANK.NS',
    'ITC Limited': 'ITC.NS',
    'ICICI Bank': 'ICICIBANK.NS',
    'State Bank of India': 'SBIN.NS',
    'Bharti Airtel': 'BHARTIARTL.NS',
    'Wipro': 'WIPRO.NS',
    'Hindustan Unilever': 'HINDUNILVR.NS'
}

# Selection method
selection_method = st.sidebar.radio("Choose method:", ["Popular Stocks", "Enter Custom"])

if selection_method == "Popular Stocks":
    selected_company = st.sidebar.selectbox('Select Company:', list(popular_stocks.keys()))
    ticker = popular_stocks[selected_company]
else:
    ticker = st.sidebar.text_input("Enter NSE ticker:", "RELIANCE.NS")
    st.sidebar.caption("Format: SYMBOL.NS (e.g., TCS.NS)")

# Period selection
period = st.sidebar.selectbox('Time Period:', ['1mo', '3mo', '6mo', '1y', '2y', '5y'])

# Fetch button
if st.sidebar.button("🔍 Analyze Stock", type="primary"):
    st.session_state.fetch_data = True

# Main content
if 'fetch_data' in st.session_state and st.session_state.fetch_data:
    with st.spinner(f'Fetching data for {ticker}...'):
        try:
            # Fetch data
            df = yf.download(ticker, period=period, progress=False)
            
            if df.empty:
                st.error(f"❌ No data found for {ticker}")
                st.info("💡 Make sure to use .NS suffix for NSE stocks (e.g., TCS.NS)")
                st.stop()
            
            # Success message
            st.success(f"✅ Loaded data for {ticker}")
            
            # Current metrics
            current_price = df['Close'][-1]
            prev_close = df['Close'][-2]
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Current Price", f"₹{current_price:.2f}", 
                         f"{change:+.2f} ({change_pct:+.2f}%)")
            with col2:
                st.metric("📈 Day High", f"₹{df['High'][-1]:.2f}")
            with col3:
                st.metric("📉 Day Low", f"₹{df['Low'][-1]:.2f}")
            with col4:
                st.metric("📊 Volume", f"{df['Volume'][-1]:,.0f}")
            
            # Candlestick chart
            st.subheader("📊 Price Chart")
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=ticker
            )])
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                height=500,
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            st.subheader("📊 Trading Volume")
            fig_vol = go.Figure([go.Bar(x=df.index, y=df['Volume'], name='Volume')])
            fig_vol.update_layout(height=300)
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # Technical Indicators
            st.subheader("📈 Technical Indicators")
            
            # Calculate indicators
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            
            # RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("MA 20", f"₹{df['MA20'][-1]:.2f}")
            with col2:
                st.metric("MA 50", f"₹{df['MA50'][-1]:.2f}")
            with col3:
                rsi_val = df['RSI'][-1]
                rsi_signal = "🔴 Overbought" if rsi_val > 70 else "🟢 Oversold" if rsi_val < 30 else "🟡 Neutral"
                st.metric("RSI (14)", f"{rsi_val:.2f}", rsi_signal)
            
            # Recent data table
            st.subheader("📋 Recent Trading Data")
            st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please check the ticker symbol and try again")

else:
    st.info("👈 Select a stock from the sidebar and click 'Analyze Stock'")
    
    # Show examples
    st.subheader("✨ Popular Indian Stocks")
    
    cols = st.columns(5)
    example_stocks = [
        ('RELIANCE.NS', '🏭 Reliance'),
        ('TCS.NS', '💻 TCS'),
        ('INFY.NS', '🌐 Infosys'),
        ('HDFCBANK.NS', '🏦 HDFC Bank'),
        ('ITC.NS', '🚬 ITC')
    ]
    
    for idx, (ticker_ex, name) in enumerate(example_stocks):
        with cols[idx]:
            st.info(f"**{name}**\n`{ticker_ex}`")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("💡 NSE stocks: Add .NS suffix")
st.sidebar.caption("💡 BSE stocks: Add .BO suffix")
