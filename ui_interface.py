import streamlit as st
from quant_agent import quant_agent

# Set Page Config
st.set_page_config(page_title="Market Regime Detector AI", layout="wide")

# Custom CSS for "The Matrix" / Terminal feel (optional)
st.markdown("""
<style>
    .stAlert { border-radius: 4px; }
    h1 { color: #00e676; font-family: 'Courier New'; }
    .metric-card { background-color: #1e1e1e; padding: 15px; border-radius: 8px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Agent For Market Regime Detector")
st.caption("Powered by LangGraph, Llama 3, and Yahoo Finance")

# Sidebar for Input
with st.sidebar:
    st.header("Configuration")
    ticker_input = st.text_input("Enter Ticker Symbol", value="NVDA", help="e.g., AAPL, NVDA, BTC-USD")
    run_btn = st.button("🚀 Run Analysis", type="primary")
    st.info("Agent Workflow:\n1. Fetch Data\n2. Classify Regime\n3. Draft Strategy\n4. Risk Review\n5. Final Decision")

if run_btn:
    if not ticker_input:
        st.warning("Please enter a valid ticker.")
    else:
        try:
            with st.status("🤖 AI Agents at work...", expanded=True) as status:
                st.write("📊 Fetching market data...")
                # We call the backend here
                result = quant_agent(ticker_input)
                
                st.write("🧠 Classifying Market Regime...")
                st.write("💡 Drafting Initial Strategy...")
                st.write("🛡️ Risk Manager Critiquing...")
                st.write("✅ Finalizing Decision...")
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            # --- DISPLAY RESULTS ---
            
            # 1. Market Data Overview
            st.subheader(f"1. Technical Snapshot: {ticker_input.upper()}")
            
            # Parse the market_data string roughly to display metrics nicely
            data_str = result['market_data']
            if "Error" in data_str:
                st.error(data_str)
            else:
                # Parse lines based on the fixed format in backend.py
                lines = data_str.split('\n')
                
                # Extract values safely (stripping whitespace)
                # Format: "Label: Value" -> split by ": " -> get index 1
                price = lines[1].split(': ')[1]
                sma_50 = lines[2].split(': ')[1]
                sma_200 = lines[3].split(': ')[1]
                volatility = lines[4].split(': ')[1]
                daily_return = lines[5].split(': ')[1]

                # Create a 3-column grid for the first row of metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Current Price", value=price)
                with col2:
                    st.metric(label="50-Day SMA", value=sma_50)
                with col3:
                    st.metric(label="200-Day SMA", value=sma_200)

                # Create a 2-column grid for the second row
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric(label="Volatility (Annualized)", value=volatility)
                with col5:
                    st.metric(label="Daily Return", value=daily_return)
                with col6:
                    st.metric(label="", value="") 
                    
                with st.expander("View Raw Technical Data"):
                    st.text(result['market_data'])

            # 2. Market Regime
            st.divider()
            st.subheader("2. Market Regime Detection")
            st.info(result['regime'], icon="🧐")

            # 3. Strategy & Reflection (Side by Side)
            st.divider()
            col_strat, col_risk = st.columns(2)
            
            with col_strat:
                st.subheader("3. Initial Strategy")
                st.markdown(f"_{result['initial_strategy']}_")
            
            with col_risk:
                st.subheader("4. Risk Critique")
                st.warning(result['reflection'], icon="⚠️")

            # 4. Final Decision
            st.divider()
            st.subheader("5. CIO Final Verdict")
            st.success(result['final_decision'], icon="🏆")

        except Exception as e:
            st.error(f"An error occurred: {e}")