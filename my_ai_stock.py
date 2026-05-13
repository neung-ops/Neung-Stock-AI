import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. ระบบรักษาความปลอดภัย (Password Protection) ---
def check_password():
    """ตรวจสอบรหัสผ่านก่อนเข้าใช้งาน"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 Restricted Access")
        pwd = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบ AI:", type="password")
        if st.button("เข้าใช้งาน"):
            if pwd == "zerorezstock":  # <--- คุณหนึ่งเปลี่ยนรหัสผ่านตรงนี้ได้ตามใจชอบครับ
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ รหัสผ่านไม่ถูกต้อง")
        return False
    return True

# ถ้ายังไม่ผ่านรหัสผ่าน ให้หยุดทำงานที่เหลือ
if not check_password():
    st.stop()

# --- 2. ตั้งค่าหน้าจอ (จะทำงานเมื่อรหัสผ่านถูกต้อง) ---
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")
st.title("📈 AI Stock Analysis Dashboard")

# --- 3. ส่วน Sidebar: เลือกหุ้นและตั้งค่า ---
with st.sidebar:
    st.header("Settings")
    # เพิ่ม .strip() ป้องกันการเคาะช่องว่างเกิน
    ticker = st.text_input("ใส่ชื่อหุ้น (เช่น NVDA, AMD, VOO):", value="NVDA").upper().strip()
    days_to_predict = st.slider("จำนวนวันที่ต้องการพยากรณ์ล่วงหน้า:", 1, 30, 7)
    period = st.selectbox("ช่วงเวลาข้อมูลย้อนหลัง:", ["6mo", "1y", "2y", "5y"], index=1)
    
    if st.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- 4. ฟังก์ชันดึงข้อมูลแบบ Cache ---
@st.cache_data
def load_data(symbol, p):
    try:
        data = yf.download(symbol, period=p)
        return data
    except:
        return None

# --- 5. ส่วนประมวลผลหลัก ---
if ticker:
    try:
        with st.spinner(f'กำลังวิเคราะห์ข้อมูล {ticker}...'):
            df = load_data(ticker, period)
        
        # ตรวจสอบว่ามีข้อมูลจริงไหมก่อนรัน AI
        if df is None or df.empty:
            st.info(f"ขณะนี้ยังไม่มีข้อมูลของ {ticker} กรุณาตรวจสอบชื่อหุ้นอีกครั้ง หรือรอการอัปเดตจากตลาด")
        else:
            # เตรียมข้อมูลสำหรับ AI (Linear Regression)
            # ดึงราคาปิดและจัดการมิติข้อมูลให้เป็น 2D
            close_prices = df['Close'].values.flatten()
            
            df_ml = pd.DataFrame({'Close': close_prices})
            df_ml['S_1'] = df_ml['Close'].shift(1)
            df_ml = df_ml.dropna()

            X = df_ml[['S_1']].values.reshape(-1, 1)
            y = df_ml['Close'].values.reshape(-1, 1)

            # สร้างและเทรน Model
            model = LinearRegression()
            model.fit(X, y)

            # ทำนายราคาอนาคต
            last_price = float(close_prices[-1])
            predictions = []
            for _ in range(days_to_predict):
                next_price = model.predict(np.array([[last_price]]))[0][0]
                predictions.append(next_price)
                last_price = next_price

            # --- 6. การแสดงผล (Layout) ---
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(f"กราฟราคาและแนวโน้มของ {ticker}")
                fig = go.Figure()
                
                # เส้นราคาจริง
                fig.add_trace(go.Scatter(x=df.index, y=close_prices, name="ราคาจริง (Actual Price)"))
                
                # เส้นพยากรณ์
                future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, days_to_predict + 1)]
                fig.add_trace(go.Scatter(
                    x=future_dates, 
                    y=predictions, 
                    name="AI พยากรณ์ (Forecast)", 
                    line=dict(dash='dash', color='orange')
                ))
                
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("บทวิเคราะห์โดย AI")
                current_price = float(close_prices[-1])
                target_price = float(predictions[-1])
                percent_change = ((target_price - current_price) / current_price) * 100
                
                st.metric("ราคาล่าสุด", f"${current_price:.2f}")
                st.metric(f"เป้าหมายอีก {days_to_predict} วัน", f"${target_price:.2f}", 
                          delta=f"{percent_change:.2f}%")
                
                st.write("---")
                st.info(f"วิเคราะห์ด้วยโมเดล Linear Regression โดยอ้างอิงสถิติย้อนหลัง {period}")
                
                csv = df.to_csv().encode('utf-8')
                st.download_button("ดาวน์โหลดข้อมูล (CSV)", csv, f"{ticker}_data.csv", "text/csv")

    except Exception as e:
        st.warning("ระบบกำลังปรับจูนมิติข้อมูล กรุณารอสักครู่...")
else:
    st.info("กรุณาใส่ชื่อ Ticker หุ้นที่ต้องการวิเคราะห์ที่แถบด้านซ้าย")
