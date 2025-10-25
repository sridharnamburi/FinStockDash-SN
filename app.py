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
    st.session_state.current_ticker = ticker
    st.session_state.current_period = period

# Main content
if 'fetch_data' in st.session_state and st.session_state.fetch_data:
    ticker = st.session_state.get('current_ticker', ticker)
    period = st.session_state.get('current_period', period)
    
    with st.spinner(f'Fetching data for {ticker}...'):
        try:
            # Fetch data
            df = yf.download(ticker, period=period, progress=False)
            
            # Check if data is empty
            if df is None or df.empty or len(df) == 0:
                st.error(f"❌ No data found for {ticker}")
                st.info("💡 Make sure to use .NS suffix for NSE stocks (e.g., TCS.NS)")
                st.stop()
            
            # Ensure we have at least 2 data points
            if len(df) < 2:
                st.error(f"❌ Insufficient data for {ticker}")
                st.stop()
            
            # Success message
            st.success(f"✅ Loaded {len(df)} days of data for {ticker}")
            
            # Safe data extraction with error handling
            try:
                # Get the latest values safely
                current_price = float(df['Close'].iloc[-1])
                prev_close = float(df['Close'].iloc[-2])
                day_high = float(df['High'].iloc[-1])
                day_low = float(df['Low'].iloc[-1])
                volume = int(df['Volume'].iloc[-1])
                
                # Calculate change
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
            except (IndexError, KeyError, ValueError) as e:
                st.error(f"❌ Error processing data: {str(e)}")
                st.write("Data structure:")
                st.write(df.head())
                st.stop()
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Current Price", f"₹{current_price:.2f}", 
                         f"{change:+.2f} ({change_pct:+.2f}%)")
            with col2:
                st.metric("📈 Day High", f"₹{day_high:.2f}")
            with col3:
                st.metric("📉 Day Low", f"₹{day_low:.2f}")
            with col4:
                st.metric("📊 Volume", f"{volume:,}")
            
            # Price Chart
st.subheader("📊 Price Chart")

try:
    # Create candlestick chart
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker,
        increasing_line_color='green',
        decreasing_line_color='red'
    ))
    
    # Update layout with explicit settings
    fig.update_layout(
        title=f'{ticker} Price Movement',
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        height=500,
        width=None,
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=True
    )
    
    # Display with specific config
    st.plotly_chart(
        fig, 
        use_container_width=True,
        config={'displayModeBar': True, 'displaylogo': False}
    )
    
except Exception as e:
    st.error(f"Chart error: {str(e)}")
    
    # Fallback: Simple line chart
    st.subheader("📈 Closing Price (Line Chart)")
    st.line_chart(df['Close'])

            
            # Volume chart
            st.subheader("📊 Trading Volume")
            try:
                fig_vol = go.Figure([go.Bar(x=df.index, y=df['Volume'], name='Volume')])
                fig_vol.update_layout(
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="Volume"
                )
                st.plotly_chart(fig_vol, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create volume chart: {e}")
            
            # Technical Indicators
            st.subheader("📈 Technical Indicators")
            
            try:
                # Calculate indicators with proper error handling
                if len(df) >= 20:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    ma20_value = df['MA20'].iloc[-1]
                else:
                    ma20_value = None
                
                if len(df) >= 50:
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                    ma50_value = df['MA50'].iloc[-1]
                else:
                    ma50_value = None
                
                # RSI Calculation
                if len(df) >= 14:
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    rsi_val = df['RSI'].iloc[-1]
                else:
                    rsi_val = None
                
                # Display indicators
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if ma20_value:
                        st.metric("MA 20", f"₹{ma20_value:.2f}")
                    else:
                        st.info("MA 20: Insufficient data")
                
                with col2:
                    if ma50_value:
                        st.metric("MA 50", f"₹{ma50_value:.2f}")
                    else:
                        st.info("MA 50: Insufficient data")
                
                with col3:
                    if rsi_val:
                        rsi_signal = "🔴 Overbought" if rsi_val > 70 else "🟢 Oversold" if rsi_val < 30 else "🟡 Neutral"
                        st.metric("RSI (14)", f"{rsi_val:.2f}", rsi_signal)
                    else:
                        st.info("RSI: Insufficient data")
                
            except Exception as e:
                st.warning(f"Could not calculate technical indicators: {e}")
            
            # Recent data table
            st.subheader("📋 Recent Trading Data")
            try:
                # Format the dataframe for display
                display_df = df.tail(10).copy()
                display_df = display_df.sort_index(ascending=False)
                
                # Round numerical columns
                for col in ['Open', 'High', 'Low', 'Close']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].round(2)
                
                st.dataframe(display_df, use_container_width=True)
                
            except Exception as e:
                st.warning(f"Could not display recent data: {e}")
            
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.info("Please try again or select a different stock")
            
            # Debug info
            with st.expander("Debug Information"):
                st.write(f"Ticker: {ticker}")
                st.write(f"Period: {period}")
                st.write(f"Error type: {type(e).__name__}")

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
st.sidebar.caption("📊 Data source: Yahoo Finance")

