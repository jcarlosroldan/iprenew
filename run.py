from autoselenium import Firefox
from os.path import exists, abspath
from random import gauss
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from simpler.files import load, save
from simpler.terminal import cprint
from sys import argv
from time import sleep as _sleep
from typing import List
from urllib.parse import urljoin
from urllib.request import urlopen

CONFIG = {}
PATH_CONFIG = 'config.json'
ATTEMPTS = 5

WAIT_BEFORE_WRITE = .3
WAIT_BETWEEN_KEYSTROKES = .04
WAIT_BEFORE_CLICK = .2
WAIT_BEFORE_HOVER = .2
WAIT_TIMEOUT = 10
WAIT_LOAD = 1.5
WAIT_LOAD_INCREASE = .05  # each time a page is loaded, cloudfare adds some penalty

def main() -> None:
	load_config()
	ip = get_ip()
	driver = Firefox()
	login(driver)
	for domain in domains(driver):
		print('Changing ip of domain ' + domain)
		attempts = ATTEMPTS
		while True:
			try:
				change_ip(driver, domain, ip)
				break
			except:
				if attempts == 0:
					cprint('\tToo many failed attempts. Jumping into the next domain', fg='red')
					break
				else:
					attempts -= 1
					cprint('\tRetrying after an error', fg='yellow')
	cprint('Done!', fg='green')

def load_config() -> None:
	if exists(PATH_CONFIG):
		CONFIG.update(load(PATH_CONFIG))
	else:
		save(PATH_CONFIG, {'mail': 'your@mail.com', 'password': 'your_password', 'ignore_domains': []})
		cprint('A new config was created, modify it and run this script again. It\'s located at ' + abspath(PATH_CONFIG), fg='yellow')
		exit()

# region freenom interaction

def get_ip() -> str:
	if len(argv) > 1:
		ip = argv[1]
	elif 'ip' in CONFIG:
		ip = CONFIG['ip']
	else:
		cprint('IP not specified, using this machine\'s from ipinfo.io', fg='yellow')
		ip = urlopen('https://ipinfo.io/ip').read().decode()
	assert len(ip.split('.')) == 4 and all(1 <= int(p) <= 255 for p in ip.split('.')), 'Invalid IP'
	return ip

def login(driver: Firefox) -> None:
	print('Logging in')
	browse(driver, 'https://my.freenom.com/clientarea.php?language=english')
	write(driver, '#username', CONFIG['mail'])
	write(driver, '#password', CONFIG['password'])
	click(driver, '.login input[type=submit]')
	try:
		assert select(driver, '.splash').text.startswith('Hello')
	except:
		cprint('Invalid mail/password or language is not English.', fg='red')

def domains(driver: Firefox) -> List[str]:
	print('Retrieving list of domains')
	click(driver, '.main-menu > li:first-child')
	click(driver, '.main-menu > li:first-child li:nth-child(2)')
	change_selector(driver, 'select[name="itemlimit"]', 'Unlimited')
	select(driver, '.results a.smallBtn')
	return [
		urljoin(driver.current_url, e.get_attribute('href'))
		for e in driver.find_elements_by_css_selector('.results a.smallBtn')
	]

def change_ip(driver: Firefox, domain: str, ip: str) -> None:
	browse(driver, domain)
	click(driver, '#tabs > ul > li:last-child a')
	sleep(4)
	if select(driver, 'h1').text.rsplit(' ', 1)[-1] not in CONFIG['ignore_domains']:
		write(driver, '.value_column input[type="text"][size="30"][name="records[0][value]"]', ip)
		click(driver, '#recordslistform .smallBtn.primaryColor')
		assert select(driver, '.dnssuccess, .dnserror').text in ('Record modified successfully', 'There were no changes')

# endregion

# region selenium shorthands

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

# endregion

if __name__ == '__main__':
	main()