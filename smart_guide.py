import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------
# คำอธิบายแต่ละกลยุทธ์ (โผล่ตอน hover)
# ---------------------------------------------------------------
STRATEGY_TIPS = {
    "sell_now":  "ขายออกทันทีที่ราคาตลาดตอนนี้เลย ได้เงินแน่นอน แต่อาจพลาดกำไรที่จะมาเพิ่ม",
    "hold_tp":   "อดทนถือต่อจนราคาถึงเป้าที่ตั้งไว้ ได้กำไรมากกว่า แต่ต้องยอมรับความเสี่ยงที่ราคาอาจไม่ไปถึง",
    "breakeven": "ขายแค่พอได้ทุนคืน หุ้นที่เหลือถือฟรีไม่มีความเสี่ยง เหมาะถ้าอยากลดความกังวลแต่ยังอยากลุ้น",
}


def build_strategy_html(rows: list, highlight_idx: int) -> str:
    tips = list(STRATEGY_TIPS.values())

    rows_html = ""
    for i, r in enumerate(rows):
        tip     = tips[i]
        is_hi   = i == highlight_idx
        border  = "2px solid #1fa66b" if is_hi else "1px solid #e0e0e0"
        bg      = "#f6fdf9" if is_hi else "#ffffff"
        bc_bg   = {"green": "#d1fae5", "amber": "#fef3c7", "gray": "#f3f4f6"}[r["badge_color"]]
        bc_txt  = {"green": "#065f46", "amber": "#92400e", "gray": "#374151"}[r["badge_color"]]
        p_color = "#1fa66b" if r["profit_pos"] else "#dc2626"

        rows_html += f"""
        <div class="card" style="border:{border};background:{bg};">
          <div class="col-title">
            <span class="title-text">{r['title']}</span>
            <span class="q-icon">?
              <div class="tooltip">{tip}</div>
            </span>
          </div>
          <div class="col">
            <div class="cell-label">ราคาขาย</div>
            <div class="cell-value">{r['price']}</div>
          </div>
          <div class="col">
            <div class="cell-label">มูลค่าที่ได้</div>
            <div class="cell-value">{r['value']}</div>
          </div>
          <div class="col">
            <div class="cell-label">กำไร/ขาดทุน</div>
            <div class="cell-value" style="color:{p_color}">{r['profit']}</div>
            <div class="cell-sub">{r['profit_pct']}</div>
          </div>
          <div class="col-badge">
            <span class="badge" style="background:{bc_bg};color:{bc_txt}">{r['badge']}</span>
          </div>
        </div>
        """

    return f"""
    <style>
      * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 0; }}
      body {{ background: transparent; }}
      .wrapper {{ padding: 2px 0 8px; }}
      .header {{
        display: grid;
        grid-template-columns: 2.4fr 1fr 1fr 1.2fr 0.8fr;
        gap: 8px;
        padding: 0 14px 8px;
        font-size: 11px;
        color: #999;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }}
      .card {{
        display: grid;
        grid-template-columns: 2.4fr 1fr 1fr 1.2fr 0.8fr;
        gap: 8px;
        align-items: center;
        border-radius: 10px;
        padding: 13px 14px;
        margin-bottom: 8px;
        transition: box-shadow 0.15s;
      }}
      .card:hover {{ box-shadow: 0 3px 14px rgba(0,0,0,0.07); }}
      .col-title {{ display: flex; align-items: center; gap: 7px; position: relative; }}
      .title-text {{ font-size: 13.5px; font-weight: 500; color: #111; }}
      .q-icon {{
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px; height: 18px;
        border-radius: 50%;
        background: #e9eaec;
        color: #555;
        font-size: 11px;
        font-weight: 700;
        cursor: default;
        flex-shrink: 0;
        user-select: none;
      }}
      .tooltip {{
        display: none;
        position: absolute;
        top: calc(100% + 7px);
        left: 0;
        background: #1c1c1e;
        color: #f0f0f0;
        font-size: 13px;
        line-height: 1.55;
        padding: 10px 13px;
        border-radius: 9px;
        width: 270px;
        z-index: 9999;
        pointer-events: none;
        white-space: normal;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
      }}
      .q-icon:hover .tooltip {{ display: block; }}
      .col {{ display: flex; flex-direction: column; gap: 2px; }}
      .cell-label {{ font-size: 11px; color: #aaa; }}
      .cell-value {{ font-size: 14px; font-weight: 500; color: #111; }}
      .cell-sub {{ font-size: 12px; color: #888; }}
      .col-badge {{ display: flex; align-items: center; }}
      .badge {{
        font-size: 11.5px;
        padding: 4px 11px;
        border-radius: 20px;
        font-weight: 500;
        white-space: nowrap;
      }}
    </style>
    <div class="wrapper">
      <div class="header">
        <div>กลยุทธ์</div>
        <div>ราคาขาย</div>
        <div>มูลค่าที่ได้</div>
        <div>กำไร/ขาดทุน</div>
        <div>สถานะ</div>
      </div>
      {rows_html}
    </div>
    """


def render_smart_guide():
    st.write("---")
    st.header("🧠 ระบบวิเคราะห์และช่วยตัดสินใจ (Smart Guide)")

    cost = shares = current_price = tp_price = sl_price = 0.0

    c1, c2 = st.columns(2)
    with c1:
        cost = st.number_input(
            "1. ต้นทุนเฉลี่ยต่อหุ้น ($)",
            value=0.0, step=0.0001, format="%.4f", key="sg_cost"
        )
    with c2:
        shares = st.number_input(
            "2. จำนวนหุ้นที่ถือ",
            value=0.0, step=1e-10, format="%.10f", key="sg_shares"
        )

    current_price = st.number_input(
        "3. ราคาตลาดปัจจุบัน ($)",
        value=0.0, format="%.4f", key="sg_market"
    )

    st.write("### 🎯 4. เลือกเป้าหมายกำไร:")
    plan_choice = st.radio(
        "เลือกระดับความคาดหวัง:",
        ["เอาค่าขนม (+5%)", "พอดีคำ (+10%)", "คำโต (+20%)"],
        index=1, horizontal=True, key="sg_plan"
    )
    target_pct = 5.0 if "5%" in plan_choice else (10.0 if "10%" in plan_choice else 20.0)

    if cost > 0:
        tp_price = cost * (1 + target_pct / 100)
        sl_price = cost * 0.95
        st.info(
            f"📍 **เป้าหมาย:** ขายที่ ${tp_price:.4f} "
            f"| ตัดขาดทุนที่ ${sl_price:.4f}"
        )

    if cost > 0 and shares > 0 and current_price > 0:
        invested      = cost * shares
        current_value = current_price * shares
        pnl           = current_value - invested
        pnl_pct       = (pnl / invested) * 100
        target_value  = tp_price * shares
        target_profit = target_value - invested

        # Summary metrics
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("💼 ลงทุนไป",      f"${invested:,.2f}")
        m2.metric("📈 มูลค่าตอนนี้",  f"${current_value:,.2f}")
        m3.metric("💰 กำไร/ขาดทุน",  f"${pnl:,.2f}", delta=f"{pnl_pct:+.1f}%")

        # Status bar
        st.write("---")
        if current_price >= tp_price:
            st.success(
                f"🔥 กำไรทะลุเป้าแล้ว! "
                f"ราคาปัจจุบัน ${current_price:.4f} สูงกว่าเป้า ${tp_price:.4f}"
            )
        elif current_price < sl_price:
            st.error(
                f"🚨 ต่ำกว่าจุดตัดขาดทุน! "
                f"พิจารณาขายเพื่อจำกัดความเสียหาย (จุดคัท ${sl_price:.4f})"
            )
        elif current_price < cost:
            st.warning(
                f"⚠️ ติดลบอยู่ อีก ${cost - current_price:.4f}/หุ้น ถึงเท่าทุน"
            )
        else:
            st.info(
                f"⏳ กำลังเดินทาง... อีก ${tp_price - current_price:.4f}/หุ้น ถึงเป้าหมาย"
            )

        # กำหนด badge + highlight ตามสถานการณ์
        if current_price >= tp_price:
            badges       = ["แนะนำ",        "ถึงแล้ว!",   "ลดความเสี่ยง"]
            badge_colors = ["green",         "green",       "green"]
            highlight    = 0
        elif current_price < sl_price:
            badges       = ["เจ็บแต่จบ",    "ต้องรออีก",  "ยังทำไม่ได้"]
            badge_colors = ["amber",         "gray",        "gray"]
            highlight    = 0
        elif current_price < cost:
            badges       = ["เจ็บแต่จบ",    "ต้องรออีก",  "ยังทำไม่ได้"]
            badge_colors = ["amber",         "gray",        "gray"]
            highlight    = 0
        else:
            badges       = ["ใจร้อนไปนิด",  "ตามแผน ✅",   "ลดความเสี่ยง"]
            badge_colors = ["amber",         "green",       "green"]
            highlight    = 1

        rows = [
            {
                "title":       "💰 ขายตอนนี้เลย",
                "price":       f"${current_price:.4f}",
                "value":       f"${current_value:,.2f}",
                "profit":      f"${pnl:+,.2f}",
                "profit_pct":  f"{pnl_pct:+.1f}%",
                "profit_pos":  pnl >= 0,
                "badge":       badges[0],
                "badge_color": badge_colors[0],
            },
            {
                "title":       f"🎯 ถือรอเป้า +{target_pct:.0f}%",
                "price":       f"${tp_price:.4f}",
                "value":       f"${target_value:,.2f}",
                "profit":      f"${target_profit:+,.2f}",
                "profit_pct":  f"{target_pct:+.1f}%",
                "profit_pos":  True,
                "badge":       badges[1],
                "badge_color": badge_colors[1],
            },
            {
                "title":       "🛡️ ขายคืนทุน แล้วถือฟรี",
                "price":       f"${cost:.4f}",
                "value":       f"${invested:,.2f}",
                "profit":      "ได้ทุนคืน",
                "profit_pct":  "+0.0%",
                "profit_pos":  True,
                "badge":       badges[2],
                "badge_color": badge_colors[2],
            },
        ]

        st.write(
            f"#### 📊 เปรียบเทียบกลยุทธ์ (เป้า +{target_pct:.0f}%)"
            "  —  วางเมาส์ที่ปุ่ม **?** เพื่ออ่านคำอธิบาย"
        )
        html = build_strategy_html(rows, highlight)
        components.html(html, height=235, scrolling=False)

    else:
        st.warning(
            "👈 กรุณากรอก ต้นทุน, จำนวนหุ้น และ ราคาตลาด "
            "เพื่อให้ระบบแสดงตารางวิเคราะห์ครับ"
        )


# --- เรียกใช้ standalone หรือ import ก็ได้ ---
if __name__ == "__main__":
    st.set_page_config(page_title="Smart Guide", page_icon="🧠", layout="centered")
    render_smart_guide()
