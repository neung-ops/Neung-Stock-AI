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
            if pwd == "1234": # คุณหนึ่งเปลี่ยนรหัสตรงนี้ได้ครับ
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ รหัสผ่านไม่ถูกต้อง")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. การตั้งค่าหน้าจอและคู่มือ (App Config & Manual) ---
st.set_page_config(page_title="AI Stock Pro", layout="wide")

# ส่วนปุ่มคู่มือการใช้งาน (Manual Popover)
with st.sidebar:
    with st.popover("📖 คู่มือการใช้งาน (User Manual)"):
        st.markdown("""
        ### วิธีใช้งานเบื้องต้น
        1. **เลือกหุ้น:** เลือกจาก 'รายการโปรด' หรือ 'พิมพ์ชื่อเอง' ที่แถบด้านซ้าย
        2. **ซูมกราฟ:** ใช้ **ลูกกลิ้งเมาส์ (Scroll Wheel)** เพื่อซูมเข้า-ออกได้อิสระ
        3. **เลื่อนกราฟ:** คลิกแล้วลากเพื่อเลื่อนดูช่วงเวลา (Pan)
        4. **สัญญาณ AI:** ดูแถบสีและข้อความสรุปใต้กราฟเพื่อประกอบการตัดสินใจ
        ---
        *หมายเหตุ: เป็นการพยากรณ์เชิงสถิติเท่านั้น โปรดใช้วิจารณญาณ*
        """)

# --- 3. ส่วนจัดการรายการหุ้นโปรด (Quick Select) ---
with st.sidebar:
    st.header("🔍 ค้นหาหุ้น")
    search_mode = st.radio("รูปแบบการเลือก:", ["รายการโปรด", "พิมพ์ชื่อเอง"])
    
    if search_mode == "รายการโปรด":
        fav_list = {
            "NVDA": "NVIDIA (หุ้นชิป AI)",
            "AMD": "AMD (หุ้นชิป/ประมวลผล)",
            "VOO": "S&P 500 (กองทุนดัชนีสหรัฐ)",
            "VGT": "Tech Sector (กองทุนกลุ่มเทคโนโลยี)",
            "GC=F": "Gold (ราคาทองคำโลก)"
        }
        ticker_input = st.selectbox("เลือกจากรายการที่คุณติดตาม:", options=list(fav_list.keys()), format_func=lambda x: fav_list[x])
    else:
        ticker_input = st.text_input("พิมพ์ชื่อ Ticker (เช่น AAPL, TSLA):", value="").upper().strip()

    st.write("---")
    days_to_predict = st.slider("พยากรณ์ล่วงหน้า (วัน):", 1, 30, 7)
    period = st.selectbox("ข้อมูลย้อนหลัง:", ["6mo", "1y", "2y", "5y"], index=1)
    
    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- 4. ฟังก์ชันคำนวณและดึงข้อมูล ---
@st.cache_data
def get_data(symbol, p):
    try:
        data = yf.download(symbol, period=p)
        return data
    except: return None

if ticker_input:
    df = get_data(ticker_input, period)
    
    if df is None or df.empty:
        st.info(f"💡 กำลังรอข้อมูลจาก '{ticker_input}' หรือชื่อหุ้นไม่ถูกต้อง")
    else:
        # --- เตรียม AI (Linear Regression) ---
        close_prices = df['Close'].values.flatten()
        df_ml = pd.DataFrame({'Close': close_prices})
        df_ml['S_1'] = df_ml['Close'].shift(1)
        df_ml = df_ml.dropna()
        X = df_ml[['S_1']].values.reshape(-1, 1)
        y = df_ml['Close'].values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # พยากรณ์
        last_val = float(close_prices[-1])
        preds = []
        for _ in range(days_to_predict):
            next_p = model.predict(np.array([[last_val]]))[0][0]
            preds.append(next_p)
            last_val = next_p

        # --- 5. ส่วนการแสดงผล (UI) ---
        st.title(f"📈 {ticker_input} Analysis Report")
        
        # กราฟพร้อมระบบซูมด้วยลูกกลิ้งเมาส์
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=close_prices, name="ราคาจริง", line=dict(color='#1f77b4')))
        
        future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, days_to_predict + 1)]
        fig.add_trace(go.Scatter(x=future_dates, y=preds, name="AI พยากรณ์", line=dict(dash='dash', color='#ff7f0e')))
        
        # ตั้งค่าการซูมด้วย Mouse Wheel
        fig.update_layout(
            hovermode="x unified",
            dragmode="pan", # คลิกค้างเพื่อเลื่อน
            xaxis=dict(rangeslider=dict(visible=False)),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        # เปิดใช้งาน Scroll Zoom
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # --- 6. ระบบวิเคราะห์สัญญาณ (AI Commentary & Action) ---
        current_p = float(close_prices[-1])
        target_p = float(preds[-1])
        change_pct = ((target_p - current_p) / current_p) * 100

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("ราคาล่าสุด", f"${current_p:.2f}")
        with c2:
            st.metric(f"เป้าหมาย ({days_to_predict} วัน)", f"${target_p:.2f}", delta=f"{change_pct:.2f}%")
        with c3:
            # ระบบสัญญาณไฟจราจร
            if change_pct > 2:
                st.success("🟢 คำแนะนำ: Buy / สะสม")
            elif change_pct < -2:
                st.error("🔴 คำแนะนำ: Sell / ลดพอร์ต")
            else:
                st.warning("🟡 คำแนะนำ: Hold / ถือรอ")

        # กล่องคำอธิบาย AI
        with st.expander("📝 บทวิเคราะห์จากระบบ AI", expanded=True):
            trend = "ขาขึ้น (Bullish)" if change_pct > 0 else "ขาลง (Bearish)"
            st.write(f"""
            จากการเรียนรู้ข้อมูลย้อนหลัง **{period}** หุ้น **{ticker_input}** แสดงทิศทางเป็น **{trend}** 
            โดยมีราคาเป้าหมายอยู่ที่ประมาณ **${target_p:.2f}** (เปลี่ยนแปลง {change_pct:.2f}%) 
            กลยุทธ์ที่แนะนำคือสอดคล้องกับสัญญาณไฟด้านบน ทั้งนี้ควรตรวจสอบข่าวสารตลาดประกอบด้วย
            """)
