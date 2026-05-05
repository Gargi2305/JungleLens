

import requests
from bs4 import BeautifulSoup
import re
import time
import random

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
]

def bsr_to_monthly_sales(rank):
    if rank <= 1:    return 45000
    elif rank <= 2:  return 30000
    elif rank <= 3:  return 22000
    elif rank <= 5:  return 15000
    elif rank <= 7:  return 10000
    elif rank <= 10: return 7000
    else:            return 3000

def clean_price(price_str):
    if not price_str: return 0.0
    price_str = re.sub(r'[^\d.]', '', str(price_str).replace(',', ''))
    try:    return float(price_str)
    except: return 0.0

def clean_reviews(review_str):
    if not review_str: return 0
    numbers = re.findall(r'[\d,]+', str(review_str))
    if numbers: return int(numbers[0].replace(',', ''))
    return 0

def fetch_with_scraperapi(url, scraper_api_key):
    api_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}&render=true&country_code=us"
    resp = requests.get(api_url, timeout=60)
    resp.raise_for_status()
    return resp

def fetch_direct(url):
    headers = random.choice(HEADERS_LIST)
    session = requests.Session()
    try:
        session.get("https://www.amazon.com", headers=headers, timeout=10)
        time.sleep(random.uniform(1.5, 2.5))
    except:
        pass
    resp = session.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp

def parse_products(soup):
    products = []
    seen_asins = set()
    rank = 1

    items = []
    for sel in ['div[data-asin]', 'li.zg-item-immersion', 'div.zg-item', '[data-asin]']:
        candidates = soup.select(sel)
        valid = [i for i in candidates if i.get('data-asin') and len(i.get('data-asin','')) > 5]
        if len(valid) >= 3:
            items = valid
            break

    for item in items:
        if rank > 10: break
        try:
            asin = item.get('data-asin', '')
            if not asin or asin in seen_asins or len(asin) < 5:
                continue
            seen_asins.add(asin)

            title = f"Product {rank}"
            for ts in ['._cDEzb_p13n-sc-css-line-clamp-3_g3dy1', '.p13n-sc-truncate-desktop-type2',
                       '.p13n-sc-truncated', 'span[class*="truncate"]', 'a span', 'span']:
                el = item.select_one(ts)
                if el and len(el.get_text(strip=True)) > 5:
                    title = el.get_text(strip=True)
                    break

            price = 0.0
            for ps in ['._cDEzb_p13n-sc-price_3mJ9Z', '.p13n-sc-price', 'span.a-color-price',
                       'span[class*="price"]', '.a-price .a-offscreen']:
                el = item.select_one(ps)
                if el:
                    p = clean_price(el.get_text(strip=True))
                    if p > 0: price = p; break

            rating = 0.0
            for rs in ['span.a-icon-alt', 'i[class*="star"] span']:
                el = item.select_one(rs)
                if el:
                    m = re.search(r'(\d+\.?\d*)', el.get_text())
                    if m: rating = float(m.group(1)); break

            reviews = 0
            for rs in ['span.a-size-small', 'a[href*="customerReviews"]', 'span[class*="review"]']:
                el = item.select_one(rs)
                if el:
                    r = clean_reviews(el.get_text(strip=True))
                    if r > 0: reviews = r; break

            img_el = item.select_one('img')
            image = ''
            if img_el:
                image = img_el.get('src') or img_el.get('data-src') or ''

            monthly_sales = bsr_to_monthly_sales(rank)
            price = price if price > 0 else None

            monthly_revenue = None
            if price:
                monthly_revenue = round(monthly_sales * price, 2)

            products.append({
                'rank': rank, 'asin': asin,
                'title': title[:80] + ('...' if len(title) > 80 else ''),
                'price': price, 'rating': rating, 'reviews': reviews,
                'monthly_sales': monthly_sales, 'monthly_revenue': monthly_revenue,
                'image': image,
            })
            rank += 1
        except:
            continue

    return products

def scrape_best_sellers(url, scraper_api_key=None):
    if scraper_api_key and scraper_api_key.strip():
        try:
            resp = fetch_with_scraperapi(url, scraper_api_key.strip())
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = parse_products(soup)

            if not products:
              return [], "Invalid or empty category page (Amazon returned no products). Try another URL."

            return products, None
        except Exception as e:
            pass

    for attempt in range(2):
        try:
            resp = fetch_direct(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = parse_products(soup)
            if not products:
              return [], "Invalid or empty category page (Amazon returned no products). Try another URL."
            return products, None
            time.sleep(2)
        except:
            time.sleep(2)

    return [], "Amazon is blocking direct requests. Please add a free ScraperAPI key in the sidebar (free at scraperapi.com)."