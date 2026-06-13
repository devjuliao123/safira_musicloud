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
        
        await page.screenshot(path="/home/jules/verification/menu_with_room.png")
        
        # Navigate to Agenda
        await page.goto("http://127.0.0.1:5000/agenda")
        await page.wait_for_selector("#filterBtn")
        
        # Add new schedule with room
        await page.click(".btn-insert")
        await page.select_option('select[name="teacher_id"]', index=1)
        await page.select_option('select[name="day_of_week"]', value="segunda-feira")
        await page.fill('input[name="start_time"]', "10:00")
        await page.fill('input[name="end_time"]', "11:00")
        await page.fill('input[name="course_name"]', "Bateria")
        await page.fill('input[name="room"]', "Sala de Percussão")
        await page.screenshot(path="/home/jules/verification/agenda_add_modal_with_room.png")
        await page.click('#addModal button[type="submit"]')
        
        # Filter and check table
        await page.wait_for_selector("#filterBtn")
        await page.fill('#searchInput', "Bateria")
        await page.click("#filterBtn")
        await asyncio.sleep(1)
        await page.screenshot(path="/home/jules/verification/agenda_table_with_room.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
