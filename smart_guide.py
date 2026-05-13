def render_smart_guide():
    st.write("---")
    st.header("🧠 ระบบวิเคราะห์และช่วยตัดสินใจ (Smart Guide)")
 
    # --- Pre-define ---
    cost = 0.0
    shares = 0.0
    current_price = 0.0
    tp_price = 0.0
    sl_price = 0.0
 
    # --- 1. Input หลัก ---
    c1, c2 = st.columns(2)
    with c1:
        cost = st.number_input(
            "1. ต้นทุนเฉลี่ยต่อหุ้น ($)",
            value=0.0, step=0.0001, format="%.4f", key="sg_cost"
        )
    with c2:
        shares = st.number_input(
            "2. จำนวนหุ้นที่ถือ (รองรับเศษหุ้น)",
            value=0.0, step=1e-10, format="%.10f", key="sg_shares"
        )
 
    # --- 2. ราคาตลาด ---
    current_price = st.number_input(
        "3. ราคาตลาดปัจจุบัน ($)",
        value=0.0, format="%.4f", key="sg_market"
    )
 
    # --- 3. เลือกแผน ---
    st.write("### 🎯 4. เลือกเป้าหมายกำไร:")
    plan_choice = st.radio(
        "เลือกระดับความคาดหวัง:",
        ["เอาค่าขนม (+5%)", "พอดีคำ (+10%)", "คำโต (+20%)"],
        index=1, horizontal=True, key="sg_plan"
    )
 
    if "5%" in plan_choice:
        target_pct = 5.0
    elif "10%" in plan_choice:
        target_pct = 10.0
    else:
        target_pct = 20.0
 
    # --- คำนวณเป้าหมาย ---
    if cost > 0:
        tp_price = cost * (1 + target_pct / 100)
        sl_price = cost * 0.95
        st.info(
            f"📍 **เป้าหมายปัจจุบัน:** ขายที่ ${tp_price:.4f} "
            f"| ตัดขาดทุนที่ ${sl_price:.4f}"
        )
 
    # --- แสดงผลเมื่อครบ ---
    if cost > 0 and shares > 0 and current_price > 0:
        invested      = cost * shares
        current_value = current_price * shares
        pnl           = current_value - invested
        pnl_pct       = (pnl / invested) * 100
 
        target_value  = tp_price * shares
        target_profit = target_value - invested
        sl_value      = sl_price * shares
 
        # Summary cards
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("💼 ลงทุนไป",     f"${invested:,.2f}")
        m2.metric("📈 มูลค่าตอนนี้", f"${current_value:,.2f}")
        m3.metric(
            "💰 กำไร/ขาดทุน",
            f"${pnl:,.2f}",
            delta=f"{pnl_pct:+.1f}%"
        )
 
        # Status bar
        st.write("---")
        if current_price >= tp_price:
            st.success(
                f"🔥 **กำไรทะลุเป้าแล้ว!** "
                f"ราคาปัจจุบัน ${current_price:.4f} สูงกว่าเป้า ${tp_price:.4f}"
            )
        elif current_price < sl_price:
            st.error(
                f"🚨 **ต่ำกว่าจุดตัดขาดทุน!** "
                f"พิจารณาขายเพื่อจำกัดความเสียหาย "
                f"(จุดคัท ${sl_price:.4f})"
            )
        elif current_price < cost:
            st.warning(
                f"⚠️ **ติดลบอยู่** "
                f"อีก ${cost - current_price:.4f}/หุ้น ถึงเท่าทุน"
            )
        else:
            st.info(
                f"⏳ **กำลังเดินทาง...** "
                f"อีก ${tp_price - current_price:.4f}/หุ้น ถึงเป้าหมาย"
            )
 
        # ตารางกลยุทธ์
        st.write(f"#### 📊 ตารางเปรียบเทียบกลยุทธ์ (เป้า +{target_pct:.0f}%)")
 
        # กำหนด badge AI ตามสถานการณ์
        if current_price >= tp_price:
            badges = [
                "กำไรเน้นๆ จบงาน",
                "ขายตามระเบียบวินัย",
                "แนะนำ! คืนทุนแล้วถือลุ้นต่อ"
            ]
        elif current_price < sl_price:
            badges = [
                "เจ็บแต่จบ ดีกว่าปล่อยทิ้ง",
                "ต้องรออีกนาน",
                "ยังทำไม่ได้"
            ]
        elif current_price < cost:
            badges = [
                "เจ็บแต่จบ",
                "ต้องรออีกนาน",
                "ยังทำไม่ได้"
            ]
        else:
            badges = [
                "ใจร้อนไปนิด",
                "ถือตามแผนต่อไป ✅",
                "ลดความเสี่ยงได้ดี"
            ]
 
        table_data = {
            "กลยุทธ์": [
                "💰 ขายตอนนี้เลย",
                f"🎯 ถือรอเป้าหมาย +{target_pct:.0f}%",
                "🛡️ ขายคืนทุน แล้วถือฟรี"
            ],
            "ราคาขาย ($)": [
                f"${current_price:.4f}",
                f"${tp_price:.4f}",
                f"${cost:.4f}"
            ],
            "มูลค่าที่ได้ ($)": [
                f"${current_value:,.2f}",
                f"${target_value:,.2f}",
                f"${invested:,.2f}"
            ],
            "กำไร/ขาดทุน ($)": [
                f"${pnl:+,.2f} ({pnl_pct:+.1f}%)",
                f"${target_profit:+,.2f} ({target_pct:+.1f}%)",
                "ได้ทุนคืน (หุ้นที่เหลือคือโบนัส)"
            ],
            "มุมมอง": badges
        }
 
        st.table(table_data)
 
    else:
        st.warning(
            "👈 กรุณากรอก **ต้นทุน**, **จำนวนหุ้น** และ **ราคาตลาด** "
            "เพื่อให้ระบบแสดงตารางวิเคราะห์ครับ"
        )
 
 
# --- เรียกใช้ standalone หรือ import ก็ได้ ---
if __name__ == "__main__":
    st.set_page_config(page_title="Smart Guide", page_icon="🧠", layout="centered")
    render_smart_guide()
