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
        await page.wait_for_selector(".btn-insert")
        
        # Open Add Modal
        await page.click(".btn-insert")
        await asyncio.sleep(0.5)
        
        # Type "Aluno" (default), check if Guardian section is visible
        await page.screenshot(path="/home/jules/verification/pessoas_add_aluno.png")
        
        # Check the guardian checkbox
        await page.check('#addHasGuardian')
        await asyncio.sleep(0.3)
        await page.screenshot(path="/home/jules/verification/pessoas_guardian_fields.png")
        
        # Fill data with phone mask test
        await page.fill('input[name="phone"]', "11988887777")
        await page.fill('input[name="guardian_phone"]', "11911112222")
        await page.screenshot(path="/home/jules/verification/pessoas_phone_mask.png")
        
        # Switch to Professor and check if Guardian section disappears
        await page.select_option('select[name="type"]', value="teacher")
        await asyncio.sleep(0.3)
        await page.screenshot(path="/home/jules/verification/pessoas_teacher_no_guardian.png")
        
        # Close modal and filter to see ID
        await page.click(".close-custom")
        await page.click("#filterBtn")
        await asyncio.sleep(0.5)
        await page.screenshot(path="/home/jules/verification/pessoas_table_with_id.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
