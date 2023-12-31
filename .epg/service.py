# -*- coding: utf-8 -*-
import time, tools, os, io, json, re, sys, requests
from tools import datapath, temppath, log, notify, addon_name, addon_version, loc
from datetime import date, datetime, timedelta
import socket
from collections import Counter
import xml_structure
import magenta_DE
import tvspielfilm_DE
#import swisscom_CH
#import horizon
#import zattoo
import platform
import importlib
tools.delete(os.path.join(datapath, 'log.txt'))
thread_temppath = os.path.join(temppath, "multithread")
machine = platform.machine()

## Read Global Settings
storage_path = os.path.join(datapath, "storage")
tools.makedir(storage_path)
auto_download = False
timeswitch_1 = 0
timeswitch_2 = 0
timeswitch_3 = 0
enable_rating_mapper = False
use_local_sock = False
tvh_local_sock = ""
download_threads = 5
enable_multithread = False


## Get Enabled Grabbers
# Divers
enable_grabber_magentaDE = True
enable_grabber_tvsDE = True
enable_grabber_swcCH = False
# Horizon
enable_grabber_hznDE = False
enable_grabber_hznAT = False
enable_grabber_hznCH = False
enable_grabber_hznNL = False
enable_grabber_hznPL = False
enable_grabber_hznIE = False
enable_grabber_hznGB = False
enable_grabber_hznSK = False
enable_grabber_hznCZ = False
enable_grabber_hznHU = False
enable_grabber_hznRO = False
# Zattoo
enable_grabber_zttDE = False
enable_grabber_zttCH = False
enable_grabber_1und1DE = False
enable_grabber_qlCH = False
enable_grabber_mnetDE = False
enable_grabber_walyCH = False
enable_grabber_mweltAT = False
enable_grabber_bbvDE = False
enable_grabber_vtxCH = False
enable_grabber_myvisCH = False
enable_grabber_gvisCH = False
enable_grabber_sakCH = False
enable_grabber_nettvDE = False
enable_grabber_eweDE = False
enable_grabber_qttvCH = False
enable_grabber_saltCH = False
enable_grabber_swbDE = False
enable_grabber_eirIE = False

# Check if any Grabber is enabled
if (enable_grabber_magentaDE or enable_grabber_tvsDE or enable_grabber_swcCH or enable_grabber_hznDE or enable_grabber_hznAT or enable_grabber_hznCH or enable_grabber_hznNL or enable_grabber_hznPL or enable_grabber_hznIE or enable_grabber_hznGB or enable_grabber_hznSK or enable_grabber_hznCZ or enable_grabber_hznHU or enable_grabber_hznRO or enable_grabber_zttDE or enable_grabber_zttCH or enable_grabber_1und1DE or enable_grabber_qlCH or enable_grabber_mnetDE or enable_grabber_walyCH or enable_grabber_mweltAT or enable_grabber_bbvDE or enable_grabber_vtxCH or enable_grabber_myvisCH or enable_grabber_gvisCH or enable_grabber_sakCH or enable_grabber_nettvDE or enable_grabber_eweDE or enable_grabber_qttvCH or enable_grabber_saltCH or enable_grabber_swbDE or enable_grabber_eirIE):
	enabled_grabber = True
else:
	enabled_grabber = False

guide_temp = os.path.join(datapath, 'guide.xml')
guide_dest = os.path.join(os.path.dirname(datapath), 'guide.xml.gz')
grabber_cron = os.path.join(datapath, 'grabber_cron.json')
grabber_cron_tmp = os.path.join(temppath, 'grabber_cron.json')
xmltv_dtd = os.path.join(datapath, 'xmltv.dtd')


def copy_guide_to_destination():
	done = tools.comp(guide_temp, guide_dest)
	if done:
		try:
			tools.delete(guide_temp)
			tools.delete(os.path.join(datapath, '__pycache__'))
			tools.delete(os.path.join(datapath, 'log.txt'))
			tools.delete(storage_path)
			## Write new setting last_download
			with open(grabber_cron, 'r', encoding='utf-8') as f:
				data = json.load(f)
				data['last_download'] = str(int(time.time()))

			with open(grabber_cron_tmp, 'w', encoding='utf-8') as f:
				json.dump(data, f, indent=4)

			## rename temporary file replacing old file
			tools.copy(grabber_cron_tmp, grabber_cron)
			time.sleep(3)
			tools.delete(grabber_cron_tmp)
			notify(addon_name, loc(32350))
			log(loc(32350))
		except:
			log('Worker can´t read cron File, creating new File...'.format(loc(32356)))
			with open(grabber_cron, 'w', encoding='utf-8') as f:
				f.write(json.dumps({'last_download': str(int(time.time())), 'next_download': str(int(time.time()) + 86400)}))
			notify(addon_name, loc(32350))
			log(loc(32350))
	else:
		notify(addon_name, loc(32351))
		log(loc(32351))

def check_channel_dupes():
	with open(guide_temp, encoding='utf-8') as f:
		c = Counter(c.strip() for c in f if c.strip())  # for case-insensitive search
		dupe = []
		for line in c:
			if c[line] > 1:
				if ('display-name' in line or 'icon src' in line or '</channel' in line):
					pass
				else:
					dupe.append(line + '\n')
		dupes = ''.join(dupe)

		if (not dupes == ''):
			log('{} {}'.format(loc(32400), dupes))
			ok = True
			if ok:
				return False
			return False
		else:
			return True

def run_grabber():
	if check_startup():
		importlib.reload(xml_structure)
		importlib.reload(magenta_DE)
		importlib.reload(tvspielfilm_DE)
		#importlib.reload(swisscom_CH)
		#importlib.reload(horizon)
		#importlib.reload(zattoo)
		xml_structure.xml_start()
		xml_structure.xml_channels_start('ZAPPN')
		xml_structure.xml_channels('PULS24', 'PULS24', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/PULS24logo.png/640px-PULS24logo.png', 'de')
		## Check Provider , Create XML Channels
		if enable_grabber_magentaDE:
			if magenta_DE.startup():
				magenta_DE.create_xml_channels()
		if enable_grabber_tvsDE:
			if tvspielfilm_DE.startup():
				tvspielfilm_DE.create_xml_channels()
		if enable_grabber_swcCH:
			if swisscom_CH.startup():
				swisscom_CH.create_xml_channels()
		if enable_grabber_hznDE:
			if horizon.startup('de'):
				horizon.create_xml_channels('de')
		if enable_grabber_hznAT:
			if horizon.startup('at'):
				horizon.create_xml_channels('at')
		if enable_grabber_hznCH:
			if horizon.startup('ch'):
				horizon.create_xml_channels('ch')
		if enable_grabber_hznNL:
			if horizon.startup('nl'):
				horizon.create_xml_channels('nl')
		if enable_grabber_hznPL:
			if horizon.startup('pl'):
				horizon.create_xml_channels('pl')
		if enable_grabber_hznIE:
			if horizon.startup('ie'):
				horizon.create_xml_channels('ie')
		if enable_grabber_hznGB:
			if horizon.startup('gb'):
				horizon.create_xml_channels('gb')
		if enable_grabber_hznSK:
			if horizon.startup('sk'):
				horizon.create_xml_channels('sk')
		if enable_grabber_hznCZ:
			if horizon.startup('cz'):
				horizon.create_xml_channels('cz')
		if enable_grabber_hznHU:
			if horizon.startup('hu'):
				horizon.create_xml_channels('hu')
		if enable_grabber_hznRO:
			if horizon.startup('ro'):
				horizon.create_xml_channels('ro')
		if enable_grabber_zttDE:
			if zattoo.startup('ztt_de'):
				zattoo.create_xml_channels('ztt_de')
		if enable_grabber_zttCH:
			if zattoo.startup('ztt_ch'):
				zattoo.create_xml_channels('ztt_ch')
		if enable_grabber_1und1DE:
			if zattoo.startup('1und1_de'):
				zattoo.create_xml_channels('1und1_de')
		if enable_grabber_qlCH:
			if zattoo.startup('ql_ch'):
				zattoo.create_xml_channels('ql_ch')
		if enable_grabber_mnetDE:
			if zattoo.startup('mnet_de'):
				zattoo.create_xml_channels('mnet_de')
		if enable_grabber_walyCH:
			if zattoo.startup('walytv_ch'):
				zattoo.create_xml_channels('walytv_ch')
		if enable_grabber_mweltAT:
			if zattoo.startup('meinewelt_at'):
				zattoo.create_xml_channels('meinewelt_at')
		if enable_grabber_bbvDE:
			if zattoo.startup('bbtv_de'):
				zattoo.create_xml_channels('bbtv_de')
		if enable_grabber_vtxCH:
			if zattoo.startup('vtxtv_ch'):
				zattoo.create_xml_channels('vtxtv_ch')
		if enable_grabber_myvisCH:
			if zattoo.startup('myvision_ch'):
				zattoo.create_xml_channels('myvision_ch')
		if enable_grabber_gvisCH:
			if zattoo.startup('glattvision_ch'):
				zattoo.create_xml_channels('glattvision_ch')
		if enable_grabber_sakCH:
			if zattoo.startup('sak_ch'):
				zattoo.create_xml_channels('sak_ch')
		if enable_grabber_nettvDE:
			if zattoo.startup('nettv_de'):
				zattoo.create_xml_channels('nettv_de')
		if enable_grabber_eweDE:
			if zattoo.startup('tvoewe_de'):
				zattoo.create_xml_channels('tvoewe_de')
		if enable_grabber_qttvCH:
			if zattoo.startup('quantum_ch'):
				zattoo.create_xml_channels('quantum_ch')
		if enable_grabber_saltCH:
			if zattoo.startup('salt_ch'):
				zattoo.create_xml_channels('salt_ch')
		if enable_grabber_swbDE:
			if zattoo.startup('tvoswe_de'):
				zattoo.create_xml_channels('tvoswe_de')
		if enable_grabber_eirIE:
			if zattoo.startup('eir_ie'):
				zattoo.create_xml_channels('eir_ie')

		# Check for Channel Dupes
		if check_channel_dupes():

			## Create XML Broadcast
			api_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0', 'Content-type': 'application/json;charset=utf-8', 'X-Api-Date-Format': 'iso', 'X-Api-Camel-Case': 'true', 'referer': 'https://streaming.simplitv.at/'}
			data_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0', 'Accept': 'application/json'}
			time_start = str(datetime.now().strftime("%Y-%m-%dT%H:%M:00.000Z"))
			time_end = str((datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:00.000Z"))
			epg_url = "https://api.app.simplitv.at/v1/EpgTile/FilterProgramTiles?$headers=%7B%22Content-Type%22:%22application%2Fjson%3Bcharset%3Dutf-8%22,%22X-Api-Date-Format%22:%22iso%22,%22X-Api-Camel-Case%22:true%7D"
			epg_post = json.dumps({"platformCodename": "www", "from": time_start, "to": time_end})
			epg_resp = requests.post(epg_url, timeout=5, headers=api_headers, data=epg_post, allow_redirects=False).json()["programs"]
			prg_url = "https://api.app.simplitv.at/v2/Tile/GetTiles?$headers=%7B%22Content-Type%22:%22application%2Fjson%3Bcharset%3Dutf-8%22,%22X-Api-Date-Format%22:%22iso%22,%22X-Api-Camel-Case%22:true%7D"
			prg_post = json.dumps({"platformCodename": "www", "requestedTiles": [{"id": a["id"]} for i in epg_resp.keys() for a in epg_resp[i] if i == "puls24"]})
			epg_data = requests.post(prg_url, timeout=5, headers=api_headers, data=prg_post, allow_redirects=False).json()["tiles"]
			for program in epg_data:
				item_starttime = datetime.strptime(program["start"].split('+')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d%H%M%S')
				item_endtime = datetime.strptime(program["stop"].split('+')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d%H%M%S')
				items_genre = program['categories'][-1]['name'] if len(program.get("categories", [])) > 0 else ""
				item_country = ', '.join([i['name'] for i in program['countries']]) if len(program.get("countries", [])) > 0 else ""
				item_description = program.get("description", "").replace("\n\n", "")
				item_title = program.get("title", "")
				item_picture = program["images"][0]["url"]
				item_season = program.get('seasonNumber', "")
				item_episode = program.get("episodeNumber", "")
				item_subtitle = program.get("subTitle", "")
				item_date = program["date"] if program.get("date", 0) != 0 else ""
				item_agerating, item_starrating, items_director, items_producer = "", "", "", ""
				if len(program.get("people", [])) > 0:
					c = {}
					for i in program["people"]:
						if not c.get('[B]'+i["roleName"]+'[/B]', False):
							c['[B]'+i["roleName"]+'[/B]'] = []
						c['[B]'+i["roleName"]+'[/B]'].append(i["fullName"])
					items_actor = '; '.join([i+': '+', '.join([a for a in c[i]]) for i in c.keys()])
				else: items_actor = ""
				xml_structure.xml_broadcast('onscreen', "PULS24", item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, item_starrating, items_director, items_producer, items_actor, False, "de")
			if enable_grabber_magentaDE:
				if magenta_DE.startup():
					magenta_DE.create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_tvsDE:
				if tvspielfilm_DE.startup():
					tvspielfilm_DE.create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_swcCH:
				if swisscom_CH.startup():
					swisscom_CH.create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznDE:
				if horizon.startup('de'):
					horizon.create_xml_broadcast('de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznAT:
				if horizon.startup('at'):
					horizon.create_xml_broadcast('at', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznCH:
				if horizon.startup('ch'):
					horizon.create_xml_broadcast('ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznNL:
				if horizon.startup('nl'):
					horizon.create_xml_broadcast('nl', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznPL:
				if horizon.startup('pl'):
					horizon.create_xml_broadcast('pl', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznIE:
				if horizon.startup('ie'):
					horizon.create_xml_broadcast('ie', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznGB:
				if horizon.startup('gb'):
					horizon.create_xml_broadcast('gb', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznSK:
				if horizon.startup('sk'):
					horizon.create_xml_broadcast('sk', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznCZ:
				if horizon.startup('cz'):
					horizon.create_xml_broadcast('cz', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznHU:
				if horizon.startup('hu'):
					horizon.create_xml_broadcast('hu', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_hznRO:
				if horizon.startup('ro'):
					horizon.create_xml_broadcast('ro', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_zttDE:
				if zattoo.startup('ztt_de'):
					zattoo.create_xml_broadcast('ztt_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_zttCH:
				if zattoo.startup('ztt_ch'):
					zattoo.create_xml_broadcast('ztt_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_1und1DE:
				if zattoo.startup('1und1_de'):
					zattoo.create_xml_broadcast('1und1_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_qlCH:
				if zattoo.startup('ql_ch'):
					zattoo.create_xml_broadcast('ql_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_mnetDE:
				if zattoo.startup('mnet_de'):
					zattoo.create_xml_broadcast('mnet_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_walyCH:
				if zattoo.startup('walytv_ch'):
					zattoo.create_xml_broadcast('walytv_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_mweltAT:
				if zattoo.startup('meinewelt_at'):
					zattoo.create_xml_broadcast('meinewelt_at', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_bbvDE:
				if zattoo.startup('bbtv_de'):
					zattoo.create_xml_broadcast('bbtv_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_vtxCH:
				if zattoo.startup('vtxtv_ch'):
					zattoo.create_xml_broadcast('vtxtv_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_myvisCH:
				if zattoo.startup('myvision_ch'):
					zattoo.create_xml_broadcast('myvision_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_gvisCH:
				if zattoo.startup('glattvision_ch'):
					zattoo.create_xml_broadcast('glattvision_ch', enable_rating_mapper, thread_temppath,download_threads)
			if enable_grabber_sakCH:
				if zattoo.startup('sak_ch'):
					zattoo.create_xml_broadcast('sak_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_nettvDE:
				if zattoo.startup('nettv_de'):
					zattoo.create_xml_broadcast('nettv_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_eweDE:
				if zattoo.startup('tvoewe_de'):
					zattoo.create_xml_broadcast('tvoewe_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_qttvCH:
				if zattoo.startup('quantum_ch'):
					zattoo.create_xml_broadcast('quantum_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_saltCH:
				if zattoo.startup('salt_ch'):
					zattoo.create_xml_broadcast('salt_ch', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_swbDE:
				if zattoo.startup('tvoswe_de'):
					zattoo.create_xml_broadcast('tvoswe_de', enable_rating_mapper, thread_temppath, download_threads)
			if enable_grabber_eirIE:
				if zattoo.startup('eir_ie'):
					zattoo.create_xml_broadcast('eir_ie', enable_rating_mapper, thread_temppath, download_threads)

			## Finish XML
			xml_structure.xml_end()
			copy_guide_to_destination()

			## Write Guide in TVH Socked
			if use_local_sock:
				write_to_sock()

def write_to_sock():
	if check_startup():
		if (use_local_sock and os.path.isfile(guide_temp)):
			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			epg = open(guide_temp, 'rb')
			epg_data = epg.read()
			try:
				log('{} {}'.format(loc(32380), tvh_local_sock))
				notify(addon_name, loc(32380))
				sock.connect(tvh_local_sock)
				sock.sendall(epg_data)
				log('{} {}'.format(sock.recv, tvh_local_sock))
			except socket.error as e:
				notify(addon_name, '{} {}'.format(loc(32379), e))
				log('{} {}'.format(loc(32379), e))
			finally:
				sock.close()
				epg.close()
		else:
			ok = dialog.ok(loc(32119), loc(32409))
			if ok:
				log(loc(32409))

def worker(timeswitch_1, timeswitch_2, timeswitch_3):
	initiate_download = False

	## Read Settings for last / next_download
	try:
		with open(grabber_cron, 'r', encoding='utf-8') as f:
			cron = json.load(f)
			next_download = cron['next_download']
			last_download = cron['last_download']
	except:
		log('Worker can´t read cron File, creating new File...'.format(loc(32356)))
		with open(grabber_cron, 'w', encoding='utf-8') as f:
			f.write(json.dumps({'last_download': str(int(time.time())), 'next_download': str(int(time.time()) + 86400)}))
		with open(grabber_cron, 'r', encoding='utf-8') as f:
			cron = json.load(f)
			next_download = cron['next_download']
			last_download = cron['last_download']

	log('{} {}'.format(loc(32352), datetime.fromtimestamp(int(last_download)).strftime('%d.%m.%Y %H:%M')))

	if (int(next_download) > int(last_download)):
		log('{} {}'.format(loc(32353), datetime.fromtimestamp(int(next_download)).strftime('%d.%m.%Y %H:%M')))

	if int(next_download) < int(time.time()):
		# suggested download time has passed (e.g. system was offline) or time is now, download epg
		# and set a new timestamp for the next download
		log('{} {}'.format(loc(32352), datetime.fromtimestamp(int(last_download)).strftime('%d.%m.%Y %H:%M')))
		log('{} {}'.format(loc(32353), datetime.fromtimestamp(int(next_download)).strftime('%d.%m.%Y %H:%M')))
		log('{}'.format(loc(32356)))
		initiate_download = True

	## If next_download < last_download, initiate an Autodownload
	if initiate_download:
		notify(addon_name, loc(32357))
		run_grabber()
		## Update Cron Settings
		with open(grabber_cron, 'r', encoding='utf-8') as f:
			cron = json.load(f)
			next_download = cron['next_download']
			last_download = cron['last_download']

	## Calculate the next_download Setting

	# get Settings for daily_1, daily_2, daily_3
	today = datetime.today()
	now = int(time.time())
	calc_daily_1 = datetime(today.year, today.month, day=today.day, hour=timeswitch_1, minute=0, second=0)
	calc_daily_2 = datetime(today.year, today.month, day=today.day, hour=timeswitch_2, minute=0, second=0)
	calc_daily_3 = datetime(today.year, today.month, day=today.day, hour=timeswitch_3, minute=0, second=0)

	try:
		daily_1 = int(calc_daily_1.strftime("%s"))
		daily_2 = int(calc_daily_2.strftime("%s"))
		daily_3 = int(calc_daily_3.strftime("%s"))
	except ValueError:
		daily_1 = int(time.mktime(calc_daily_1.timetuple()))
		daily_2 = int(time.mktime(calc_daily_2.timetuple()))
		daily_3 = int(time.mktime(calc_daily_3.timetuple()))

	## If sheduleplan for daily 1,2,3 is in the past, plan it for next day
	if daily_1 <= now:
		daily_1 += 86400
	if daily_2 <= now:
		daily_2 += 86400
	if daily_3 <= now:
		daily_3 += 86400

	## Find the lowest Integer for next download
	next_download = min([int(daily_1), int(daily_2), int(daily_3)])

	## Write new setting next_download
	with open(grabber_cron, 'w', encoding='utf-8') as f:
		f.write(json.dumps({'last_download': str(int(last_download)), 'next_download': str(int(next_download))}))

def check_internet(host="8.8.8.8", port=53, timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except socket.error as ex:
		return False

def check_startup():
	#Create Tempfolder if not exist
	tools.makedir(temppath)
	tools.makedir(thread_temppath)

	if storage_path == 'choose':
		notify(addon_name, loc(32359))
		log(loc(32359))
		return False

	if not enabled_grabber:
		notify(addon_name, loc(32360))
		log(loc(32360))
		return False

	if use_local_sock:
		socked_string = '.sock'
		if not re.search(socked_string, tvh_local_sock):
			notify(addon_name, loc(32378))
			log(loc(32378))
			return False

	if enable_multithread:
		#log(machine)
		#log('Multithreading is currently under Kodi 19 broken, please disable it')
		ok = True
		if ok:
			return True
		return False

	## create Crontab File which not exists at first time
	if (not os.path.isfile(grabber_cron) or os.stat(grabber_cron).st_size <= 1):
		with open(grabber_cron, 'w', encoding='utf-8') as f:
			f.write(json.dumps({'last_download': str(int(time.time())), 'next_download': str(int(time.time()) + 86400)}))

	## Clean Tempfiles
	for file in os.listdir(temppath):
		tools.delete(os.path.join(temppath, file))

	## Check internet Connection
	if not check_internet():
		retries = 12
		while retries > 0:
			log(loc(32385))
			notify(addon_name, loc(32385))
			time.sleep(5)
			if check_internet():
				log(loc(32386))
				notify(addon_name, loc(32386))
				return True
			else:
				retries -= 1
		if retries == 0:
			log(loc(32387))
			notify(addon_name, loc(32387))
			return False
	else:
		return True

run_grabber()
