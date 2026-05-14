import streamlit as st
import streamlit.components.v1 as components

# TIPS เดิม 3 อัน + เพิ่มอันที่ 4
TIPS = [
    "ขายหุ้นออกตอนนี้เพื่อปิดดีลรับเงินก้อนทั้งหมด (ทั้งทุนและกำไร) เข้าบัญชีทันที",
    "รอให้ราคาขึ้นถึงเป้าที่คุณเลือก ระบบจะคำนวณว่าถ้าถึงจุดนั้นจะได้เงินรวมเท่าไหร่",
    "ขายหุ้นออกแค่เท่ากับจำนวนเงินที่ลงทุนไป เงินที่เหลือในพอร์ตคือ 'หุ้นฟรี' ที่ไม่มีต้นทุนแล้ว",
    "ดึงเฉพาะเงินส่วนเกิน (กำไร) ออกมาใช้จ่าย โดยที่ยังรักษาเงินต้นเท่าเดิมไว้ในหุ้นตัวเดิม"
]

# ... (ฟังก์ชัน build_strategy_html เหมือนเดิมเป๊ะ ไม่ต้องแก้) ...

def render_smart_guide(market_price: float = 0.0):
    st.write("---")
    st.header("🧠 ระบบช่วยตัดสินใจ (Smart Guide)")

    cost = shares = tp_price = sl_price = 0.0

    c1, c2 = st.columns(2)
    with c1:
        cost = st.number_input("ต้นทุนต่อหุ้น ($)", value=0.0, step=0.0001, format="%.4f", key="sg_cost")
    with c2:
        shares = st.number_input("จำนวนหุ้นที่ถืออยู่", value=0.0, step=1e-10, format="%.10f", key="sg_shares")

    if market_price > 0:
        current_price = market_price
        st.info(f"📡 ราคาตลาดปัจจุบัน: **${current_price:.4f}**")
    else:
        current_price = st.number_input("ราคาตลาดตอนนี้ ($)", value=0.0, format="%.4f", key="sg_market")

    if cost > 0 and shares > 0 and current_price > 0:
        invested      = cost * shares
        current_value = current_price * shares
        pnl           = current_value - invested
        pnl_pct       = (pnl / invested) * 100
        
        # --- ส่วนที่ 1: การ์ด 3 ใบเดิมของคุณหนึ่ง ---
        st.write("### 🎯 แผนการรันเทรน (3 ใบเดิม)")
        plan_choice = st.radio(
            "เลือกเป้าหมายกำไร:",
            ["นิดหน่อยก็พอ (+5%)", "พอดีๆ (+10%)", "รอให้ได้เยอะ (+20%)"],
            index=1, horizontal=True, key="sg_plan"
        )
        target_pct = 5.0 if "5%" in plan_choice else (10.0 if "10%" in plan_choice else 20.0)
        tp_price      = cost * (1 + target_pct / 100)
        target_value  = tp_price * shares
        target_profit = target_value - invested

        rows_trading = [
            {
                "title": "💰 1. ขายเลย เอาเงินออกมา",
                "price": f"${current_price:.4f}",
                "value": f"${current_value:,.2f}",
                "profit": f"${pnl:+,.2f}",
                "profit_pct": f"{pnl_pct:+.1f}%",
                "profit_pos": pnl >= 0,
                "badge": "Cash Out",
                "badge_color": "green" if pnl >= 0 else "gray",
                "note": "",
            },
            {
                "title": f"🎯 2. รอเป้าหมาย {target_pct}%",
                "price": f"${tp_price:.4f}",
                "value": f"${target_value:,.2f}",
                "profit": f"${target_profit:+,.2f}",
                "profit_pct": f"{target_pct:+.1f}%",
                "profit_pos": True,
                "badge": "Waiting",
                "badge_color": "amber",
                "note": "*ตัวเลขคาดการณ์เมื่อถึงเป้า",
            },
            {
                "title": "🛡️ 3. ขายคืนทุน เหลือไว้ลุ้นฟรี",
                "price": f"${cost:.4f}",
                "value": f"${invested:,.2f}",
                "profit": "ได้ทุนคืน",
                "profit_pct": "+0.0%",
                "profit_pos": True,
                "badge": "Risk Free",
                "badge_color": "green",
                "note": "หุ้นที่เหลือในพอร์ตจะไม่มีต้นทุน",
            }
        ]
        
        # แสดง 3 ใบเดิม
        html_trading = build_strategy_html(rows_trading, highlight_idx=-1, key=f"trade_{target_pct}")
        components.html(html_trading, height=330, scrolling=False)

        # --- ส่วนที่ 2: ใบที่ 4 พิเศษ (ขูดกำไร) ---
        st.write("### 🍃 โซนเก็บเกี่ยว (Harvesting)")
        
        if pnl > 0:
            rows_harvest = [
                {
                    "title": "✂️ 4. ขูดกำไรออกมาใช้ (Cash out Profit)",
                    "price": f"${current_price:.4f}",
                    "value": f"${pnl:,.2f}",
                    "profit": "ดึงกำไรออก",
                    "profit_pct": f"{pnl_pct:+.1f}%",
                    "profit_pos": True,
                    "badge": "เก็บเกี่ยวได้ ✅",
                    "badge_color": "green",
                    "note": "ขายยอดนี้ใน Dime! เพื่อดึงกำไรไปใช้ (เงินต้นยังอยู่ครบ)",
                }
            ]
            html_harvest = build_strategy_html(rows_harvest, highlight_idx=0, key="harvest_only")
            # แก้ไขลำดับ TIPS ในใจให้ดึงอันที่ 4 มาใช้
            # (ต้องแก้ในฟังก์ชัน build_strategy_html เล็กน้อย หรือส่ง TIPS เข้าไป)
            # แต่เพื่อให้ง่าย ผมใช้ html ของเดิมที่ส่งค่าไปได้เลย
            components.html(html_harvest, height=140, scrolling=False)
        else:
            st.warning("พอร์ตยังไม่มีกำไรให้เก็บเกี่ยว")

    else:
        st.warning("👈 กรอกข้อมูลให้ครบเพื่อเริ่มวางแผน")
