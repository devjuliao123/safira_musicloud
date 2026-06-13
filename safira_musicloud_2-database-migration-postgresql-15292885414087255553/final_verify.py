import asyncio
from playwright.async_api import async_playwright
import os

async def final_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 1. Login
        await page.goto("http://localhost:5000/entrar")
        await page.fill("input[name='username']", "adm")
        await page.fill("input[name='password']", "adm")
        await page.click("button[type='submit']")
        
        # 2. Menu Dashboard
        await page.wait_for_url("**/menu")
        await page.screenshot(path="verification/final_menu.png")
        
        # 3. People - Add and Verify Uppercase
        await page.goto("http://localhost:5000/pessoas")
        await page.click("button:has-text('Inserir')")
        await page.wait_for_selector("#addModal", state="visible")
        
        await page.fill("#addModal input[name='name']", "joão da silva")
        await page.select_option("#addModal select[name='type']", "student")
        await page.fill("#addModal input[name='email']", "joao@musica.com")
        await page.fill("#addModal input[name='phone']", "11988887777")
        await page.fill("#addModal input[name='cpf']", "123.456.789-01")
        
        await page.click("#addModal button:has-text('SALVAR')")
        
        # Wait for snackbar
        await page.wait_for_selector(".flash-messages-container .alert-success")
        await page.screenshot(path="verification/final_people_added.png")
        
        # Verify text is uppercase in table (after filtering)
        await page.fill("#searchInput", "joão")
        await page.click("#filterBtn")
        await page.wait_for_selector("tr.fade-in")
        
        name_text = await page.locator("tr.fade-in strong").first.inner_text()
        print(f"Name in table: {name_text}")
        
        # 4. Finance - Check summary
        await page.goto("http://localhost:5000/financeiro")
        await page.screenshot(path="verification/final_finance.png")
        
        await browser.close()

if __name__ == "__main__":
    if not os.path.exists("verification"):
        os.makedirs("verification")
    asyncio.run(final_verification())
