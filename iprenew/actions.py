from iprenew.constants import WAIT_BEFORE_CLICK, WAIT_BEFORE_HOVER, WAIT_BEFORE_WRITE, WAIT_BETWEEN_KEYSTROKES, WAIT_LOAD, WAIT_LOAD_INCREASE, WAIT_TIMEOUT
from autoselenium import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from time import sleep as _sleep
from random import gauss

def browse(driver: Firefox, url: str) -> None:
	global WAIT_LOAD
	driver.get(url)
	sleep(WAIT_LOAD)
	WAIT_LOAD += WAIT_LOAD_INCREASE

def write(driver: Firefox, selector: str, text: str) -> None:
	sleep(WAIT_BEFORE_WRITE)
	elem = select(driver, selector)
	elem.clear()
	for char in text:
		elem.send_keys(char)
		sleep(WAIT_BETWEEN_KEYSTROKES)

def click(driver: Firefox, selector: str) -> None:
	sleep(WAIT_BEFORE_CLICK)
	select(driver, selector).click()

def hover(driver: Firefox, selector: str) -> None:
	sleep(WAIT_BEFORE_HOVER)
	ActionChains(driver).move_to_element(select(driver, selector)).perform()

def change_selector(driver: Firefox, selector: str, option: str) -> None:
	click(driver, selector)
	Select(select(driver, selector, wait=False)).select_by_visible_text(option)

def select(driver: Firefox, selector: str, wait: bool = True) -> None:
	if wait:
		WebDriverWait(driver, WAIT_TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
	return driver.find_element_by_css_selector(selector)

def sleep(average_time: float) -> None:
	_sleep(max(0, min(average_time * 2, gauss(average_time, average_time / 4))))