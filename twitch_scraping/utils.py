import asyncio

from pyppeteer.page import Page


async def scroll_down(page: Page):
    await page.keyboard.down(key='End')
    await asyncio.sleep(1)
