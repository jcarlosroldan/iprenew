from iprenew.constants import ATTEMPTS, CONFIG
from autoselenium import Firefox
from simpler.terminal import cprint
from typing import List
from urllib.parse import urljoin
from iprenew.actions import browse, change_selector, click, select, sleep, write

def freenom_renew(ip: str) -> None:
	driver = Firefox()
	_login(driver)
	for domain in _domains(driver):
		print('Changing ip of domain ' + domain)
		attempts = ATTEMPTS
		while True:
			try:
				_change_ip(driver, domain, ip)
				break
			except:
				if attempts == 0:
					cprint('\tToo many failed attempts. Jumping into the next domain', fg='red')
					break
				else:
					attempts -= 1
					cprint('\tRetrying after an error', fg='yellow')
	cprint('Done!', fg='green')
	driver.close()

def _login(driver: Firefox) -> None:
	print('Logging in')
	browse(driver, 'https://my.freenom.com/clientarea.php?language=english')
	write(driver, '#username', CONFIG['freenom']['mail'])
	write(driver, '#password', CONFIG['freenom']['password'])
	click(driver, '.login input[type=submit]')
	try:
		assert select(driver, '.splash').text.startswith('Hello')
	except:
		cprint('Invalid mail/password or language is not English.', fg='red')

def _domains(driver: Firefox) -> List[str]:
	print('Retrieving list of domains')
	click(driver, '.main-menu > li:first-child')
	click(driver, '.main-menu > li:first-child li:nth-child(2)')
	change_selector(driver, 'select[name="itemlimit"]', 'Unlimited')
	select(driver, '.results a.smallBtn')
	return [
		urljoin(driver.current_url, e.get_attribute('href'))
		for e in driver.find_elements_by_css_selector('.results a.smallBtn')
	]

def _change_ip(driver: Firefox, domain: str, ip: str) -> None:
	browse(driver, domain)
	click(driver, '#tabs > ul > li:last-child a')
	sleep(4)
	if select(driver, 'h1').text.rsplit(' ', 1)[-1] not in CONFIG['freenom']['ignore_domains']:
		write(driver, '.value_column input[type="text"][size="30"][name="records[0][value]"]', ip)
		click(driver, '#recordslistform .smallBtn.primaryColor')
		assert select(driver, '.dnssuccess, .dnserror').text in ('Record modified successfully', 'There were no changes')