from orm.driver import Driver
from orm.ui import UI

# from helpers.action import sleepWithLog

driver = Driver(dry_run=False, high_light_mode=True)

# # Test "Click by attribute"
# driver.switchTab(0)
# driver.goto("https://stackoverflow.com/questions/30324760/how-to-get-an-attribute-of-an-element-from-selenium")
# sleep(1)
# driver.switchTab(0)
# driver.clickByAttribute(
#     selector="#answers > div",
#     attribute="itemprop",
#     value="suggestedAnswer",
#     # [name="q"]
# )

# # Test "Select"
# driver.switchTab(0)
# driver.goto("https://map2.nissan.co.jp/c/h/?hs_cd=0570&grp=&uc=60&BT1=2&BT10=1&BT15=1&isNdex=1")
# sleepWithLog(1)
# driver.clickByCSS(selector="body > div.contents > div.shop-block > ul > li:nth-child(1) > div.shop-info > div > div.as-link.shaken-reserve-request.only-large > div > div")
# sleepWithLog(1)
# driver.switchTab(1)
# sleepWithLog(1)
# driver.clickByCSS("#root > main > article > section > div > form > div:nth-child(2) > div.Item.-birth.car_mode > div > div:nth-child(2) > label > span.icon")
# sleepWithLog(1)
# driver.select(
#     selector="#catalog_car_mode_id",
#     value="ノートオーラ",
# )
# sleepWithLog(1)
# driver.select(
#     selector="#catalog_car_mode_id",
#     value="16", # ルークス 
# )
# sleepWithLog(100)

# driver.goto("https://reservation.reginaclinic.jp/?_gl=1*t0cawi*_gcl_aw*R0NMLjE3MjQ1NjUxODIuRUFJYUlRb2JDaE1JM1o2Njc3bVBpQU1Wd1Z3UEFoMlBnemhpRUFBWUFpQUFFZ0w1aVBEX0J3RQ..*_gcl_au*MTkxMDM0NTM0OS4xNzI0NTY1MTc4#/")

# driver.executeScript("window.open('');")
# driver.switchTab(1)
# driver.goto("https://reservation.mens.reginaclinic.jp/?utm_medium=cpc_brand&utm_source=google&utm_campaign=brand_term&argument=cYCQCTwd&dmai=a652fa167b8892#/")

# Most of the UI setup is done in the init function.
ui = UI(driver=driver)

ui.go()
driver.close()
