import re
from playwright.async_api import async_playwright

async def fetch_product_price(url: str, css_selector: str) -> float:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            element = await page.wait_for_selector(css_selector, timeout=5000)
            raw_text = await element.inner_text()
            clean_price = re.sub(r"[^\d.]", "", raw_text.replace(",", ""))
            return float(clean_price)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
        finally:
            await browser.close()