import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. ระบบรักษาความปลอดภัย (Security) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔒 AI Stock Analyzer Access")
        pwd = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน:", type="password")
        if st.button("Login"):
            if pwd == "zerozezstock": # เปลี่ยนรหัสผ่านตรงนี้ได้ตามต้องการ
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ รหัสผ่านไม่ถูกต้อง")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. การตั้งค่าหน้าจอและคู่มือ (App Config & Detailed Manual) ---
st.set_page_config(page_title="AI Stock Pro - " + datetime.now().strftime('%Y'), layout="wide")

with st.sidebar:
    st.header("📖 Help Center")
    with st.popover("📚 คู่มือการใช้งานเบื้องต้น"):
        st.markdown("""
        ### 🛠 วิธีการใช้งานเบื้องต้น
        1. **การเลือกหุ้น:** 
            * เลือก **'รายการโปรด'** สำหรับหุ้นที่ถืออยู่ (NVDA, AMD, ทอง) 
            * หรือเลือก **'พิมพ์ชื่อเอง'** เพื่อค้นหาหุ้นใหม่ๆ ทั่วโลก
        2. **การปรับช่วงเวลา:**
            * ใช้สไลเดอร์ปรับ **'พยากรณ์ล่วงหน้า'** (แนะนำ 7-14 วันเพื่อให้แม่นยำที่สุด)
            * เลือก **'ข้อมูลย้อนหลัง'** เพื่อให้ AI เรียนรู้พฤติกรรมราคา (1y หรือ 2y กำลังดีครับ)
        
        ### 🖱️ เทคนิคการควบคุมกราฟ
        * **ซูม (Zoom):** หมุนลูกกลิ้งเมาส์ (Scroll Wheel) ขึ้น-ลง ตรงจุดที่ต้องการดู
        * **เลื่อน (Pan):** คลิกซ้ายค้างที่กราฟแล้วลากไปมาเพื่อดูข้อมูลย้อนหลัง
        * **รีเซ็ต (Reset):** **ดับเบิ้ลคลิก (Double Click)** ที่พื้นที่ว่างบนกราฟ เพื่อกลับสู่มุมมองปกติทันที
        
        ### 🎯 กลยุทธ์การลงทุน
        * **สายชิลล์:** เหมาะกับคุณหนึ่งที่ไม่ว่างเช็กทุกวัน ระบบจะคัดกรองเฉพาะเทรนด์ที่ชัดเจนจริงๆ (เน้นถือยาว)
        * **สายลุย:** เหมาะกับการเล่นรอบสั้น ระบบจะไวต่อการแกว่งตัวของราคาเป็นพิเศษ
        """)

# --- 3. ส่วนการเลือกกลยุทธ์และหุ้น (Strategy & Ticker Selection) ---
with st.sidebar:
    st.write("---")
    st.header("🎯 กลยุทธ์การลงทุน")
    strategy = st.radio(
        "เลือกสไตล์ของคุณ:",
        ["สายชิลล์ (ถือยาว)", "สายลุย (ทำรอบ)"],
        help="สายชิลล์: ซื้อเมื่อมั่นใจ (+5%), ขายเมื่อเริ่มเสี่ยง (-3%) | สายลุย: เข้าออกไว (+2%/-2%)"
    )
    
    # กำหนดเกณฑ์ตามกลยุทธ์
    if strategy == "สายชิลล์ (ถือยาว)":
        buy_limit, sell_limit = 5, -3
        strat_tag = "🔵 Conservative Mode"
    else:
        buy_limit, sell_limit = 2, -2
        strat_tag = "🔥 Aggressive Mode"

    st.write("---")
    st.header("🔍 ค้นหาหุ้น")
    search_mode = st.radio("รูปแบบ:", ["รายการโปรด", "พิมพ์ชื่อเอง"])
    
    if search_mode == "รายการโปรด":
        fav_list = {
            "NVDA": "NVIDIA (AI Leader)",
            "AMD": "AMD (Processors)",
            "VOO": "S&P 500 ETF",
            "VGT": "Tech ETF",
            "GC=F": "Gold (ทองคำ)"
        }
        ticker_input = st.selectbox("หุ้นที่คุณติดตาม:", options=list(fav_list.keys()), format_func=lambda x: fav_list[x])
    else:
        ticker_input = st.text_input("พิมพ์ Ticker (เช่น TSLA, BTC-USD):", value="").upper().strip()

    days_to_predict = st.slider("พยากรณ์ล่วงหน้า (วัน):", 1, 30, 7)
    period = st.selectbox("ข้อมูลย้อนหลัง:", ["6mo", "1y", "2y", "5y"], index=1)
    
    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- 4. ฟังก์ชันประมวลผลข้อมูล ---
@st.cache_data
def get_data(symbol, p):
    try:
        data = yf.download(symbol, period=p)
        return data
    except: return None

if ticker_input:
    df = get_data(ticker_input, period)
    
    if df is None or df.empty:
        st.info("💡 เลือกหุ้นจากรายการด้านซ้ายเพื่อเริ่มวิเคราะห์")
    else:
        # AI Logic (Linear Regression)
        close_prices = df['Close'].values.flatten()
        df_ml = pd.DataFrame({'Close': close_prices})
        df_ml['S_1'] = df_ml['Close'].shift(1)
        df_ml = df_ml.dropna()
        X = df_ml[['S_1']].values.reshape(-1, 1)
        y = df_ml['Close'].values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # ทำนาย
        last_val = float(close_prices[-1])
        preds = []
        for _ in range(days_to_predict):
            next_p = model.predict(np.array([[last_val]]))[0][0]
            preds.append(next_p)
            last_val = next_p

        # --- 5. กราฟและการควบคุม ---
        st.title(f"📈 {ticker_input} Analysis")
        st.subheader(f"Strategy: {strat_tag}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=close_prices, name="ราคาจริง", line=dict(color='#1f77b4')))
        
        future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, days_to_predict + 1)]
        fig.add_trace(go.Scatter(x=future_dates, y=preds, name="AI พยากรณ์", line=dict(dash='dash', color='#ff7f0e')))
        
        fig.update_layout(
            hovermode="x unified",
            dragmode="pan",
            xaxis=dict(rangeslider=dict(visible=False)),
            margin=dict(l=10, r=10, t=40, b=10),
            height=550
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # --- 6. สรุปผลและสัญญาณ (Action Signals) ---
        current_p = float(close_prices[-1])
        target_p = float(preds[-1])
        change_pct = ((target_p - current_p) / current_p) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ราคาล่าสุด", f"${current_p:.2f}")
        with col2:
            st.metric(f"เป้าหมาย ({days_to_predict} วัน)", f"${target_p:.2f}", delta=f"{change_pct:.2f}%")
        with col3:
            if change_pct > buy_limit:
                st.success(f"🟢 แนะนำ: Buy ({strategy})")
            elif change_pct < sell_limit:
                st.error(f"🔴 แนะนำ: Sell ({strategy})")
            else:
                st.warning(f"🟡 แนะนำ: Hold ({strategy})")

        with st.expander("📝 บทวิเคราะห์โดยละเอียด", expanded=True):
            trend = "ขาขึ้น" if change_pct > 0 else "ขาลง"
            advice = "เป็นโอกาสที่ดีในการเข้าสะสม" if change_pct > buy_limit else "ควรพิจารณาขายเพื่อลดความเสี่ยง" if change_pct < sell_limit else "ยังไม่พบสัญญาณการเปลี่ยนแปลงที่สำคัญ"
            
            st.write(f"""
            ระบบวิเคราะห์หุ้น **{ticker_input}** โดยอ้างอิงกลยุทธ์ **{strategy}** 
            พบว่าแนวโน้มในอีก {days_to_predict} วันข้างหน้ามีโอกาสเป็น **{trend}** 
            โดยราคาพยากรณ์อยู่ที่ **${target_p:.2f}** ({change_pct:.2f}%)
            สรุป: {advice} (คำแนะนำนี้ปรับตามเกณฑ์กลยุทธ์ที่คุณเลือก)
            """)
            st.info("💡 TIP: หากมุมมองกราฟเพี้ยน ให้ Double Click ที่กราฟเพื่อรีเซ็ตหน้าจอ")
