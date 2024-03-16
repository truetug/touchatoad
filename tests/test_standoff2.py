import os
import sys
import pytest
import asyncio
import pydantic

from playwright.async_api import async_playwright

#pytestmark = pytest.mark.anyio


URL = "https://store.standoff2.com/"
PATH = "/api/v1/accounts"


class User(pydantic.BaseModel):
    name: str
    uid: int
    avatar: str
    rctoken: str | None = None


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_userdata():
    user_id = os.environ.get("USER_ID")
    if not user_id:
        assert False

    await process(user_id)


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
        # Находим элемент с плейсхолдером
        await page.get_by_placeholder("ID").fill(user_id)
        # Находим элемент кнопки
        await page.get_by_role("button").filter(has_text="Искать").click()
    
    response = await response_info.value
    if response.status != 200:
        print("Process failed")
        print(response.request.method, response.request.url)
        print(response.status)
        print(await response.text())
    else:
        user = User.model_validate(await response.json())
        with open("result.json", "w") as fp:
            user.rctoken = response.request.headers["rctoken"]
            data = user.model_dump_json()
            print(data)
            fp.write(data)

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
