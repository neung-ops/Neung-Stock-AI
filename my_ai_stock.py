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
            if pwd == "zerorezstock": # รหัสผ่านที่คุณกำหนด
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ รหัสผ่านไม่ถูกต้อง")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. ตั้งค่าหน้าจอและคู่มือฉบับทางการ (App Config & Professional Manual) ---
st.set_page_config(page_title="AI Stock Analyzer Pro", layout="wide")

with st.sidebar:
    st.header("📖 Help Center")
    with st.popover("📚 คู่มือการใช้งาน"):
        st.markdown("""
        ### 🛠 วิธีการใช้งานเบื้องต้น
        1. **การเลือกสินทรัพย์:** 
            * เลือกจาก **'รายการโปรด'** สำหรับหุ้นหลักที่ระบบติดตามอยู่ (NVDA, AMD, Gold ฯลฯ)
            * หรือเลือก **'พิมพ์ชื่อเอง'** เพื่อค้นหา Ticker จาก Yahoo Finance ทั่วโลก
        2. **การปรับช่วงข้อมูล:**
            * **พยากรณ์ล่วงหน้า:** ปรับจำนวนวันที่ต้องการให้ AI ทำนายผล (แนะนำ 7-14 วัน)
            * **ข้อมูลย้อนหลัง:** เลือกช่วงเวลาเพื่อให้ AI เรียนรู้พฤติกรรมราคา (เริ่มต้นที่ 1 ปี)
        
        ### 🖱️ เทคนิคการควบคุมกราฟ
        * **การซูม (Zoom):** ใช้ลูกกลิ้งเมาส์ (Scroll Wheel) เพื่อขยายดูรายละเอียดเฉพาะจุด
        * **การเลื่อน (Pan):** คลิกซ้ายค้างที่หน้ากราฟแล้วลากเพื่อดูข้อมูลย้อนหลัง
        * **การรีเซ็ต (Reset View):** **ดับเบิ้ลคลิก (Double Click)** บนพื้นที่ว่างของกราฟ เพื่อกลับสู่มุมมองปกติ
        
        ### 🎯 กลยุทธ์การลงทุน
        * **สายชิลล์ (Conservative):** เหมาะสำหรับการถือครองระยะยาว ระบบจะเน้นสัญญาณที่ชัดเจนเพื่อลดความผันผวน
        * **สายลุย (Aggressive):** เหมาะสำหรับการเล่นรอบระยะสั้น ระบบจะไวต่อการเปลี่ยนแปลงของราคาเป็นพิเศษ
        """)
        
        st.info("""
        **🧭 ข้อแนะนำในการใช้งาน:**
        โปรดใช้แอปพลิเคชันนี้เปรียบเสมือน **'เข็มทิศนำทาง'** เพื่อช่วยคัดกรองสัญญาณทางเทคนิคและลดการใช้อารมณ์ในการตัดสินใจ โดยควรตรวจสอบราคา Real-time จากแอปพลิเคชันหลักและติดตามข่าวสารสำคัญควบคู่ไปด้วยก่อนการลงทุนเสมอ
        """)

# --- 3. เมนูเลือกกลยุทธ์และหุ้น (Strategy & Selection) ---
with st.sidebar:
    st.write("---")
    st.header("🎯 กลยุทธ์การลงทุน")
    strategy = st.radio(
        "เลือกสไตล์การวิเคราะห์:",
        ["สายชิลล์ (ถือยาว)", "สายลุย (ทำรอบ)"],
        help="สายชิลล์: ซื้อเมื่อมั่นใจ (+5%), ขายเมื่อเริ่มเสี่ยง (-3%) | สายลุย: เข้าออกไว (+2%/-2%)"
    )
    
    if strategy == "สายชิลล์ (ถือยาว)":
        buy_limit, sell_limit = 5, -3
        strat_tag = "🔵 Conservative Mode"
    else:
        buy_limit, sell_limit = 2, -2
        strat_tag = "🔥 Aggressive Mode"

    st.write("---")
    st.header("🔍 ค้นหาข้อมูลหุ้น")
    search_mode = st.radio("รูปแบบการค้นหา:", ["รายการโปรด", "พิมพ์ชื่อเอง"])
    
    if search_mode == "รายการโปรด":
        fav_list = {
            "NVDA": "NVIDIA (AI & GPU Leader)",
            "AMD": "AMD (Processors & Graphics)",
            "VOO": "VOO (S&P 500 Index ETF)",
            "VGT": "VGT (Information Technology ETF)",
            "GC=F": "Gold (ทองคำ)"
        }
        ticker_input = st.selectbox("เลือกจากรายการหลัก:", options=list(fav_list.keys()), format_func=lambda x: fav_list[x])
    else:
        ticker_input = st.text_input("ระบุ Ticker Symbol (เช่น AAPL, BTC-USD):", value="").upper().strip()

    days_to_predict = st.slider("พยากรณ์ล่วงหน้า (วัน):", 1, 30, 7)
    
    # เพิ่มคำอธิบาย Tooltip สำหรับช่วงเวลา
    st.sidebar.markdown("เลือกช่วงข้อมูลย้อนหลัง:", help="""
    • 6mo: สำหรับหุ้นผันผวนสูง (e.g.TECH)
    • 1y: มาตรฐานที่แม่นยำที่สุด
    • 2y+: ดูแนวต้านระยะยาว
    """)
    
    # 2. ใส่ Selectbox ไว้ข้างล่างโดย 'ซ่อน' Label ของตัวมันเอง
    period = st.sidebar.selectbox(
        "Select Period", # ชื่อภายใน (มองไม่เห็นบนหน้าเว็บ)
        ["6mo", "1y", "2y", "5y"], 
        index=1,
        label_visibility="collapsed" # บรรทัดนี้สำคัญมาก: ทำให้ชื่อข้างบนหายไปและไม่กินพื้นที่
    )
    
    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()

# --- 4. การประมวลผลข้อมูล AI ---
@st.cache_data
def get_data(symbol, p):
    try:
        data = yf.download(symbol, period=p)
        return data
    except: return None

if ticker_input:
    df = get_data(ticker_input, period)
    
    if df is None or df.empty:
        st.info("💡 กรุณาเลือกหุ้นหรือระบุ Ticker เพื่อเริ่มต้นการวิเคราะห์")
    else:
        # AI Modeling (Linear Regression)
        close_prices = df['Close'].values.flatten()
        df_ml = pd.DataFrame({'Close': close_prices})
        df_ml['S_1'] = df_ml['Close'].shift(1)
        df_ml = df_ml.dropna()
        X = df_ml[['S_1']].values.reshape(-1, 1)
        y = df_ml['Close'].values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Prediction Logic
        last_val = float(close_prices[-1])
        preds = []
        for _ in range(days_to_predict):
            next_p = model.predict(np.array([[last_val]]))[0][0]
            preds.append(next_p)
            last_val = next_p

        # --- 5. การแสดงผลกราฟ Interactive ---
        st.title(f"📈 {ticker_input} Market Analysis")
        st.markdown(f"**Investment Strategy:** `{strat_tag}`")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=close_prices, name="Historical Price", line=dict(color='#1f77b4', width=2)))
        
        future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, days_to_predict + 1)]
        fig.add_trace(go.Scatter(x=future_dates, y=preds, name="AI Prediction", line=dict(dash='dash', color='#ff7f0e', width=2)))
        
        fig.update_layout(
            hovermode="x unified",
            dragmode="pan",
            xaxis=dict(rangeslider=dict(visible=False)),
            margin=dict(l=10, r=10, t=40, b=10),
            height=550
        )
        
        # เปิดการซูมด้วยลูกกลิ้งเมาส์
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        # --- 6. บทสรุปและสัญญาณวิเคราะห์ ---
        current_p = float(close_prices[-1])
        target_p = float(preds[-1])
        change_pct = ((target_p - current_p) / current_p) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ราคาตลาดล่าสุด", f"${current_p:.2f}")
        with col2:
            st.metric(f"เป้าหมาย ({days_to_predict} วันข้างหน้า)", f"${target_p:.2f}", delta=f"{change_pct:.2f}%")
        with col3:
            if change_pct > buy_limit:
                st.success(f"🟢 แนะนำ: ซื้อ (Buy Signal)")
            elif change_pct < sell_limit:
                st.error(f"🔴 แนะนำ: ขาย (Sell Signal)")
            else:
                st.warning(f"🟡 แนะนำ: ถือ/รอดูอาการ (Hold)")

        with st.expander("📝 บทวิเคราะห์เชิงเทคนิคจาก AI", expanded=True):
            trend_txt = "ทิศทางขาขึ้น" if change_pct > 0 else "ทิศทางขาลง"
            status_txt = "เป็นจุดที่น่าสนใจในการสะสม" if change_pct > buy_limit else "ควรระมัดระวังแรงเทขาย" if change_pct < sell_limit else "ราคามีแนวโน้มเคลื่อนไหวในกรอบแคบ"
            
            st.write(f"""
            จากการประมวลผลข้อมูลหุ้น **{ticker_input}** ย้อนหลังในช่วง **{period}** 
            ระบบ AI คาดการณ์ว่าในระยะสั้นมีโอกาสเป็น **{trend_txt}** โดยมีราคาเป้าหมายอยู่ที่ประมาณ **${target_p:.2f}** 
            ภายใต้กลยุทธ์ที่เลือก สรุปคือ **{status_txt}** ทั้งนี้ผู้ลงทุนควรศึกษาปัจจัยพื้นฐานเพิ่มเติมประกอบการตัดสินใจ
            """)
            st.caption("หมายเหตุ: ดับเบิ้ลคลิกที่หน้ากราฟเพื่อรีเซ็ตมุมมองการซูม")

        st.write("---")
        # --- [USER-FRIENDLY VERSION] ภาษาชาวบ้าน อ่านง่าย สั่งงานชัด ---
        st.write("---")
        st.header("🧮 เครื่องมือช่วยตัดสินใจ (ฉบับเข้าใจง่ายที่สุด)")

        # 1. หาราคาตลาดปัจจุบัน
        current_val = 0.0
        try:
            if 'hist' in locals(): current_val = float(hist['Close'].iloc[-1])
            elif 'df' in locals(): current_val = float(df['Close'].iloc[-1])
            elif 'last_price' in locals(): current_val = float(last_price)
        except: current_val = 0.0

        # 2. กรอกข้อมูลแบบง่ายๆ
        c1, c2, c3 = st.columns(3)
        with c1:
            cost = st.number_input("1. ซื้อมาหุ้นละกี่ดอลล์ ($)", value=0.0, key="c_final")
        with c2:
            shares = st.number_input("2. มีอยู่ในมือทั้งหมดกี่หุ้น", value=0, key="s_final")
        with c3:
            target = st.slider("3. อยากได้กำไรกี่ % ดี?", 5, 50, 10, key="p_final")

        if cost > 0 and shares > 0:
            take_profit = cost * (1 + target/100)
            stop_loss = cost * 0.95 
            
            # สรุปแผนแบบไม่ต้องใช้ศัพท์เทคนิค
            st.info(f"💡 **สรุปแผน:** ถ้าถึง **${take_profit:.2f}** ให้รีบขายเอาเงินเข้ากระเป๋า | แต่ถ้าหล่นไปถึง **${stop_loss:.2f}** ให้รีบหนีทันที!")

            # 3. ส่วนเช็คสถานะและสั่งการ
            price_input = st.number_input("4. ราคาตลาดตอนนี้ที่เห็นคือเท่าไหร่ ($)", value=current_val if current_val > 0 else 0.0)
            now_price = price_input if price_input > 0 else current_val

            if now_price > 0:
                st.write("### 📢 สิ่งที่คุณต้องทำตอนนี้:")
                
                # สถานการณ์: กำไรทะลุเป้า
                if now_price >= take_profit:
                    total_profit = (now_price - cost) * shares
                    st.success(f"### 🔥 **รวยแล้ว! กำไรทะลุเป้าไป ${total_profit:,.2f}**")
                    
                    st.write("**เลือกทำตามตารางนี้ได้เลยครับ:**")
                    st.table({
                        "แผนการ": ["A: ขายหมดเกลี้ยง", "B: ขายครึ่งเดียวเอาทุนคืน"],
                        "จำนวนหุ้นที่ต้องขาย": [f"{shares} หุ้น", f"{shares // 2} หุ้น"],
                        "เงินที่จะได้รับจริง ($)": [f"${now_price * shares:,.2f}", f"${now_price * (shares // 2):,.2f}"],
                        "ผลลัพธ์": ["จบงาน สบายใจ", f"ได้ทุนคืน แล้วถือลุ้นต่ออีก {shares - (shares // 2)} หุ้น"]
                    })
                
                # สถานการณ์: ขาดทุนถึงจุดต้องหนี
                elif now_price <= stop_loss:
                    loss = (cost - now_price) * shares
                    st.error(f"### 🚨 **ต้องยอมแพ้แล้ว! กดขายทิ้งทันที**")
                    st.write(f"ถ้าขายตอนนี้จะขาดทุนที่ **${loss:,.2f}** ยอมเจ็บแค่นี้เพื่อรักษาเงินส่วนใหญ่ไว้ไปเล่นตัวใหม่ครับ")
                
                # สถานการณ์: ราคายังนิ่งๆ
                else:
                    diff = (now_price - cost) * shares
                    st.warning(f"### ⏳ **นั่งนิ่งๆ จิบกาแฟรอไปก่อน**")
                    st.write(f"ตอนนี้สถานะคือ {'กำไร' if diff > 0 else 'ขาดทุน'} อยู่ **${abs(diff):,.2f}** ราคายังไม่ถึงจุดที่ต้องขยับตามแผนครับ")
        else:
            st.write("👈 รบกวนคุณหนึ่งกรอกเลขในข้อ 1 กับ 2 ให้ผมหน่อยครับ เดี๋ยวผมช่วยวางแผนให้")

        # --- Footer ---
        from datetime import datetime, timedelta
        now_thai = datetime.now() + timedelta(hours=7) 
        st.write("---") 
        st.caption(f"Last updated: {now_thai.strftime('%Y-%m-%d %H:%M:%S')} (TH) | พัฒนาโดย ZEROREZ")
