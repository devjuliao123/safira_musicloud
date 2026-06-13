import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Login
        await page.goto("http://127.0.0.1:5000/entrar")
        await page.fill('input[name="username"]', "adm")
        await page.fill('input[name="password"]', "adm")
        await page.click('button[type="submit"]')
        await page.wait_for_url("http://127.0.0.1:5000/menu")
        
        # Navigate to Pessoas
        await page.goto("http://127.0.0.1:5000/pessoas")
        await page.wait_for_selector("#filterBtn")
        
        # Click Filter to show data
        await page.click("#filterBtn")
        await asyncio.sleep(1) # Wait for JS render
        
        await page.screenshot(path="/home/jules/verification/pessoas_new_ui.png")
        
        # Test dropdown
        await page.click(".dropdown button")
        await asyncio.sleep(0.5)
        await page.screenshot(path="/home/jules/verification/pessoas_dropdown.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
