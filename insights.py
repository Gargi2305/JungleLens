from openai import OpenAI

def generate_insights(products, category_name="this category"):
    if not products:
        return "No products found to analyze."

    client = OpenAI()

    product_lines = []
    for p in products:
        product_lines.append(
            f"Rank #{p['rank']}: {p['title']} | Price: ${p['price']} | "
            f"Rating: {p['rating'] or 0}★ | Reviews: {p['reviews']:,} | "
            # f"Est. Monthly Revenue: ${p['monthly_revenue']:,.0f}"
            f"Est. Monthly Revenue: ${((p['monthly_revenue'] or 0)):,.0f}"
        )
    product_text = "\n".join(product_lines)

    total_market = sum(p['monthly_revenue'] or 0 for p in products)
    valid_prices = [p['price'] for p in products if p['price'] and p['price'] > 0]
    avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 0
    top3_revenue = sum(p['monthly_revenue'] or 0 for p in products[:3])
    top3_pct = (top3_revenue / total_market * 100) if total_market > 0 else 0

    # --- Call 1: Core market insights ---
    r1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a sharp Amazon market analyst. Be concise, specific, data-driven. Use markdown headers."},
            {"role": "user", "content": f"""Analyze these top products in {category_name}:

{product_text}

Total market: ${total_market:,.0f}/month | Avg price: ${avg_price:.2f} | Top 3 share: {top3_pct:.0f}%

Provide:
### Market Opportunity Score
Rate /10 with one sentence why.

### Price Sweet Spot
What price range to target and why.

### Competition Level
Easy / Medium / Hard with 2-sentence reasoning.

### Top 3 Market Insights
Numbered, each 1 sentence, data-backed.

Be direct. No fluff. Do not use any emojis."""}
        ],
        temperature=0.7, max_tokens=500
    )

    # --- Call 2: Market gap analysis ---
    r2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an Amazon market gap expert. Find real opportunities others miss."},
            {"role": "user", "content": f"""Given these top 10 products in {category_name}:

{product_text}

Identify:
### Market Gap
What price range, feature, or customer segment is underserved? Be specific with numbers.

### Competitor Weaknesses
Pick 2-3 top products. What specific weakness can a new seller exploit? (Look at ratings below 4.5, missing features in titles, price gaps)

### Entry Strategy
One specific, actionable move a new seller should make to win this market.

Be ruthlessly specific. No generic advice. Do not use any emojis."""}
        ],
        temperature=0.7, max_tokens=500
    )

    # --- Call 3: Listing blueprint ---
    r3 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Pixii listing optimization expert. You help Amazon sellers write listings that convert."},
            {"role": "user", "content": f"""Based on the top 10 products in {category_name}:

{product_text}

Generate a listing blueprint for a NEW seller entering this market:

### Listing Blueprint
**Title must include keywords:** (list 4-5 exact keywords from top sellers)
**Price to launch at:** (specific number, undercut strategy)
**Lead image must show:** (2-3 specific visual elements that top sellers use)
**Bullet point 1 must highlight:** (top buying driver)
**Review target before scaling ads:** (specific number based on competition)

### Visual Strategy (for Pixii)
What should the listing LOOK like to beat the competition? Describe:
- Hero image style
- Lifestyle image concept
- Key text overlay to include

Keep it punchy and actionable. Do not use any emojis."""}
        ],
        temperature=0.7, max_tokens=500
    )

    return (
        r1.choices[0].message.content,
        r2.choices[0].message.content,
        r3.choices[0].message.content
    )

