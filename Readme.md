# 🤖 Market-Regime-Detector-AI

**A Multi-Agent Reflexion System for Market Regime Detection & Strategy Formulation.**

This project uses **LangGraph** and **Llama 3** (via Groq) to simulate a hedge fund team. It autonomously analyzes financial data, detects market regimes, drafts a trading strategy, and performs a risk assessment ("reflexion") before finalizing a decision.

---

## 📊 Core Metrics Explained

The agent relies on four key technical indicators to form its "Ground Truth." Here is how they are calculated and why they matter:

### 1. Simple Moving Averages (SMA 50 & 200)
- **What it is:** The average closing price over the last 50 days (Short-term trend) and 200 days (Long-term trend).
- **How it's used:**
    - **Golden Cross (Bullish):** When the 50 SMA crosses *above* the 200 SMA.
    - **Death Cross (Bearish):** When the 50 SMA crosses *below* the 200 SMA.
    - **Support/Resistance:** Prices often bounce off these lines.

### 2. Annualized Volatility
- **Formula:** $\sigma_{annual} = \sigma_{daily} \times \sqrt{252}$
- **What it is:** A measure of how wildly the price swings. We assume 252 trading days in a year.
- **Thresholds (General Rules):**
    - **Low (<15%):** Calm market (Steady trends).
    - **Medium (15% - 30%):** Normal activity.
    - **High (>30%):** Distressed or speculative market.
- **Impact:** High volatility triggers the agent to suggest *smaller position sizes* or *staying in cash*.

### 3. Daily Returns
- **Formula:** $\frac{Price_{today} - Price_{yesterday}}{Price_{yesterday}}$
- **What it is:** The percentage gain or loss for the most recent trading day.
- **Impact:** Used to gauge immediate short-term momentum.

---

## 🧠 The Decision Logic (Agent Workflow)

The system is built as a **State Graph** where data flows through specialized "Agents" (Nodes).

### 1. Regime Classifier Node
*Analyzes the raw metrics to tag the current market state.*
- **Bull:** Price > SMA 50 > SMA 200.
- **Bear:** Price < SMA 50 < SMA 200.
- **Sideways/Choppy:** Price is bouncing around the SMAs with no clear direction.
- **High-Volatility Distressed:** Volatility is extreme (>30-40%), regardless of direction.

### 2. Strategist Node (The Portfolio Manager)
*Proposes a plan based strictly on the Regime.*
- **If Bull:** Suggests "Trend Following" or "Buying the Dip."
- **If Bear:** Suggests "Cash Preservation" or "Short Selling."
- **If Sideways:** Suggests "Iron Condors" (Options) or "Mean Reversion" trades.
- **If Volatile:** Suggests "Risk-Off" (Reduce exposure).

### 3. Reflector Node (The Risk Manager)
*The "Skeptic" agent.*
- Looks for **"Fake Outs"** (e.g., A Bull Trap where price rises briefly but volume is low).
- Checks if the volatility is too high for the proposed strategy.
- asks: *"What if the market gaps down 5% tomorrow?"*

### 4. Final Adjuster (The CIO)
*Synthesizes the Strategy and the Critique.*
- If the Risk Manager raises valid concerns, the CIO modifies the plan (e.g., "Buy, but wait for a pullback to $105").
- If risks are critical, it overrides the strategy to **"Stay in Cash."**

---

## 🚀 Installation & Usage

1. **Clone the repository**
   ```bash
   git clone [https://github.com/mamoon-ansari/Market-Regime-Detector-AI.git](https://github.com/mamoon-ansari/Market-Regime-Detector-AI.git)
   cd quant-agent
