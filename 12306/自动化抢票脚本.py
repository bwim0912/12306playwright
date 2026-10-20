import time
import random
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # 打开登录页扫码
    page.goto('https://kyfw.12306.cn/otn/resources/login.html', wait_until="domcontentloaded")
    scan_tab = page.locator(".login-hd-account a")
    scan_tab.click()
    print("请手动用12306APP扫码登录")

    link_for_ticket = page.locator("#link_for_ticket")
    print("等待扫码登录中...")
    link_for_ticket.wait_for(state="visible", timeout=120000)
    print("登录成功")

    # 监听在点击车票预订后是否存在新页面（当前页跳转）
    with page.expect_navigation(timeout=10000):
        link_for_ticket.click()

    # 等待出发地输入框出现
    page.wait_for_selector("#fromStationText", state="visible", timeout=15000)
    print("已成功进入车票查询页面")

    # 出发地输入
    from_station = page.locator("#fromStationText")
    from_station.click()
    from_station.press_sequentially("北京", delay=150)
    page.wait_for_timeout(1000)  # 等待下拉菜单渲染
    page.wait_for_selector("ul >> [data='BJP']", state="attached", timeout=5000)
    page.locator("ul >> [data='BJP']").first.click(force=True)
    print("出发地已填入: 北京")

    # 到达地输入（同理）
    to_station = page.locator("#toStationText")
    to_station.click()
    to_station.press_sequentially("广州", delay=150)
    page.wait_for_timeout(1000)
    page.wait_for_selector("ul >> [data='GZQ']", state="attached", timeout=5000)
    page.locator("ul >> [data='GZQ']").first.click(force=True)
    print("目的地已填入: 广州")

    # 出发日期输入
    train_date = page.locator("input#train_date")
    train_date.click()
    train_date.fill("")
    train_date.fill("2026-10-06")
    page.keyboard.press("Enter")
    time.sleep(random.uniform(0.5, 1.0))
    print("出发日期已填入: 2026-10-06")





    input("")