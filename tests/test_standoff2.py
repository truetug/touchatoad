import asyncio
import sys
import pydantic
from playwright.async_api import async_playwright


URL = "https://store.standoff2.com/"
PATH = "/api/v1/accounts"


class User(pydantic.BaseModel):
    name: str
    uid: int
    avatar: str


async def process(user_id: str) -> None:
    # Создаем экземпляр Playwright
    playwright = await async_playwright().start()

    # Создаем экземпляр Chrome
    browser = await playwright.firefox.launch()

    # Создаем экземпляр страницы
    page = await browser.new_page()

    # Переходим на страницу по урлу
    await page.goto(URL)
    async with page.expect_response(lambda x: PATH in x.url) as response_info:
        # Находим элемент с плейсхолдером ИНПУТ
        await page.get_by_placeholder("ID").fill(user_id)
        # Находим элемент кнопки
        await page.get_by_role("button").filter(has_text="Искать").click()
        
    response = await response_info.value
    user = User.parse_obj(await response.json())
    print(user)
    # print(response.request.headers)
    print(response.request.headers["rctoken"]) 

    # Закрываем браузер
    await browser.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("User ID required: python test.py <user_id>")
        exit(1)

    user_id = sys.argv[-1]

    # Запускаем функцию main
    asyncio.get_event_loop().run_until_complete(process(user_id))
    print("Done")
