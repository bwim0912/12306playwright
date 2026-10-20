import requests
import json
from stations_data import STATIONS
import execjs
from playwright.sync_api import sync_playwright
from lxml import etree
import time
import random
import re
import sys

# 当前页跳转 → 用 expect_navigation
#
# 新标签页打开 → 用 expect_page

#2026-09-26

TICKET_ADULT= 'ADULT'
TICKET_STUDENT = 'STUDENT'

STATION_MAP = {name: code for name, code, _, _ in STATIONS}


def get_station_code(station_name):
    return STATION_MAP.get(station_name)


# ---------- 交互输入 ----------
from_station = input("请输入起始站:")
from_station_code = get_station_code(from_station)
if from_station_code is None:
    print("未查询到该车站!")
    #终止程序
    raise SystemExit
print(from_station_code)

to_station = input("请输入终点站:")
to_station_code = get_station_code(to_station)
if to_station_code is None:
    print("未查询到该车站!")
    #终止程序
    raise SystemExit
print(to_station_code)

print("按照如下填写时间--->年份-月份-日期")
train_date = input("请输入乘车时间:")

print("成人票填写1，学生票填写2.")
choice = input("请填写: ").strip()

if choice == '1':
    category = TICKET_ADULT
elif choice == '2':
    category = TICKET_STUDENT
else:
    print("不存在该票类")
    raise SystemExit


# ---------- 请求 ----------
def get_result():
    cookies = {
        '_uab_collina': '178975283745524271395063',
        'JSESSIONID': '959419B7B21F96EB00D5D1A110466FE7',
        'SF_cookie_2': '28976421',
        'BIGipServerotn': '2880570378.38945.0000',
        'guidesStatus': 'off',
        'highContrastMode': 'defaltMode',
        'cursorStatus': 'off',
        'BIGipServerpassport': '988283146.50215.0000',
        '_jc_save_fromStation': '%u5E7F%u5DDE%2CGZQ',
        '_jc_save_toStation': '%u60E0%u5DDE%2CHCQ',
        '_jc_save_fromDate': '2026-09-25',
        '_jc_save_toDate': '2026-09-19',
        '_jc_save_wfdc_flag': 'dc',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'If-Modified-Since': '0',
        'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'leftTicketDTO.train_date':  train_date,
        'leftTicketDTO.from_station': from_station_code,
        'leftTicketDTO.to_station':   to_station_code,
        'purpose_codes':              category,
    }
    # params = {
    #     #     'leftTicketDTO.train_date':  '2026-10-07',
    #     #     'leftTicketDTO.from_station': 'HCQ',
    #     #     'leftTicketDTO.to_station':'GZQ',
    #     #     'purpose_codes':'ADULT',
    #     # }

    resp = requests.get(
        'https://kyfw.12306.cn/otn/leftTicket/queryG',
        params=params, cookies=cookies, headers=headers,
    )
    try:
        respond = resp.json()
        data=respond['data']
        return data
    finally:
        resp.close()


def get_decode_result(data):
    with open("result_code.js",mode="r",encoding="utf-8") as f:
        js_code = f.read()
    ctx = execjs.compile(js_code)
    decoded = ctx.call('cN',data['result'],data['map'])
    return decoded


if __name__ == '__main__':
    data=get_result()
    if data and data.get('flag')=='1':
        decoded=get_decode_result(data)
        result=[]
        for item in decoded:
            d=item['queryLeftNewDTO']
            result.append((
                d['station_train_code'],   # 车次
                d['from_station_name'],    # 出发站
                d['to_station_name'],      # 到达站
                d['start_time'],           # 发车时间
                d['arrive_time'],          # 到达时间
                d['lishi'],                # 历时
                d['tz_num'],               # 特等座
                d['zy_num'],               # 一等
                d['ze_num'],               # 二等
                d['rw_num'],               # 软卧
                d['yw_num'],               # 硬卧
                d['yz_num'],               # 硬座
                d['wz_num'],               # 无座
            ))

        for idx, row in enumerate(result, start=1):
            print(f"-----------------------第{idx}辆车-----------------------")
            print(f"车次: {row[0]}")
            print(f"出发站: {row[1]}")
            print(f"到达站: {row[2]}")
            print(f"发车: {row[3]}")
            print(f"到达: {row[4]}")
            print(f"历时: {row[5]}")
            print(f"特等座: {row[6]}")
            print(f"一等: {row[7]}")
            print(f"二等: {row[8]}")
            print(f"软卧: {row[9]}")
            print(f"硬卧: {row[10]}")
            print(f"硬座: {row[11]}")
            print(f"无座: {row[12]}")

        data = {}
        print("")
        print("")
        chosen_idx_train = input("请输入车序号:").strip()
        num = int(chosen_idx_train)
        if 1 <= num <= len(result):
            row = result[num - 1]
            idx = num
            print(f"你选择的是:{row[0]}车次,由{row[1]}-->{row[2]},出发时间为{row[3]},到达时间为{row[4]}")
            print(
                f"车票信息为:特等座:{row[6]},一等座:{row[7]},二等座:{row[8]},软卧:{row[9]},硬卧:{row[10]},硬座:{row[11]},无座:{row[12]}")
            seat = input("请输入要查询的座位类型（特等座/一等座/二等座/软卧/硬卧/硬座/无座）：").strip()

            data["车次"] = row[0]
            data["出发站"] = row[1]
            data["到达站"] = row[2]
            data["发车"] = row[3]
            data["到达"] = row[4]
            data["历时"] = row[5]
            data["座位类型"] = seat

            if seat == "特等座":
                data["余票"] = row[6]
                print(f"特等座余票：{row[6]}")
            elif seat == "一等座":
                data["余票"] = row[7]
                print(f"一等座余票：{row[7]}")
            elif seat == "二等座":
                data["余票"] = row[8]
                print(f"二等座余票：{row[8]}")
            elif seat == "软卧":
                data["余票"] = row[9]
                print(f"软卧余票：{row[9]}")
            elif seat == "硬卧":
                data["余票"] = row[10]
                print(f"硬卧余票：{row[10]}")
            elif seat == "硬座":
                data["余票"] = row[11]
                print(f"硬座余票：{row[11]}")
            elif seat == "无座":
                data["余票"] = row[12]
                print(f"无座余票：{row[12]}")
            else:
                data["余票"] = None
                print("没有这个座位类型")

            print(f"已保存到 data：{data}")

            # ---------- 提前让用户选好乘车人 ----------
            print("")
            print("请选择乘车人：")
            print("  1 = 乘车人1（列表第一个）")
            print("  2 = 乘车人2（列表第二个）")
            print("  3 = 乘车人3（列表第三个）")
            print("  ...")
            passenger_choice = input("请输入乘车人序号:").strip()
            # ------------------------------------------------

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
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

                # 出发地输入（直接注入，绕过下拉框）
                from_station_name = data["出发站"]
                from_station_code = get_station_code(from_station_name)
                page.locator("#fromStation").evaluate(f"el => el.value = '{from_station_code}'")
                page.locator("#fromStationText").evaluate(f"el => el.value = '{from_station_name}'")
                print(f"出发地已填入: {from_station_name} ({from_station_code})")

                # 到达地输入（同理）
                to_station_name = data["到达站"]
                to_station_code = get_station_code(to_station_name)
                page.locator("#toStation").evaluate(f"el => el.value = '{to_station_code}'")
                page.locator("#toStationText").evaluate(f"el => el.value = '{to_station_name}'")
                print(f"目的地已填入: {to_station_name} ({to_station_code})")

                # 出发日期输入
                train_date_input = page.locator("input#train_date")
                train_date_input.click()
                train_date_input.fill("")
                train_date_input.fill(train_date)
                page.keyboard.press("Enter")
                time.sleep(random.uniform(0.5, 1.0))
                print(f"出发日期已填入: {train_date}")

                # 监听在点击查询后是否存在新页面
                print("正在点击查询按钮...")
                page.click("#query_ticket")

                # 等待车次列表出现
                page.wait_for_selector("#queryLeftTable tr", state="attached", timeout=15000)
                print("查询成功")

                # 判断页面中是否存在"去填写"按钮
                print("正在查找'去填写'按钮...")
                page.wait_for_timeout(1000)

                prefilled_btn = page.locator("a.entry-btn", has_text="去填写")
                prefilled_btn.wait_for(state="attached", timeout=5000)
                prefilled_btn.click(force=True)

                # ================= 按 data-info 属性定位 =================
                # 等待预填车次列表加载完成
                page.wait_for_selector(".ticket-result-item", state="attached", timeout=15000)
                print("预填页面已加载")

                SEAT_CODE_MAP = {
                    "商务座": "9", "特等座": "P", "优选一等座": "D",
                    "一等座": "M", "二等座": "O",
                    "一等卧": "I", "二等卧": "J", "动卧": "F",
                    "高级软卧": "6", "软卧": "4", "硬卧": "3",
                    "硬座": "1", "无座": "W",
                }
                seat_code = SEAT_CODE_MAP.get(data["座位类型"])
                print(f"车次={data['车次']}, 座位={data['座位类型']}, 座位代码={seat_code}")

                # 定位按钮：加入出发地和目的地过滤，避免选错车站
                btns = page.locator(f'a.btn[data-info*="{data["车次"]}"][data-info*="#{seat_code}#"]')
                count = btns.count()
                target_btn = None

                print(f"找到 {count} 个符合条件的按钮，正在精确匹配出发站和到达站...")
                for i in range(count):
                    b = btns.nth(i)
                    info = b.get_attribute("data-info") or ""
                    # 严格匹配出发站和到达站代码
                    if from_station_code in info and to_station_code in info:
                        target_btn = b
                        print(f"匹配成功: {info}")
                        break

                if target_btn:
                    target_btn.wait_for(state="visible", timeout=10000)
                    target_btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    target_btn.click()
                    print(
                        f"已成功点击车次 {data['车次']} 从 {data['出发站']} 到 {data['到达站']} 的 {data['座位类型']} 选择按钮！")
                else:
                    print("错误：未找到精确匹配出发站和到达站的预填按钮！")
                    raise SystemExit

                # 等待提交按钮变为可点击状态（最多等 10 秒）
                submit_btn = page.locator("#saveBtn")
                print("等待'提交'按钮启用...")
                submit_enabled = False
                for i in range(20):
                    page.wait_for_timeout(500)
                    submit_class = submit_btn.get_attribute("class") or ""
                    if "btn-disabled" not in submit_class:
                        submit_enabled = True
                        break

                if submit_enabled:
                    submit_btn.scroll_into_view_if_needed()
                    submit_btn.click()

                    # ================= 提交后：勾选乘车人 + 点确定 =================
                    # 等待预填单列表页加载完成
                    print("等待预填单列表页加载...")
                    page.wait_for_selector("#passenge_list li", state="visible", timeout=15000)
                    page.wait_for_timeout(1000)
                    print("预填单列表页已加载")

                    # 按用户选择的序号勾选乘车人
                    passenger_idx = int(passenger_choice) - 1
                    passenger_label = page.locator("#passenge_list li").nth(passenger_idx).locator("label.check-inline")
                    passenger_label.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    passenger_name = passenger_label.get_attribute("title")
                    passenger_label.click()
                    print(f"已勾选乘车人 {passenger_choice}: {passenger_name}")
                    page.wait_for_timeout(800)

                    # 点击页面上的"确定"按钮
                    confirm_btn = page.locator(".order-detail-ft a.btn-primary", has_text="确定").first
                    confirm_btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    confirm_btn.click()
                    print("已点击'确定'按钮")

                    # ================= 倒计时结束立即点击购票 =================
                    print("")
                    print("等待开售...")

                    start_wait = time.time()
                    last_print = 0

                    while True:
                        # 超时保护：最多等 1 小时
                        if time.time() - start_wait > 3600:
                            print("\n等待超时（超过1小时），退出")
                            break

                        # 【第一优先级】检查购票按钮是否已显示
                        buy_btn = page.locator("a.buy-ticket-button").first
                        if buy_btn.count() > 0:
                            try:
                                if buy_btn.is_visible():
                                    print("\n已开售，购票按钮已出现")
                                    break
                            except:
                                pass

                        # 【第二优先级】读取倒计时
                        remain = 999
                        countdown_loc = page.locator(".count-down-text")
                        if countdown_loc.count() > 0:
                            try:
                                text = countdown_loc.inner_text().strip()
                                if text:
                                    now = time.time()
                                    if now - last_print > 1:
                                        sys.stdout.write(f"\r剩余时间: {text}      ")
                                        sys.stdout.flush()
                                        last_print = now
                                    min_match = re.search(r"(\d+)\s*分", text)
                                    sec_match = re.search(r"(\d+)\s*秒", text)
                                    remain = 0
                                    if min_match:
                                        remain += int(min_match.group(1)) * 60
                                    if sec_match:
                                        remain += int(sec_match.group(1))
                            except:
                                pass

                        if remain > 60:
                            page.wait_for_timeout(1000)  # >60秒: 1秒一次
                        elif remain > 10:
                            page.wait_for_timeout(300)  # 10-60秒: 300ms一次
                        elif remain > 3:
                            page.wait_for_timeout(100)  # 3-10秒: 100ms一次
                        else:
                            page.wait_for_timeout(50)  # <3秒: 50ms高频轰炸

                    # ==================== 开售瞬间，进入抢票阶段 ====================
                    print("\n进入抢票阶段...")

                    # 步骤1：点击"按预填信息购票"（用高频重试，防止按钮没渲染好）
                    buy_clicked = False
                    for attempt in range(50):
                        try:
                            buy_btn = page.locator("a.buy-ticket-button:visible").first
                            if buy_btn.count() > 0:
                                buy_btn.scroll_into_view_if_needed()
                                buy_btn.click(force=True, timeout=50)
                                buy_clicked = True
                                print(f"[尝试{attempt + 1}] 已点击'按预填信息购票'")
                                break
                        except Exception as e:
                            pass
                        page.wait_for_timeout(100)

                    if not buy_clicked:
                        print("多次尝试仍未点到购票按钮，尝试主动刷新...")
                        try:
                            page.locator("#query_ticket").click(force=True)
                            page.wait_for_timeout(500)
                        except:
                            pass

                    # 步骤2：等提交订单按钮/弹窗，一出现立刻点
                    print("等待提交订单按钮...")
                    submit_clicked = False
                    for attempt in range(80):  # 最多等 8 秒（80 * 100ms）
                        try:
                            # 优先：订单确认页的“提交订单”按钮（ID 长期稳定）
                            submit_btn = page.locator("#submitOrder_id")
                            if submit_btn.count() > 0 and submit_btn.first.is_visible():
                                submit_btn.first.scroll_into_view_if_needed()
                                submit_btn.first.click(force=True, timeout=50)
                                submit_clicked = True
                                print(f"[尝试{attempt + 1}] 已点击'提交订单' (submitOrder_id)")
                                break

                            # 备选：弹窗中的“提交订单”按钮（不同版本弹窗结构可能不同）
                            modal_btn = page.locator(
                                ".modal .modal-ft a.btn.btn-primary.ok, "
                                ".modal .modal-ft a.btn.btn-primary, "
                                ".modal .modal-ft a.ok"
                            )
                            if modal_btn.count() > 0 and modal_btn.first.is_visible():
                                modal_btn.first.scroll_into_view_if_needed()
                                modal_btn.first.click(force=True, timeout=50)
                                submit_clicked = True
                                print(f"[尝试{attempt + 1}] 已点击'提交订单' (弹窗按钮)")
                                break

                        except Exception as e:
                            # 调试时可打印：print(f"尝试{attempt+1}异常: {e}")
                            pass

                        page.wait_for_timeout(100)

                    if not submit_clicked:
                        print("多次尝试仍未点到提交订单按钮")
                    # ==================================================================

                input("")
                browser.close()