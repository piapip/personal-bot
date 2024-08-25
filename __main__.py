from orm.driver import Driver
from orm.ui import UI

driver = Driver(dry_run=False, high_light_mode=False)
# print("The current url is:"+str(driver.driver.current_url))

# driver.switchTab(0)
# driver.goto("https://reservation.reginaclinic.jp/?_gl=1*t0cawi*_gcl_aw*R0NMLjE3MjQ1NjUxODIuRUFJYUlRb2JDaE1JM1o2Njc3bVBpQU1Wd1Z3UEFoMlBnemhpRUFBWUFpQUFFZ0w1aVBEX0J3RQ..*_gcl_au*MTkxMDM0NTM0OS4xNzI0NTY1MTc4#/")

# driver.executeScript("window.open('');")
# driver.switchTab(1)
# driver.goto("https://reservation.mens.reginaclinic.jp/?utm_medium=cpc_brand&utm_source=google&utm_campaign=brand_term&argument=cYCQCTwd&dmai=a652fa167b8892#/")

# Most of the UI setup is done in the init function.
ui = UI(driver=driver)

# New strat.
# Login normally, then type the key to start the automation.
# driver.login()

ui.go()
driver.close()
