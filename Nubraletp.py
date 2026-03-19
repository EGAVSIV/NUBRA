import streamlit as st
import pandas as pd
import time

from nubra_python_sdk.marketdata.market_data import MarketData
from nubra_python_sdk.start_sdk import InitNubraSdk, NubraEnv

# ================= INIT =================
nubra = InitNubraSdk(NubraEnv.UAT, env_creds=True)
market_data = MarketData(nubra)

# ================= CONFIG =================
symbols = ["NIFTY", "RELIANCE", "TCS", "INFY"]

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Nubra Live Dashboard", layout="wide")

st.title("📊 Nubra Live Market Dashboard")

# ================= FETCH FUNCTION =================
def fetch_ltp(symbol):
    try:
        data = market_data.current_price(symbol)

        return {
            "Symbol": symbol,
            "LTP": data.price / 100 if data.price else None,
            "% Change": data.change if data.change else 0
        }
    except:
        return None

# ================= REFRESH BUTTON =================
if st.button("🔄 Refresh Data"):
    st.rerun()

# ================= AUTO REFRESH =================
refresh_interval = st.slider("Auto Refresh (seconds)", 2, 10, 3)

# ================= MAIN LOOP =================
placeholder = st.empty()

while True:
    results = []

    for sym in symbols:
        result = fetch_ltp(sym)
        if result:
            results.append(result)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Sort by % Change
    df = df.sort_values(by="% Change", ascending=False)

    # ================= COLOR FUNCTION =================
    def color_change(val):
        if val > 0:
            return "color: green"
        elif val < 0:
            return "color: red"
        else:
            return "color: gray"

    # ================= DISPLAY =================
    with placeholder.container():
        st.subheader("📈 Sorted by % Gain")

        st.dataframe(
            df.style.applymap(color_change, subset=["% Change"]),
            use_container_width=True
        )

        # Top Gainer / Loser
        if not df.empty:
            top_gainer = df.iloc[0]
            top_loser = df.iloc[-1]

            col1, col2 = st.columns(2)

            with col1:
                st.success(f"🚀 Top Gainer: {top_gainer['Symbol']} ({top_gainer['% Change']:.2f}%)")

            with col2:
                st.error(f"🔻 Top Loser: {top_loser['Symbol']} ({top_loser['% Change']:.2f}%)")

    time.sleep(refresh_interval)
