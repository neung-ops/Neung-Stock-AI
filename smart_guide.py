import streamlit as st
import streamlit.components.v1 as components

TIPS = [
    "ขายหุ้นออกตอนนี้เพื่อปิดดีลรับเงินก้อนทั้งหมด (ทั้งทุนและกำไร) เข้าบัญชีทันที",
    "เป็นการวางแผนล่วงหน้า ระบบจะคำนวณว่าถ้าราคาไปถึงเป้าที่คุณเลือก คุณจะได้เงินรวมเท่าไหร่",
    "ดึงเฉพาะเงินส่วนเกิน (กำไร) ออกมาใช้จ่าย โดยที่ 'เงินต้น' ยังอยู่ครบเท่าเดิมในพอร์ต",
]

def build_strategy_html(rows: list, highlight_idx: int, key: str) -> str:
    rows_html = ""
    for i, r in enumerate(rows):
        tip     = TIPS[i]
        is_hi   = i == highlight_idx
        border  = "2px solid #1fa66b" if is_hi else "1px solid #e0e0e0"
        bg      = "#f0fdf6" if is_hi else "#ffffff"
        bc_bg   = {"green": "#d1fae5", "amber": "#fef3c7", "gray": "#f3f4f6"}[r["badge_color"]]
        bc_txt  = {"green": "#065f46", "amber": "#92400e", "gray": "#374151"}[r["badge_color"]]
        p_color = "#1fa66b" if r["profit_pos"] else "#dc2626"
        note_html = f'<div class="cell-note">{r["note"]}</div>' if r.get("note") else ""

        rows_html += f"""
        <div class="card" style="border:{border};background:{bg};">
          <div class="col-title">
            <span class="title-text">{r['title']}</span>
            <span class="q-icon">?<div class="tooltip">{tip}</div></span>
          </div>
          <div class="col">
            <div class="cell-label">ราคาที่อ้างอิง</div>
            <div class="cell-value">{r['price']}</div>
          </div>
          <div class="col">
            <div class="cell-label">เงินที่ดึงออกมาได้</div>
            <div class="cell-value">{r['value']}</div>
            {note_html}
          </div>
          <div class="col">
            <div class="cell-label">ผลตอบแทน</div>
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
      *{{box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:0}}
      body{{background:transparent}}
      .wrapper{{padding:2px 0 8px}}
      .header{{display:grid;grid-template-columns:2.2fr 1fr 1.1fr 1.1fr 0.85fr;gap:8px;padding:0 14px 8px;font-size:11px;color:#999;font-weight:600;letter-spacing:.05em;text-transform:uppercase}}
      .card{{display:grid;grid-template-columns:2.2fr 1fr 1.1fr 1.1fr 0.85fr;gap:8px;align-items:center;border-radius:10px;padding:13px 14px;margin-bottom:8px;transition:box-shadow .15s}}
      .card:hover{{box-shadow:0 3px 14px rgba(0,0,0,.07)}}
      .col-title{{display:flex;align-items:center;gap:7px;position:relative}}
      .title-text{{font-size:13.5px;font-weight:500;color:#111}}
      .q-icon{{position:relative;display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;background:#e9eaec;color:#555;font-size:11px;font-weight:700;cursor:default;flex-shrink:0;user-select:none}}
      .tooltip{{display:none;position:absolute;top:calc(100% + 7px);left:0;background:#1c1c1e;color:#f0f0f0;font-size:13px;line-height:1.55;padding:10px 13px;border-radius:9px;width:270px;z-index:9999;pointer-events:none;white-space:normal;box-shadow:0 4px 16px rgba(0,0,0,.25)}}
      .q-icon:hover .tooltip{{display:block}}
      .col{{display:flex;flex-direction:column;gap:2px}}
      .cell-label{{font-size:11px;color:#aaa}}
      .cell-value{{font-size:14px;font-weight:500;color:#111}}
      .cell-sub{{font-size:12px;color:#888}}
      .cell-note{{font-size:11px;color:#f59e0b;margin-top:2px}}
      .col-badge{{display:flex;align-items:center}}
      .badge{{font-size:11.5px;padding:4px 11px;border-radius:20px;font-weight:500;white-space:nowrap}}
    </style>
    <div class="wrapper">
      <div class="header">
        <div>แผนการขาย</div><div>ราคาอ้างอิง</div>
        <div>ยอดเงินที่จะได้รับ</div><div>ผลตอบแทน</div><div>คำแนะนำ</div>
      </div>
      {rows_html}
    </div>
    """

def render_smart_guide(market_price: float = 0.0):
    st.write("---")
    st.header("🧠 ระบบช่วยตัดสินใจ (Smart Guide)")

    cost = shares = tp_price = sl_price = 0.0

    c1, c2 = st.columns(2)
    with c1:
        cost = st.number_input(
            "ต้นทุนต่อหุ้น ($)",
            value=0.0, step=0.0001, format="%.4f", key="sg_cost"
        )
    with c2:
        shares = st.number_input(
            "จำนวนหุ้นที่ถืออยู่",
            value=0.0, step=1e-10, format="%.10f", key="sg_shares"
        )

    if market_price > 0:
        current_price = market_price
        st.info(f"📡 ราคาตลาดปัจจุบัน: **${current_price:.4f}**")
    else:
        current_price = st.number_input(
            "ราคาตลาดตอนนี้ ($)",
            value=0.0, format="%.4f", key="sg_market"
        )

    st.write("### 🎯 ตั้งเป้าหมายกำไร")
    plan_choice = st.radio(
        "เลือกเป้าหมายการรันเทรน:",
        ["เก็บค่าขนม (+5%)", "พอดีคำ (+10%)", "คำโต (+20%)"],
        index=1, horizontal=True, key="sg_plan"
    )
    target_pct = 5.0 if "5%" in plan_choice else (10.0 if "10%" in plan_choice else 20.0)

    if cost > 0 and shares > 0 and current_price > 0:
        invested      = cost * shares
        current_value = current_price * shares
        pnl           = current_value - invested
        pnl_pct       = (pnl / invested) * 100
        
        tp_price      = cost * (1 + target_pct / 100)
        target_value  = tp_price * shares
        target_profit = target_value - invested
        sl_price      = cost * 0.95

        # --- คัดกรองข้อมูลสำหรับ "ช่องพิเศษ: ถอนกำไร" ---
        harvest_amount = pnl if pnl > 0 else 0.0
        harvest_badge = "ถอนกำไรได้ ✅" if pnl > 0 else "ยังไม่มีกำไร"
        harvest_color = "green" if pnl > 0 else "gray"

        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("💼 เงินต้นทั้งหมด", f"${invested:,.2f}")
        m2.metric("📈 มูลค่าพอร์ตปัจจุบัน", f"${current_value:,.2f}")
        m3.metric("💰 กำไรสะสม", f"${pnl:,.2f}", delta=f"{pnl_pct:+.1f}%")

        # สรุปสถานะแบบเร็ว
        if current_price >= tp_price:
            st.success(f"🔥 ถึงเป้าหมาย {target_pct}% แล้ว! พิจารณาขายเพื่อทำกำไร")
        elif current_price < sl_price:
            st.error(f"🚨 ราคาหลุดจุดคัทตัดขาดทุน (${sl_price:.4f})")
        else:
            st.info(f"⏳ อีก ${(tp_price - current_price):.4f} จะถึงเป้าหมายที่ตั้งไว้")

        # จัดเตรียมข้อมูลตาราง
        rows = [
            {
                "title": "💰 ปิดดีลขายทั้งหมด",
                "price": f"${current_price:.4f}",
                "value": f"${current_value:,.2f}",
                "profit": f"${pnl:+,.2f}",
                "profit_pct": f"{pnl_pct:+.1f}%",
                "profit_pos": pnl >= 0,
                "badge": "Cash Out",
                "badge_color": "green" if pnl >= 0 else "gray",
                "note": "ขายคืนทั้งหมดทั้งต้นและกำไร",
            },
            {
                "title": f"🎯 ถือรอเป้าหมาย {target_pct}%",
                "price": f"${tp_price:.4f}",
                "value": f"${target_value:,.2f}",
                "profit": f"${target_profit:+,.2f}",
                "profit_pct": f"{target_pct:+.1f}%",
                "profit_pos": True,
                "badge": "Waiting",
                "badge_color": "amber",
                "note": "เป้าหมายกำไรที่คุณตั้งไว้",
            },
            {
                "title": "🍃 เก็บเกี่ยวเฉพาะกำไร",
                "price": f"${current_price:.4f}",
                "value": f"${harvest_amount:,.2f}",
                "profit": "ดึงกำไรออกมาใช้",
                "profit_pct": f"{pnl_pct:+.1f}%",
                "profit_pos": pnl > 0,
                "badge": harvest_badge,
                "badge_color": harvest_color,
                "note": "ดึงเงินกำไรออก แต่รักษาเงินต้นไว้",
            },
        ]

        # แสดงผลตาราง HTML
        html_key = f"key_{cost}_{shares}_{current_price}_{target_pct}"
        html = build_strategy_html(rows, highlight_idx=-1, key=html_key)
        components.html(html, height=350, scrolling=False)

    else:
        st.warning("👈 กรอกต้นทุนและจำนวนหุ้นเพื่อเริ่มการวิเคราะห์")

if __name__ == "__main__":
    st.set_page_config(page_title="Smart Guide", layout="centered")
    render_smart_guide()
