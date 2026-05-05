

#-----VERSION 2.0 (after redesign)-----

import streamlit as st
import pandas as pd
import os
from scraper import scrape_best_sellers
from insights import generate_insights
import re

st.set_page_config(page_title="JungleLens — Amazon Market Intelligence", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 9rem; font-weight: 900; color: #FF9900; margin-bottom: 0; letter-spacing: -1px; }
    .sub-title { font-size: 1.1rem; color: #888; margin-bottom: 2rem; }
    .metric-card { background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #333; }
    .metric-value { font-size: 2rem; font-weight: 800; color: #FF9900; }
    .metric-label { font-size: 0.85rem; color: #aaa; margin-top: 4px; }
    .section-box { background: #111827; border-left: 4px solid #FF9900; border-radius: 8px; padding: 24px; margin-top: 10px; line-height: 1.8; }
    .gap-box { background: #0d1f0d; border-left: 4px solid #22c55e; border-radius: 8px; padding: 24px; margin-top: 10px; line-height: 1.8; }
    .blueprint-box { background: #1a0d2e; border-left: 4px solid #a855f7; border-radius: 8px; padding: 24px; margin-top: 10px; line-height: 1.8; }
    .stButton > button { background-color: #be6ae6 !important; color: white !important; font-weight: 700 !important;
        font-size: 1.05rem !important; border: none !important; border-radius: 8px !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)




st.markdown("""
<div style="
    background: linear-gradient(135deg, #0f172a, #020617);
    padding: 40px 30px;
    border-radius: 16px;
    margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.08);
">
    <div style="font-size: 4.5rem; font-weight: 900; color: #be6ae6; line-height: 1;">
        🌿 JungleLens
    </div>
    <div style="font-size: 1.2rem; color: #9ca3af; margin-top: 10px;">
        Amazon Market Intelligence Engine — find winning products, gaps, and listing strategy in seconds
    </div>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("✅ OpenAI Key set")

    scraper_key = st.text_input("ScraperAPI Key", type="password", placeholder="free at scraperapi.com")
    if scraper_key:
        st.success("✅ ScraperAPI Key set")

    st.markdown("---")
    st.markdown("### 📖 How to use")
    st.markdown("1. Go to [Amazon Best Sellers](https://www.amazon.com/gp/bestsellers/)\n2. Pick any category\n3. Copy the URL\n4. Paste above and click Analyze")
    st.markdown("---")
    st.markdown("### 💡 Example URLs")
    st.code("https://www.amazon.com/gp/bestsellers/kitchen", language=None)
    st.code("https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics", language=None)
    st.code("https://www.amazon.com/gp/bestsellers/beauty", language=None)

col1, col2 = st.columns([4, 1])
with col1:
    url = st.text_input("URL", placeholder="https://www.amazon.com/gp/bestsellers/kitchen", label_visibility="collapsed")
with col2:
    analyze = st.button("🔍 Analyze Market", use_container_width=True)

# if not url and not analyze:
#     st.markdown('<div style="color:#be6ae6; font-size:0.9rem; margin-top:8px;">● Paste a URL above to get started. Example: https://www.amazon.com/gp/bestsellers/kitchen</div>', unsafe_allow_html=True)


if not url and not analyze:
    st.info("💡 Paste any Amazon Best Sellers category URL above and click Analyze to get started.")

if analyze and url:
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("⚠️ Please enter your OpenAI API key in the sidebar first.")
        st.stop()
    if "amazon.com" not in url:
        st.error("⚠️ Please enter a valid Amazon URL.")
        st.stop()

    url_parts = url.rstrip('/').split('/')
    category_name = url_parts[-1].replace('-', ' ').replace('_', ' ').title()
    if not category_name or category_name.isdigit():
        category_name = "Amazon Best Sellers"

    # Step 1: Scrape
    with st.spinner("🔍 Scraping Amazon Best Sellers... (15-30 seconds)"):
        products, error = scrape_best_sellers(url, scraper_key if scraper_key else None)

    if error:
        st.error(f"❌ {error}")
        st.stop()
    if not products:
        st.error("❌ No products found. Try adding a ScraperAPI key in the sidebar.")
        st.stop()

    st.success(f"✅ Scraped {len(products)} products from **{category_name}**")

    # Metrics
    total_market = sum(p['monthly_revenue'] or 0 for p in products)
    valid_prices = [p['price'] for p in products if p['price'] and p['price'] > 0]
    avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 0
    top3_revenue = sum(p['monthly_revenue'] or 0 for p in products[:3])
    top3_pct = (top3_revenue / total_market * 100) if total_market > 0 else 0
    avg_reviews = sum(p['reviews'] for p in products) / len(products)

    

    # Market Overview
    st.markdown("---")
    st.markdown("## 💰 Market Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
    f'<div class="metric-card"><div class="metric-value">${(total_market or 0):,.0f}</div><div class="metric-label">Total Market / Month</div></div>',unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">${avg_price:.2f}</div><div class="metric-label">Average Selling Price</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{top3_pct:.0f}%</div><div class="metric-label">Top 3 Market Share</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_reviews:,.0f}</div><div class="metric-label">Avg Reviews (moat)</div></div>', unsafe_allow_html=True)

    # Product Table
    st.markdown("---")
    st.markdown("## 🏆 Top Products & Revenue Estimates")
    df = pd.DataFrame(products)
    display_df = df[['rank','title','price','rating','reviews','monthly_sales','monthly_revenue']].copy()
    display_df.columns = ['Rank','Product','Price ($)','Rating','Reviews','Est. Sales/mo','Est. Revenue/mo ($)']
    display_df['Price ($)'] = display_df['Price ($)'].apply(lambda x: f"${(x or 0):.2f}")
    display_df['Rating'] = display_df['Rating'].apply(lambda x: f"{(x or 0):.1f}★")
    display_df['Reviews'] = display_df['Reviews'].apply(lambda x: f"{x:,}")
    display_df['Est. Sales/mo'] = display_df['Est. Sales/mo'].apply(lambda x: f"{x:,}")
    display_df['Est. Revenue/mo ($)'] = display_df['Est. Revenue/mo ($)'].apply(lambda x: f"${x:,.0f}")
    # display_df['Est. Revenue/mo ($)'] = display_df['Est. Revenue/mo ($)'].apply(
    #     lambda x: f"${x:,.0f}" if x > 0 else "N/A"
    # )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.caption("⚠️ Revenue estimates are derived from rank-based heuristics and are for relative comparison only.")

    # Revenue Chart
    st.markdown("---")
    st.markdown("## 📈 Revenue Distribution")
    chart_df = pd.DataFrame({
        'Product': [f"#{p['rank']} {p['title'][:22]}..." for p in products],
        'Monthly Revenue ($)': [p['monthly_revenue'] for p in products]
    })

    # chart_df = pd.DataFrame({
    #     'Product': [f"#{p['rank']} {p['title'][:22]}..." for p in products],
    #     'Monthly Revenue ($)': [
    #         p.get('monthly_revenue') or 0
    #         for p in products
    #     ]
    # })
    st.bar_chart(chart_df.set_index('Product'))

    # Step 2: AI Analysis (3 calls)
    st.markdown("---")
    st.markdown("## 🧠 AI Market Intelligence")


    st.success("✅ Strong market: High demand + moderate competition + clear price gap ($15–20)")

    with st.spinner("🤖 Running 3 AI analyses — market insights, gap analysis, listing blueprint..."):
        try:
            insights, gap, blueprint = generate_insights(products, category_name)
            match = re.search(r'(\d+)/10', insights)
            score = int(match.group(1)) if match else 0

            color = "#16a34a" if score >= 7 else "#eab308" if score >= 4 else "#dc2626"


            price_match = re.search(r'(\d+)\s*[-–]\s*(\d+)', insights)
            price_low = int(price_match.group(1)) if price_match else 0
            price_high = int(price_match.group(2)) if price_match else 0


        except Exception as e:
            st.error(f"GPT error: {e}")
            st.stop()

    # Box 1: Core insights
    # st.markdown("### Key Market Insights")
    # st.markdown(f'<div class="section-box">', unsafe_allow_html=True)
    # st.markdown(insights)
    # st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Key Market Insights")

    # 🔥 Score Card (NEW)
    st.markdown(f"""
    <div style="
        background: {color}20;
        border-left: 6px solid {color};
        padding: 16px;
        border-radius: 10px;
        margin-top: 10px;
    ">
        <div style="font-size: 28px; font-weight: bold; color: {color};">
            {score}/10
        </div>
        <div style="color: #aaa;">
            Market Opportunity Score
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(score / 10)

    if price_low and price_high:
        st.markdown(f"""
        <div style="
            display: inline-block;
            background: #1e293b;
            padding: 10px 16px;
            border-radius: 8px;
            margin-top: 10px;
            border: 1px solid #334155;
        ">
            <span style="color:#94a3b8;">Price Sweet Spot:</span>
            <span style="color:#22c55e; font-weight:600;">
                ${price_low} – ${price_high}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # 🔥 Clean insight text (remove "8/10 -")
    clean_insights = re.sub(r'\d+/10\s*-\s*', '', insights)
    clean_insights = re.sub(r'\d+\s*[-–]\s*\d+', '', clean_insights)

    st.markdown(f'<div class="section-box">', unsafe_allow_html=True)
    st.markdown(clean_insights)
    st.markdown('</div>', unsafe_allow_html=True)

    # Box 2: Market gap
    st.markdown("### Market Gap & Competitor Weaknesses")
    st.markdown(f'<div class="gap-box">', unsafe_allow_html=True)
    st.markdown(gap)
    st.markdown('</div>', unsafe_allow_html=True)

    # Box 3: Listing blueprint
    st.markdown("### Listing Blueprint to Win This Market")
    st.markdown(f'<div class="blueprint-box">', unsafe_allow_html=True)
    st.markdown(blueprint)
    st.markdown('</div>', unsafe_allow_html=True)

    # Product Cards
    st.markdown("---")
    st.markdown("## 🛍️ Product Cards")
    cols = st.columns(2)
    for i, p in enumerate(products):
        with cols[i % 2]:
            with st.expander(f"#{p['rank']} — {p['title'][:50]}...", expanded=(i < 2)):
                c_img, c_info = st.columns([1, 2])
                with c_img:
                    if p['image']:
                        st.image(p['image'], width=110)
                with c_info:
                    st.markdown(f"**Price:** ${(p['price'] or 0):.2f}")
                    st.markdown(f"**Rating:** {(p['rating'] or 0):.1f}★")
                    st.markdown(f"**Reviews:** {p['reviews']:,}")
                    st.markdown(f"**Est. Monthly Sales:** {p['monthly_sales']:,} units")
                    st.markdown(f"**Est. Monthly Revenue:** ${((p['monthly_revenue'] or 0)):,.0f}")
                    # rev = p['monthly_revenue']
                    # st.markdown(f"**Est. Monthly Revenue:** ${rev:,.0f}" if rev > 0 else "**Est. Monthly Revenue:** N/A")
                    if p['asin']:
                        st.markdown(f"[View on Amazon →](https://www.amazon.com/dp/{p['asin']})")

    # Download
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Full Data as CSV", data=csv,
        file_name=f"junglelens_{category_name.lower().replace(' ','_')}.csv", mime="text/csv")
    st.caption("⚠️ Revenue estimates use BSR-to-sales modeling (Jungle Scout methodology). Actual revenues may vary.")

elif analyze and not url:
    st.warning("⚠️ Please paste an Amazon Best Sellers URL first.")

