from autoselenium import Firefox
from iprenew.actions import browse, click, select, sleep, write
from iprenew.constants import ATTEMPTS, CONFIG
from selenium.webdriver.common.action_chains import ActionChains
from simpler.terminal import cprint
from typing import List
from urllib.parse import urljoin

def ovh_renew(ip: str) -> None:
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
	browse(driver, 'https://www.ovh.com/manager/web/')
	write(driver, '.pagination-centered .control-group:nth-of-type(1) input', CONFIG['ovh']['mail'])
	write(driver, '.pagination-centered .control-group:nth-of-type(2) input', CONFIG['ovh']['password'])
	click(driver, '.login-inputs-login button[type=submit]')
	sleep(10)
	click(driver, '[data-translate=cookie_policy_refuse]')
	try:
		assert select(driver, '.d-inline').text.startswith('Welcome to the')
	except:
		cprint('Invalid mail/password or language is not English.', fg='red')

def _domains(driver: Firefox) -> List[str]:
	print('Retrieving list of domains')
	click(driver, 'button[title="Domain names"]')
	sleep(1)
	return [
		urljoin(driver.current_url, e.get_attribute('href'))
		for e in driver.find_elements_by_css_selector('.menu-level-2 a.menu-item')[2:]
	]

def _change_ip(driver: Firefox, domain: str, ip: str) -> None:
	browse(driver, domain + '/zone')
	if select(driver, 'h1.oui-header__title') in CONFIG['ovh']['ignore_domains']: return
	click(driver, '.table-responsive .oui-icon-ellipsis')
	click(driver, '[data-translate=table_modify_entry]')
	click(driver, '[data-ng-model="ctrl.model.target.value"]')
	select(driver, '[data-ng-model="ctrl.model.target.value"]').clear()
	write(driver, '[data-ng-model="ctrl.model.target.value"]', ip)
	click(driver, '[data-ng-bind="wizardNextButtonText"]')
	sleep(1)
	ActionChains(driver).key_down('\n').perform()
	sleep(4)
	assert 'modification will be applied immediately' in select(driver, '.alert-success').text