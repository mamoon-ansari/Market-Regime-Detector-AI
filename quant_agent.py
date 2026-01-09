import os
import datetime
import yfinance as yf
import pandas as pd
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

load_dotenv()

# --- CONFIGURATION ---
llm = ChatGroq(model_name="llama-3.1-8b-instant") # Using 70b for better reasoning

# --- 1. STATE DEFINITION ---
class QuantState(TypedDict):
    ticker: str
    market_data: str      # Summary of prices/indicators
    regime: str           # e.g., "High Volatility Bear"
    initial_strategy: str # The first draft plan
    reflection: str       # The risk manager's critique
    final_decision: str   # The adjusted strategy

# --- 2. TECHNICAL ANALYSIS ENGINE (Pure Python) ---
def get_market_analysis(ticker: str) -> str:
    """Fetches data and calculates SMA, RSI, and Volatility"""
    print(f"📊 Fetching data for {ticker}...")
    try:
        # FIX 1: Fetch '1y' or 'max' to get enough data for 200 SMA
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        
        if df.empty:
            return "Error: No data found."

        # FIX 2: Handle MultiIndex columns (common in new yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df = df.xs(ticker, level=1, axis=1)

        # Calculate Indicators
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        df['Returns'] = df['Close'].pct_change()
        # Annualized Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std() * (252 ** 0.5) 
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Construct specific summary string
        # Use .item() to ensure we get a native Python float if it's a scalar
        analysis = (
            f"Ticker: {ticker}\n"
            f"Current Price: ${latest['Close']:.2f}\n"
            f"50-Day SMA: ${latest['SMA_50']:.2f}\n"
            f"200-Day SMA: ${latest['SMA_200']:.2f}\n"
            f"Annualized Volatility: {latest['Volatility']:.2%}\n"
            f"Daily Return: {latest['Returns']:.2%}\n"
        )
        return analysis
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

# --- 3. CHAINS ---

# Node A: Regime Classifier
classifier_prompt = ChatPromptTemplate.from_template(
    """You are a Quantitative Analyst. Analyze the technical data below.
    Determine the Market Regime strictly from these options: 
    [Bull, Bear, Sideways/Choppy, High-Volatility Distressed].
    
    Data:
    {market_data}
    
    Reasoning: Compare Price vs SMAs. Check Volatility level (>30% is High).
    Output JUST the Regime Name followed by a 1-sentence explanation.
    """
)
classifier_chain = classifier_prompt | llm | StrOutputParser()

# Node B: Initial Strategist
strategy_prompt = ChatPromptTemplate.from_template(
    """You are a Portfolio Manager.
    Regime: {regime}
    Data: {market_data}
    
    Suggest a trading strategy.
    - If Bull: Trend following or Buy Dips.
    - If Bear: Cash preservation or Short selling.
    - If Sideways: Iron Condors or Mean Reversion.
    - If Volatile: Reduce position size drastically.
    
    Provide a concise draft strategy (approx 100 words).
    """
)
strategy_chain = strategy_prompt | llm | StrOutputParser()

# Node C: Reflector (The Risk Manager)
reflector_prompt = ChatPromptTemplate.from_template(
    """You are a Senior Risk Manager (The Skeptic).
    Review this strategy for a potential "Fake Out" or "Bull Trap".
    
    Regime Detected: {regime}
    Proposed Strategy: {initial_strategy}
    Technical Data: {market_data}
    
    Ask yourself:
    1. Is this regime shift genuine or just temporary noise?
    2. What if the volatility spikes tomorrow?
    3. Does the 200 SMA support this view?
    
    Output a critique and list specific risks.
    """
)
reflector_chain = reflector_prompt | llm | StrOutputParser()

# Node D: Final Adjuster
adjuster_prompt = ChatPromptTemplate.from_template(
    """You are the Chief Investment Officer.
    
    Original Strategy: {initial_strategy}
    Risk Critique: {reflection}
    
    Finalize the instructions. Incorporate the risks. 
    If the risk is too high, switch to "Stay in Cash".
    
    Output the Final Executive Directive.
    """
)
adjuster_chain = adjuster_prompt | llm | StrOutputParser()

# --- 4. NODE FUNCTIONS ---

def fetch_data_node(state: QuantState):
    data = get_market_analysis(state["ticker"])
    return {"market_data": data}

def classify_node(state: QuantState):
    regime = classifier_chain.invoke({"market_data": state["market_data"]})
    print(f"🧐 Regime Detected: {regime}")
    return {"regime": regime}

def strategy_node(state: QuantState):
    plan = strategy_chain.invoke({
        "regime": state["regime"], 
        "market_data": state["market_data"]
    })
    return {"initial_strategy": plan}

def reflect_node(state: QuantState):
    print("🤔 Risk Manager Reflecting...")
    critique = reflector_chain.invoke({
        "regime": state["regime"],
        "initial_strategy": state["initial_strategy"],
        "market_data": state["market_data"]
    })
    return {"reflection": critique}

def adjust_node(state: QuantState):
    final = adjuster_chain.invoke({
        "initial_strategy": state["initial_strategy"],
        "reflection": state["reflection"]
    })
    return {"final_decision": final}

# --- 5. GRAPH BUILD ---
workflow = StateGraph(QuantState)

workflow.add_node("fetch_data", fetch_data_node)
workflow.add_node("classifier", classify_node)
workflow.add_node("strategist", strategy_node)
workflow.add_node("reflector", reflect_node)
workflow.add_node("adjuster", adjust_node)

# Flow
workflow.add_edge("fetch_data", "classifier")
workflow.add_edge("classifier", "strategist")
workflow.add_edge("strategist", "reflector")
workflow.add_edge("reflector", "adjuster")
workflow.add_edge("adjuster", END)

workflow.set_entry_point("fetch_data")
app = workflow.compile()

# --- 6. EXPORTABLE FUNCTION ---
def quant_agent(ticker: str):
    """Entry point for the UI"""
    return app.invoke({"ticker": ticker})

# # --- 6. EXECUTION ---
# if __name__ == "__main__":
#     # Test on a volatile asset like NVDA or BTC-USD
#     ticker_symbol = "NATIONALUM.NS" 
    
#     print(f"🚀 Starting Quant Agent for {ticker_symbol}...")
#     result = app.invoke({"ticker": ticker_symbol})
    
#     print("\n" + "="*60)
#     print(f"RESULTS FOR {ticker_symbol}")
#     print("="*60)
#     print(f"📊 MARKET REGIME: {result['regime']}")
#     print("-" * 60)
#     print(f"🛡️ RISK REFLECTION:\n{result['reflection']}")
#     print("-" * 60)
#     print(f"🏆 FINAL STRATEGY:\n{result['final_decision']}")
#     print("="*60)