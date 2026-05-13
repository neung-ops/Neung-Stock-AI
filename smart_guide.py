import streamlit as st
import streamlit.components.v1 as components

TIPS = [
    "ขายหุ้นออกทันทีตอนนี้เลย ได้เงินจริงแน่นอน ไม่ต้องลุ้นอะไรอีก แต่ถ้าราคายังขึ้นต่อก็จะพลาดกำไรส่วนนั้นไป",
    "ยังไม่ขาย รอให้ราคาขึ้นถึงเป้าที่ตั้งไว้ก่อน ตัวเลขที่เห็นคือ 'ถ้าถึงเป้าจะได้เท่านี้' ยังไม่ได้เงินจริงจนกว่าจะขาย",
    "ขายหุ้นออกมาแค่พอได้เงินทุนคืน หุ้นที่เหลืออยู่ในพอร์ตถือว่าได้มาฟรี จะขึ้นหรือลงก็ไม่เจ็บตัว",
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
            <div class="cell-label">ขายที่ราคา</div>
            <div class="cell-value">{r['price']}</div>
          </div>
          <div class="col">
            <div class="cell-label">USD ที่ต้องขาย</div>
            <div class="cell-value">{r['value']}</div>
            {note_html}
          </div>
          <div class="col">
            <div class="cell-label">กำไรที่ได้เพิ่ม</div>
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
        <div>ทางเลือก</div><div>ขายที่ราคา</div>
        <div>USD ที่ต้องขาย</div><div>กำไรที่ได้เพิ่ม</div><div>ควรทำมั้ย?</div>
      </div>
      {rows_html}
    </div>
    """


def render_smart_guide(market_price: float = 0.0):
    st.write("---")
    st.header("🧠 ระบบช่วยตัดสินใจ")

    cost = shares = tp_price = sl_price = 0.0

    c1, c2 = st.columns(2)
    with c1:
        cost = st.number_input(
            "ต้นทุนต่อหุ้น ($) — ราคาที่ซื้อมาเฉลี่ย",
            value=0.0, step=0.0001, format="%.4f", key="sg_cost"
        )
    with c2:
        shares = st.number_input(
            "จำนวนหุ้นที่ถืออยู่",
            value=0.0, step=1e-10, format="%.10f", key="sg_shares"
        )

    # ถ้ามี market_price ส่งมาจากส่วนบน ไม่ต้องกรอกซ้ำ
    if market_price > 0:
        current_price = market_price
        st.info(f"📡 ราคาตลาดปัจจุบัน: **${current_price:.4f}** (ดึงจากระบบอัตโนมัติ)")
    else:
        current_price = st.number_input(
            "ราคาตลาดตอนนี้ ($)",
            value=0.0, format="%.4f", key="sg_market"
        )

    st.write("### อยากได้กำไรแค่ไหน?")
    plan_choice = st.radio(
        "เลือกเป้าหมาย:",
        ["นิดหน่อยก็พอ (+5%)", "พอดีๆ (+10%)", "รอให้ได้เยอะ (+20%)"],
        index=1, horizontal=True, key="sg_plan"
    )
    target_pct = 5.0 if "5%" in plan_choice else (10.0 if "10%" in plan_choice else 20.0)

    if cost > 0:
        tp_price = cost * (1 + target_pct / 100)
        sl_price = cost * 0.95

    if cost > 0 and shares > 0 and current_price > 0:
        invested      = cost * shares
        current_value = current_price * shares
        pnl           = current_value - invested
        pnl_pct       = (pnl / invested) * 100
        target_value  = tp_price * shares
        target_profit = target_value - invested

        # Summary
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("💼 ลงทุนไปทั้งหมด", f"${invested:,.2f}")
        m2.metric("📈 ถ้าขายตอนนี้ได้",  f"${current_value:,.2f}")
        m3.metric("💰 กำไร/ขาดทุน",      f"${pnl:,.2f}", delta=f"{pnl_pct:+.1f}%")

        # สถานะ
        st.write("---")
        if pnl_pct >= target_pct * 2:
            st.success(f"🔥 กำไรเกินเป้ามากแล้ว ({pnl_pct:.1f}%) ระวังราคาย้อนกลับ ควรพิจารณาล็อคกำไรได้เลย")
        elif current_price >= tp_price:
            st.success(f"✅ ถึงเป้าแล้ว! ราคาตอนนี้ ${current_price:.4f} ขายได้กำไร {pnl_pct:.1f}%")
        elif current_price < sl_price:
            st.error(f"🚨 ราคาต่ำกว่าจุดตัดขาดทุน (${sl_price:.4f}) ถือต่ออาจเสียมากกว่านี้")
        elif current_price < cost:
            st.warning(f"⚠️ ตอนนี้ขาดทุนอยู่ รอให้ราคาขึ้นอีก ${cost - current_price:.4f}/หุ้น ถึงจะเท่าทุน")
        else:
            st.info(f"⏳ กำไรอยู่แต่ยังไม่ถึงเป้า อีก ${tp_price - current_price:.4f}/หุ้น ถึงจะครบ {target_pct:.0f}%")

        # ชื่อแถว 2 เปลี่ยนตามสถานการณ์จริง
        if current_price >= tp_price:
            title_row2 = f"✅ ถึงเป้าแล้ว ขายได้เลย"
            note_row2  = ""
        else:
            title_row2 = f"⏳ รอให้ราคาขึ้นถึง ${tp_price:.4f}"
            note_row2  = "* ตัวเลขนี้จะได้จริงเมื่อราคาถึงเป้า"

        # badge + highlight ตามสถานการณ์
        if pnl_pct >= target_pct * 2:
            badges       = ["ล็อคกำไรได้เลย ✅", "เกินเป้าแล้ว",    "ทำได้ ✅"]
            badge_colors = ["green",              "amber",            "green"]
            highlight    = 0
        elif current_price >= tp_price:
            badges       = ["ขายได้เลย ✅",       "ถึงแล้ว ✅",       "ทำได้ ✅"]
            badge_colors = ["green",              "green",            "green"]
            highlight    = 0
        elif current_price < sl_price:
            badges       = ["แนะนำให้ขาย",        "เสี่ยงสูง",        "ทำไม่ได้ตอนนี้"]
            badge_colors = ["amber",              "gray",             "gray"]
            highlight    = 0
        elif current_price < cost:
            badges       = ["ขาดทุนถ้าขาย",       "รออีกนาน",         "ทำไม่ได้ตอนนี้"]
            badge_colors = ["gray",               "gray",             "gray"]
            highlight    = -1
        else:
            badges       = ["ได้กำไรนิดหน่อย",    "แนะนำ รอต่อ ✅",   "ลดความเสี่ยง"]
            badge_colors = ["amber",              "green",            "green"]
            highlight    = 1

        rows = [
            {
                "title":       "💰 ขายเลย เอาเงินออกมา",
                "price":       f"${current_price:.4f}",
                "value":       f"${current_value:,.2f}",
                "profit":      f"${pnl:+,.2f}",
                "profit_pct":  f"{pnl_pct:+.1f}%",
                "profit_pos":  pnl >= 0,
                "badge":       badges[0],
                "badge_color": badge_colors[0],
                "note":        "",
            },
            {
                "title":       title_row2,
                "price":       f"${tp_price:.4f}",
                "value":       f"${target_value:,.2f}",
                "profit":      f"${target_profit:+,.2f}",
                "profit_pct":  f"{target_pct:+.1f}%",
                "profit_pos":  True,
                "badge":       badges[1],
                "badge_color": badge_colors[1],
                "note":        note_row2,
            },
            {
                "title":       "🛡️ ขายแค่คืนทุน เหลือไว้ลุ้นฟรี",
                "price":       f"${cost:.4f}",
                "value":       f"${invested:,.2f}",
                "profit":      "ได้ทุนคืน",
                "profit_pct":  "+0.0%",
                "profit_pos":  True,
                "badge":       badges[2],
                "badge_color": badge_colors[2],
                "note":        "",
            },
        ]

        st.write("#### เปรียบเทียบทางเลือก")
        html_key = f"{cost}_{shares}_{current_price}_{target_pct}"
        html = build_strategy_html(rows, highlight, html_key)
        components.html(html, height=320, scrolling=False)

    else:
        st.warning("👈 กรอกตัวเลขด้านบนให้ครบก่อนนะครับ ระบบถึงจะแสดงผลได้")


if __name__ == "__main__":
    st.set_page_config(page_title="Smart Guide", page_icon="🧠", layout="centered")
    render_smart_guide()
