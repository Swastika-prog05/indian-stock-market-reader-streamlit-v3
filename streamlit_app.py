import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import date, timedelta

st.set_page_config(page_title="Indian Stock Market Reader", page_icon="📈", layout="wide")

INDIAN_STOCKS = {
    "Large Cap": {
        "Reliance Industries": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS", "Infosys": "INFY.NS", "Bharti Airtel": "BHARTIARTL.NS",
        "State Bank of India": "SBIN.NS", "Larsen & Toubro": "LT.NS", "ITC": "ITC.NS",
        "Hindustan Unilever": "HINDUNILVR.NS", "Axis Bank": "AXISBANK.NS", "Kotak Mahindra Bank": "KOTAKBANK.NS",
        "Bajaj Finance": "BAJFINANCE.NS", "HCL Technologies": "HCLTECH.NS", "Sun Pharma": "SUNPHARMA.NS",
        "Maruti Suzuki": "MARUTI.NS", "Asian Paints": "ASIANPAINT.NS", "Titan Company": "TITAN.NS",
        "UltraTech Cement": "ULTRACEMCO.NS", "NTPC": "NTPC.NS"
    },
    "Banking & Finance": {
        "HDFC Bank": "HDFCBANK.NS", "ICICI Bank": "ICICIBANK.NS", "State Bank of India": "SBIN.NS",
        "Axis Bank": "AXISBANK.NS", "Kotak Mahindra Bank": "KOTAKBANK.NS", "IndusInd Bank": "INDUSINDBK.NS",
        "Bank of Baroda": "BANKBARODA.NS", "Punjab National Bank": "PNB.NS", "Canara Bank": "CANBK.NS",
        "Federal Bank": "FEDERALBNK.NS", "Bajaj Finance": "BAJFINANCE.NS", "Bajaj Finserv": "BAJAJFINSV.NS",
        "SBI Life Insurance": "SBILIFE.NS", "HDFC Life Insurance": "HDFCLIFE.NS", "ICICI Prudential Life": "ICICIPRULI.NS"
    },
    "IT & Technology": {
        "TCS": "TCS.NS", "Infosys": "INFY.NS", "HCL Technologies": "HCLTECH.NS", "Wipro": "WIPRO.NS",
        "Tech Mahindra": "TECHM.NS", "LTIMindtree": "LTIM.NS", "Persistent Systems": "PERSISTENT.NS",
        "Mphasis": "MPHASIS.NS", "Coforge": "COFORGE.NS", "Oracle Financial Services": "OFSS.NS"
    },
    "Energy & Power": {
        "Reliance Industries": "RELIANCE.NS", "ONGC": "ONGC.NS", "Indian Oil Corporation": "IOC.NS",
        "Bharat Petroleum": "BPCL.NS", "Coal India": "COALINDIA.NS", "NTPC": "NTPC.NS",
        "Power Grid Corporation": "POWERGRID.NS", "Tata Power": "TATAPOWER.NS", "Adani Green Energy": "ADANIGREEN.NS"
    },
    "FMCG & Consumer": {
        "ITC": "ITC.NS", "Hindustan Unilever": "HINDUNILVR.NS", "Nestle India": "NESTLEIND.NS",
        "Britannia": "BRITANNIA.NS", "Dabur India": "DABUR.NS", "Godrej Consumer Products": "GODREJCP.NS",
        "Marico": "MARICO.NS", "Tata Consumer Products": "TATACONSUM.NS", "Varun Beverages": "VBL.NS"
    },
    "Auto": {
        "Maruti Suzuki": "MARUTI.NS", "Mahindra & Mahindra": "M&M.NS", "Tata Motors": "TATAMOTORS.NS",
        "Bajaj Auto": "BAJAJ-AUTO.NS", "Hero MotoCorp": "HEROMOTOCO.NS", "Eicher Motors": "EICHERMOT.NS",
        "TVS Motor": "TVSMOTOR.NS", "Ashok Leyland": "ASHOKLEY.NS", "MRF": "MRF.NS"
    },
    "Pharma & Healthcare": {
        "Sun Pharma": "SUNPHARMA.NS", "Dr Reddy's Laboratories": "DRREDDY.NS", "Cipla": "CIPLA.NS",
        "Divi's Laboratories": "DIVISLAB.NS", "Apollo Hospitals": "APOLLOHOSP.NS", "Lupin": "LUPIN.NS",
        "Aurobindo Pharma": "AUROPHARMA.NS", "Biocon": "BIOCON.NS", "Max Healthcare": "MAXHEALTH.NS"
    },
    "Metals & Infrastructure": {
        "Tata Steel": "TATASTEEL.NS", "JSW Steel": "JSWSTEEL.NS", "Hindalco": "HINDALCO.NS",
        "Vedanta": "VEDL.NS", "Larsen & Toubro": "LT.NS", "UltraTech Cement": "ULTRACEMCO.NS",
        "Shree Cement": "SHREECEM.NS", "Ambuja Cements": "AMBUJACEM.NS", "Adani Ports": "ADANIPORTS.NS"
    },
    "New Age & Growth": {
        "Zomato": "ZOMATO.NS", "PB Fintech": "POLICYBZR.NS", "Nykaa": "NYKAA.NS", "Paytm": "PAYTM.NS",
        "Delhivery": "DELHIVERY.NS", "Trent": "TRENT.NS", "Dixon Technologies": "DIXON.NS",
        "Tata Elxsi": "TATAELXSI.NS", "Suzlon Energy": "SUZLON.NS"
    }
}

INDIAN_INDICES = {"Nifty 50": "^NSEI", "Sensex": "^BSESN", "Bank Nifty": "^NSEBANK", "Nifty IT": "^CNXIT"}

PRESETS = {
    "Balanced India Portfolio": ["Reliance Industries", "TCS", "HDFC Bank", "ICICI Bank", "Infosys", "Larsen & Toubro", "ITC", "Sun Pharma"],
    "Banking Portfolio": ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank", "Bank of Baroda"],
    "IT Portfolio": ["TCS", "Infosys", "HCL Technologies", "Wipro", "Tech Mahindra", "LTIMindtree"],
    "Consumer Portfolio": ["ITC", "Hindustan Unilever", "Nestle India", "Britannia", "Tata Consumer Products", "Varun Beverages"],
    "Growth Portfolio": ["Zomato", "Trent", "Dixon Technologies", "Tata Elxsi", "Persistent Systems", "Suzlon Energy"]
}


def flatten_stocks():
    stocks = {}
    sectors = {}
    for sector, items in INDIAN_STOCKS.items():
        for name, ticker in items.items():
            stocks[name] = ticker
            sectors.setdefault(name, set()).add(sector)
    return stocks, {k: ", ".join(sorted(v)) for k, v in sectors.items()}

ALL_STOCKS, STOCK_SECTORS = flatten_stocks()

st.markdown("""
<style>
.answer {padding:1rem;border-radius:14px;background:#f8fafc;border:1px solid #e2e8f0;margin-bottom:1rem;}
.answer b{color:#0f172a}.small-note{color:#64748b;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)


def answer(title, text):
    st.markdown(f"<div class='answer'><b>{title}</b><br>{text}</div>", unsafe_allow_html=True)


def pct(x):
    return f"{x:.2%}"


def money(x):
    return f"₹{x:,.0f}"


def risk_label(vol):
    if vol < 0.18:
        return "Low to moderate risk"
    if vol < 0.30:
        return "Moderate to high risk"
    return "High risk"


def clean_ticker(raw):
    value = raw.strip().upper()
    if not value:
        return ""
    if value.startswith("^"):
        return value
    return value if "." in value else value + ".NS"


@st.cache_data(show_spinner=False, ttl=1800)
def load_data(tickers, start_date, end_date):
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False, threads=True, group_by="column")
    except Exception:
        return pd.DataFrame()
    if data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        if "Close" not in data.columns.get_level_values(0):
            return pd.DataFrame()
        prices = data["Close"].copy()
    else:
        if "Close" not in data.columns:
            return pd.DataFrame()
        prices = data[["Close"]].copy()
        prices.columns = [tickers[0] if isinstance(tickers, list) else tickers]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()
    prices = prices.dropna(how="all").ffill().dropna()
    valid = [c for c in prices.columns if prices[c].dropna().shape[0] >= 60]
    return prices[valid]


def stock_metrics(prices, risk_free_rate):
    returns = prices.pct_change().dropna()
    ann_return = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = (ann_return - risk_free_rate) / ann_vol.replace(0, np.nan)
    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
    dd = {}
    for t in prices.columns:
        curve = prices[t] / prices[t].iloc[0]
        dd[t] = (curve / curve.cummax() - 1).min()
    metrics = pd.DataFrame({"Total Return": total_return, "Annual Return": ann_return, "Annual Volatility": ann_vol, "Sharpe Ratio": sharpe, "Max Drawdown": pd.Series(dd)})
    return metrics.replace([np.inf, -np.inf], np.nan).dropna(), returns


def simulate(returns, simulations, risk_free_rate):
    tickers = list(returns.columns)
    mean_returns = returns.mean() * 252
    cov = returns.cov() * 252
    rows = []
    for _ in range(simulations):
        w = np.random.random(len(tickers))
        w = w / w.sum()
        r = float(np.sum(mean_returns * w))
        v = float(np.sqrt(np.dot(w.T, np.dot(cov, w))))
        s = float((r - risk_free_rate) / v) if v > 0 else 0
        row = {"Return": r, "Volatility": v, "Sharpe Ratio": s}
        row.update({f"{t} Weight": float(weight) for t, weight in zip(tickers, w)})
        rows.append(row)
    df = pd.DataFrame(rows)
    return df, df.loc[df["Sharpe Ratio"].idxmax()], df.loc[df["Volatility"].idxmin()]


def weights_from(row, tickers):
    return {t: float(row.get(f"{t} Weight", 0)) for t in tickers}


def normalize(prices):
    return prices / prices.iloc[0] * 100


def backtest(prices, weights):
    if len(prices) < 120:
        return pd.Series(dtype=float), pd.Series(dtype=float), None
    test = prices.iloc[int(len(prices) * 0.75):]
    ret = test.pct_change().dropna()
    w = np.array([weights.get(t, 0) for t in ret.columns])
    if w.sum() <= 0:
        return pd.Series(dtype=float), pd.Series(dtype=float), None
    w = w / w.sum()
    portfolio = (1 + ret.dot(w)).cumprod() * 100
    benchmark = (1 + ret.mean(axis=1)).cumprod() * 100
    result = {"Portfolio Return": portfolio.iloc[-1] / portfolio.iloc[0] - 1, "Benchmark Return": benchmark.iloc[-1] / benchmark.iloc[0] - 1}
    return portfolio, benchmark, result


def rf_prediction(prices, ticker):
    series = prices[ticker].dropna()
    if len(series) < 150:
        return None, None
    df = pd.DataFrame({"Close": series})
    for lag in [1, 2, 3, 5]:
        df[f"Lag {lag}"] = df["Close"].shift(lag)
    df["Rolling 7"] = df["Close"].rolling(7).mean()
    df["Rolling 21"] = df["Close"].rolling(21).mean()
    df["Momentum 7"] = df["Close"] / df["Close"].shift(7) - 1
    df = df.dropna()
    features = ["Lag 1", "Lag 2", "Lag 3", "Lag 5", "Rolling 7", "Rolling 21", "Momentum 7"]
    X, y = df[features], df["Close"]
    split = int(len(df) * 0.8)
    model = RandomForestRegressor(n_estimators=200, random_state=42, min_samples_leaf=2)
    model.fit(X.iloc[:split], y.iloc[:split])
    pred = model.predict(X.iloc[split:])
    rmse = float(np.sqrt(mean_squared_error(y.iloc[split:], pred)))
    pred_df = pd.DataFrame({"Actual": y.iloc[split:], "Predicted": pred}, index=y.iloc[split:].index)
    next_price = float(model.predict(X.iloc[[-1]])[0])
    latest = float(series.iloc[-1])
    return pred_df, {"Latest": latest, "Next": next_price, "Move": next_price / latest - 1, "RMSE": rmse}


st.sidebar.title("Indian Stock Selection")
mode = st.sidebar.radio("Choose selection mode", ["Popular preset", "Sector based", "Manual stock search", "Custom ticker"])
selected_names = []
custom_tickers = []

if mode == "Popular preset":
    preset = st.sidebar.selectbox("Select preset portfolio", list(PRESETS.keys()))
    selected_names = PRESETS[preset]
elif mode == "Sector based":
    selected_sectors = st.sidebar.multiselect("Select sectors", list(INDIAN_STOCKS.keys()), default=["Large Cap", "Banking & Finance", "IT & Technology"])
    options = []
    for s in selected_sectors:
        options.extend(list(INDIAN_STOCKS[s].keys()))
    options = sorted(list(dict.fromkeys(options)))
    selected_names = st.sidebar.multiselect("Choose stocks", options, default=options[:8])
elif mode == "Manual stock search":
    selected_names = st.sidebar.multiselect("Search and choose stocks", sorted(ALL_STOCKS.keys()), default=["Reliance Industries", "TCS", "HDFC Bank", "ICICI Bank", "Infosys", "Larsen & Toubro", "ITC", "Sun Pharma"])
else:
    raw = st.sidebar.text_area("Enter NSE tickers", value="RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK", help="You can type RELIANCE or RELIANCE.NS. The app adds .NS automatically.")
    custom_tickers = [clean_ticker(x) for x in raw.split(",") if clean_ticker(x)]

include_index = st.sidebar.checkbox("Compare with Indian index", value=True)
index_name = st.sidebar.selectbox("Benchmark index", list(INDIAN_INDICES.keys()))

today = date.today()
start_date = st.sidebar.date_input("Start date", value=today - timedelta(days=365 * 5))
end_date = st.sidebar.date_input("End date", value=today)
risk_free_rate = st.sidebar.slider("Risk-free rate", 0.00, 0.15, 0.06, 0.005)
simulations = st.sidebar.slider("Portfolio simulations", 1000, 30000, 8000, 1000)
investment_amount = st.sidebar.number_input("Investment amount", min_value=1000, value=100000, step=1000)
strategy = st.sidebar.radio("Portfolio strategy", ["Max Sharpe", "Minimum Risk"])
run = st.sidebar.button("Analyze now", type="primary")

st.title("Indian Stock Market Reader")
st.caption("Choose Indian stocks by name, sector, preset, or ticker. Get on-spot analysis, allocation, backtest, and ML-based price reading.")
st.warning("Educational tool only. This is not financial advice.")

if not run:
    st.markdown("### Select Indian stocks from the sidebar and click **Analyze now**.")
    st.stop()

if mode == "Custom ticker":
    tickers = custom_tickers
    label_map = {t: t.replace(".NS", "") for t in tickers}
else:
    tickers = [ALL_STOCKS[n] for n in selected_names if n in ALL_STOCKS]
    label_map = {ALL_STOCKS[n]: n for n in selected_names if n in ALL_STOCKS}

if len(tickers) < 2:
    st.error("Please select at least two valid stocks.")
    st.stop()
if len(tickers) > 15:
    st.info("For speed and stability, the app will analyze the first 15 selected stocks.")
    tickers = tickers[:15]
if start_date >= end_date:
    st.error("Start date must be earlier than end date.")
    st.stop()

with st.spinner("Fetching Indian market data and generating analysis..."):
    prices = load_data(tickers, start_date, end_date)

if prices.empty or len(prices.columns) < 2:
    st.error("Could not fetch enough valid data. Try fewer stocks, check tickers, or change the date range.")
    st.stop()

valid = list(prices.columns)
display = {t: label_map.get(t, t.replace(".NS", "")) for t in valid}
metrics, returns = stock_metrics(prices, risk_free_rate)
if metrics.empty or returns.empty:
    st.error("Could not calculate enough metrics from the selected data.")
    st.stop()

sim_df, max_sharpe, min_risk = simulate(returns, simulations, risk_free_rate)
selected_port = max_sharpe if strategy == "Max Sharpe" else min_risk
w = weights_from(selected_port, valid)
portfolio_curve, benchmark_curve, bt = backtest(prices, w)

st.header("On-Spot Answer")
best = metrics["Sharpe Ratio"].idxmax()
highest = metrics["Annual Return"].idxmax()
lowest = metrics["Annual Volatility"].idxmin()
allocs = sorted([(t, wt) for t, wt in w.items() if wt > 0.01], key=lambda x: x[1], reverse=True)
alloc_text = ", ".join([f"{display.get(t, t)}: {wt:.1%}" for t, wt in allocs[:6]])

answer("Overall reading", f"Based on the selected period, <b>{display.get(best, best)}</b> has the strongest risk-adjusted performance. Highest annual return comes from <b>{display.get(highest, highest)}</b>. Lowest volatility comes from <b>{display.get(lowest, lowest)}</b>.")
answer("Best portfolio", f"Selected strategy: <b>{strategy}</b>. Expected annual return: <b>{pct(selected_port['Return'])}</b>. Expected volatility: <b>{pct(selected_port['Volatility'])}</b>. Sharpe ratio: <b>{selected_port['Sharpe Ratio']:.3f}</b>. Risk level: <b>{risk_label(selected_port['Volatility'])}</b>.")
answer("Suggested allocation", f"For <b>{money(investment_amount)}</b>, largest allocations are: <b>{alloc_text}</b>.")
if bt:
    diff = bt["Portfolio Return"] - bt["Benchmark Return"]
    result_text = "outperformed" if diff >= 0 else "underperformed"
    answer("Backtest result", f"Optimized portfolio return: <b>{pct(bt['Portfolio Return'])}</b>. Equal-weight benchmark return: <b>{pct(bt['Benchmark Return'])}</b>. The portfolio {result_text} by <b>{pct(abs(diff))}</b>.")

st.header("Portfolio Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Expected Return", pct(selected_port["Return"]))
c2.metric("Volatility", pct(selected_port["Volatility"]))
c3.metric("Sharpe Ratio", f"{selected_port['Sharpe Ratio']:.3f}")
c4.metric("Stocks Analyzed", len(valid))

st.header("Investment Allocation")
allocation = pd.DataFrame({"Stock": [display[t] for t in valid], "Ticker": valid, "Weight": [w[t] for t in valid], "Amount": [w[t] * investment_amount for t in valid]})
allocation = allocation[allocation["Weight"] > 0.001].sort_values("Weight", ascending=False)
alloc_view = allocation.copy()
alloc_view["Weight"] = alloc_view["Weight"].map(lambda x: f"{x:.2%}")
alloc_view["Amount"] = alloc_view["Amount"].map(money)
left, right = st.columns(2)
with left:
    st.dataframe(alloc_view, use_container_width=True, hide_index=True)
with right:
    st.plotly_chart(px.pie(allocation, names="Stock", values="Weight", title="Portfolio Allocation"), use_container_width=True)

st.header("Stock-Level Analysis")
metrics_named = metrics.copy()
metrics_named.insert(0, "Stock", [display.get(t, t) for t in metrics_named.index])
metrics_named.insert(1, "Ticker", metrics_named.index)
view = metrics_named.copy()
for col in ["Total Return", "Annual Return", "Annual Volatility", "Max Drawdown"]:
    view[col] = view[col].map(pct)
view["Sharpe Ratio"] = view["Sharpe Ratio"].map(lambda x: f"{x:.3f}")
st.dataframe(view, use_container_width=True, hide_index=True)

st.header("Charts")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Price Performance", "Efficient Frontier", "Correlation", "Backtest", "Prediction"])

with tab1:
    norm = normalize(prices)
    fig = go.Figure()
    for t in valid:
        fig.add_trace(go.Scatter(x=norm.index, y=norm[t], mode="lines", name=display.get(t, t)))
    if include_index:
        index_data = load_data([INDIAN_INDICES[index_name]], start_date, end_date)
        if not index_data.empty:
            idx_norm = normalize(index_data)
            col = idx_norm.columns[0]
            fig.add_trace(go.Scatter(x=idx_norm.index, y=idx_norm[col], mode="lines", name=index_name, line=dict(dash="dash")))
    fig.update_layout(title="Normalized Price Performance", xaxis_title="Date", yaxis_title="Value, base 100", height=550)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sim_df["Volatility"], y=sim_df["Return"], mode="markers", marker=dict(size=6, color=sim_df["Sharpe Ratio"], colorscale="Viridis", showscale=True, colorbar=dict(title="Sharpe")), name="Simulated portfolios"))
    fig.add_trace(go.Scatter(x=[selected_port["Volatility"]], y=[selected_port["Return"]], mode="markers", marker=dict(size=18, symbol="star", color="red"), name="Selected portfolio"))
    fig.update_layout(title="Efficient Frontier", xaxis_title="Volatility", yaxis_title="Expected Return", height=550)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    corr = returns.corr()
    names = [display.get(t, t) for t in corr.columns]
    fig = go.Figure(data=go.Heatmap(z=corr.values, x=names, y=names, colorscale="RdBu", zmin=-1, zmax=1))
    fig.update_layout(title="Stock Return Correlation", height=550)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    if bt:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=portfolio_curve.index, y=portfolio_curve, mode="lines", name="Optimized portfolio"))
        fig.add_trace(go.Scatter(x=benchmark_curve.index, y=benchmark_curve, mode="lines", name="Equal-weight benchmark"))
        fig.update_layout(title="Backtest Performance", xaxis_title="Date", yaxis_title="Value, base 100", height=550)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Backtest requires more data.")

with tab5:
    options = {display.get(t, t): t for t in valid}
    chosen_name = st.selectbox("Select stock for prediction", list(options.keys()))
    chosen = options[chosen_name]
    pred_df, pred = rf_prediction(prices, chosen)
    if pred_df is None:
        st.warning("Prediction requires more historical data.")
    else:
        move_word = "higher" if pred["Move"] > 0 else "lower"
        answer(f"{chosen_name} prediction reading", f"Latest price: <b>₹{pred['Latest']:.2f}</b>. Model estimated next price: <b>₹{pred['Next']:.2f}</b>, which is <b>{pct(abs(pred['Move']))}</b> {move_word}. RMSE: <b>{pred['RMSE']:.2f}</b>.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pred_df.index, y=pred_df["Actual"], mode="lines", name="Actual"))
        fig.add_trace(go.Scatter(x=pred_df.index, y=pred_df["Predicted"], mode="lines", name="Predicted"))
        fig.update_layout(title=f"{chosen_name} Actual vs Predicted Price", xaxis_title="Date", yaxis_title="Price", height=550)
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("<div class='small-note'>Data source: Yahoo Finance through yfinance. NSE tickers use .NS. Results depend on selected historical data and inputs. Educational use only.</div>", unsafe_allow_html=True)
