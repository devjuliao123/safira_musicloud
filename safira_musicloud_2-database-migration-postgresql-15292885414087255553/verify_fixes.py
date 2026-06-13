import asyncio
from playwright.async_api import async_playwright
import os

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
        
        # Go to People and add someone to trigger flash
        await page.goto("http://127.0.0.1:5000/pessoas")
        await page.click('button:has-text("Inserir")')
        await page.fill('input[name="name"]', "VERIFICAR SNACKBAR")
        await page.select_option('select[name="type"]', value="student")
        await page.fill('input[name="cpf"]', "000.000.000-00")
        await page.click('button:has-text("SALVAR")')
        
        await asyncio.sleep(1)
        if not os.path.exists("verification"):
            os.makedirs("verification")
        await page.screenshot(path="verification/snackbar_centered.png")
        
        # Click Filter to show data and test dropdown
        await page.click("#filterBtn")
        await asyncio.sleep(2)
        
        dropdown_btns = await page.query_selector_all(".dropdown button")
        if dropdown_btns:
            await dropdown_btns[0].click()
            await asyncio.sleep(0.5)
            await page.screenshot(path="verification/dropdown_visible_fix.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
