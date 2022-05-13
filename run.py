from iprenew.constants import CONFIG, PATH_CONFIG
from iprenew.freenom import freenom_renew
from iprenew.ovh import ovh_renew
from os.path import exists, abspath
from simpler import load, save, cprint
from sys import argv
from urllib.request import urlopen

def main():
	load_config()
	ip = get_ip()
	ovh_renew(ip)
	freenom_renew(ip)

def load_config() -> None:
	if exists(PATH_CONFIG):
		CONFIG.update(load(PATH_CONFIG))
	else:
		save(PATH_CONFIG, {})
		cprint('A new config was created, modify it and run this script again. It\'s located at ' + abspath(PATH_CONFIG), fg='yellow')
		exit()

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

if __name__ == '__main__':
	main()