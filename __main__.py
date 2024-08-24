from orm.driver import Driver
from orm.ui import UI

driver = Driver(dry_run=True, high_light_mode=False)
# Most of the UI setup is done in the init function.
ui = UI(driver=driver)

# New strat.
# Login normally, then type the key to start the automation.
# driver.login()

ui.go()
driver.close()
