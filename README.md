# JungleLens 
AI-powered Amazon Market Intelligence Engine

🔗 Live App: https://junglelens.streamlit.app

---

## What is JungleLens?

JungleLens is an AI-powered tool that analyzes Amazon Best Sellers pages to help sellers understand:

- Market size (estimated monthly revenue)
- Competition level
- Pricing gaps
- Product-level insights
- Actionable listing strategies

Built to answer one question quickly:

> “Is this market worth entering?”

---

##  Demo

1. Paste an Amazon Best Sellers URL  
2. Click **Analyze Market**  
3. Get:
   -  Market size & revenue estimates  
   -  Product breakdown  
   -  AI-generated insights  
   -  Entry strategy & gaps  

---

##  Key Features

- **Automated scraping** of Amazon Best Sellers pages  
- **Revenue estimation** using BSR-based modeling  
- **AI insights** using LLMs (OpenAI)  
- **Market gap detection** and strategy generation  
- **Interactive dashboard** built with Streamlit  
- **Robust handling** of noisy / incomplete data  

---

##  Tech Stack

- **Frontend / UI:** Streamlit  
- **Backend:** Python  
- **AI:** OpenAI (LLM pipelines)  
- **Scraping:** Requests + BeautifulSoup + ScraperAPI  
- **Data:** Pandas  

---

##  How it Works

1. Scrapes top products from Best Sellers page  
2. Extracts:
   - price  
   - rating  
   - reviews  
   - rank  
3. Estimates:
   - monthly sales  
   - monthly revenue  
4. Sends structured data to LLM  
5. Generates:
   - market insights  
   - competitor analysis  
   - listing blueprint  

---

##  Limitations

- Revenue estimates are heuristic (BSR-based)  
- Amazon DOM structure may change  
- Requires API keys for full functionality  

---

##  Setup (Local)

```bash
git clone https://github.com/your-username/junglelens.git
cd junglelens
pip install -r requirements.txt
```

### Create .env
```
OPENAI_API_KEY=your_key
SCRAPER_API_KEY=your_key
```

### Run:
```
streamlit run app.py
```
---

##  Future Improvements

1. Multi-category comparison
2. Historical trend tracking
3. More accurate sales estimation
4.Shopify / Amazon integration
5. Batch analysis for multiple niches


### Author

Gargi Jain

