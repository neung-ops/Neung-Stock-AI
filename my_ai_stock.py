import streamlit as st

# สร้างฟังก์ชันเช็ครหัสผ่านแบบง่าย
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        pwd = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน:", type="password")
        if pwd == "zerorezstock": # เปลี่ยนคำนี้เป็นรหัสที่คุณต้องการ
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            if pwd:
                st.error("รหัสผ่านไม่ถูกต้อง")
            return False
    return True

if not check_password():
    st.stop() # หยุดการทำงานถ้าใส่รหัสไม่ถูก

# --- โค้ดเดิมของคุณทั้งหมดให้เอามาต่อตรงนี้ ---
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")
st.title("📈 AI Stock Analysis Dashboard")

# --- ส่วน Sidebar: เลือกหุ้นและตั้งค่า ---
with st.sidebar:
    st.header("Settings")
    # ใส่ Ticker หุ้นที่สนใจ (NVDA, AMD, VGT, VOO)
    ticker = st.text_input("ใส่ชื่อหุ้น (เช่น NVDA, AMD, VOO):", value="NVDA").upper()
    days_to_predict = st.slider("จำนวนวันที่ต้องการพยากรณ์ล่วงหน้า:", 1, 30, 7)
    period = st.selectbox("ช่วงเวลาข้อมูลย้อนหลัง:", ["6mo", "1y", "2y", "5y"], index=1)

# --- ฟังก์ชันดึงข้อมูล ---
@st.cache_data
def load_data(symbol, p):
    data = yf.download(symbol, period=p)
    return data

try:
    df = load_data(ticker, period)
    
    if df.empty:
        st.error("ไม่พบข้อมูลหุ้นตัวนี้ กรุณาตรวจสอบชื่อ Ticker อีกครั้ง")
    else:
        # --- เตรียมข้อมูลสำหรับ AI (Linear Regression) ---
        # ดึงราคาปิดและจัดการมิติข้อมูลให้ถูกต้อง
        close_prices = df['Close'].values.flatten()
        
        df_ml = pd.DataFrame({'Close': close_prices})
        df_ml['S_1'] = df_ml['Close'].shift(1)
        df_ml = df_ml.dropna()

        # ปรับทรงข้อมูลให้เป็น 2D Array สำหรับ Scikit-learn
        X = df_ml[['S_1']].values.reshape(-1, 1)
        y = df_ml['Close'].values.reshape(-1, 1)

        # สร้างและเทรน Model
        model = LinearRegression()
        model.fit(X, y)

        # ทำนายราคาในอนาคตตามจำนวนวันที่เลือก
        last_price = float(close_prices[-1])
        predictions = []
        for _ in range(days_to_predict):
            next_price = model.predict(np.array([[last_price]]))[0][0]
            predictions.append(next_price)
            last_price = next_price

        # --- การแสดงผล (Layout) ---
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(f"กราฟราคาและแนวโน้มของ {ticker}")
            fig = go.Figure()
            
            # เส้นราคาจริง
            fig.add_trace(go.Scatter(x=df.index, y=close_prices, name="ราคาจริง (Actual Price)"))
            
            # เส้นพยากรณ์ (เริ่มต่อจากวันล่าสุด)
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
            st.write("**สถานะพอร์ตปัจจุบัน:**")
            st.info(f"คุณกำลังวิเคราะห์หุ้น {ticker} โดยใช้สถิติย้อนหลัง {period}")
            
            # ปุ่มดาวน์โหลดข้อมูลเผื่อเอาไปใช้ในงานอื่น (เช่น Excel)
            csv = df.to_csv().encode('utf-8')
            st.download_button("ดาวน์โหลดข้อมูล (CSV)", csv, f"{ticker}_data.csv", "text/csv")

except Exception as e:
    st.warning(f"เกิดข้อผิดพลาดในการคำนวณ: {e}")
