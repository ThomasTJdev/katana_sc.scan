# This module requires katana framework 
# https://github.com/PowerScript/KatanaFramework

# :-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-: #
# Katana Core import                  #
from core.KATANAFRAMEWORK import *    #
# :-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-:-: #

# LIBRARIES 
from core.Function import get_local_ip
from xml.dom import minidom   
import xml.etree.ElementTree as ET
import commands               
# END LIBRARIES 

# INFORMATION MODULE
def init():
	init.Author             ="RedToor - Minor changes: TTJ, ThomasTJ 2016"
	init.Version            ="2.0"
	init.Description        ="Ports, OS, Etc Scan to host."
	init.CodeName           ="net/sc.scan"
	init.DateCreation       ="28/11/2015"      
	init.LastModification   ="18/05/2016"
	init.References         =None
	init.License            =KTF_LINCENSE
	init.var                ={}

	# DEFAULT OPTIONS MODULE
	init.options = {
		# NAME    	VALUE          		RQ     DESCRIPTION
		'target'	:[get_local_ip()	,True ,'Host Target'],
		'mode'  	:["mode-0"      	,False,'Port Target'],
		'databytes'	:[""				,False,'+packetsize {bytesize}'],
		'random'	:[""				,False,'Randomize order [y]'],
		'mac'		:[""				,False,'Spoof MAC [y]'],
		'checksum'	:[""				,False,'Add bad checksums [y]'],
		'zombie'	:[""				,False,'Idle zombie {zombie ip}'],
		'sourceport':[""				,False,'Source port {port}'],
		'port'		:[""				,False,'Specific port {port}'],
		'decoy'		:[""				,False,'Decoy - random ips [y]'],
		'save'		:[""				,False,'Save results {filname}'],
	}

	init.aux = """
 (mode) options
 -> [mode-0] Intense scan
 -> [mode-1] Intense scan plus UDP 
 -> [mode-2] Intense scan, all TCP ports
 -> [mode-3] Intense scan, no ping
 -> [mode-4] Ping scan
 -> [mode-5] Quick scan
 -> [mode-6] Quick scan plus                  	
 -> [mode-7] Quick traceroute 
 -> [mode-8] Regular scan
 -> [mode-9] Slow comprehensive scan
	"""
	return init
# END INFORMATION MODULE

# CODE MODULE    ############################################################################################
def main(run):
	parameter="-T4 -A -v"
	if init.var['mode']  =="mode-0":parameter="-T4 -A -v"
	elif init.var['mode']=="mode-1":parameter="-sS -sU -T4 -A -v"
	elif init.var['mode']=="mode-2":parameter="-p 1-65535 -T4 -A -v"
	elif init.var['mode']=="mode-3":parameter="-T4 -A -v -Pn"
	elif init.var['mode']=="mode-4":parameter="-sn"
	elif init.var['mode']=="mode-5":parameter="-T4 -F"
	elif init.var['mode']=="mode-6":parameter="-sV -T4 -O -F --version-light"
	elif init.var['mode']=="mode-7":parameter="-sn --traceroute"
	elif init.var['mode']=="mode-8":parameter=""
	elif init.var['mode']=="mode-9":parameter="-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script 'default or (discovery and safe)'"
	else:
		printAlert(1,"Type not allow, use show options or sop and see Auxiliar help.")
		init.var['mode']="mode-0"
		return
	
	parameter_opt=" "	
	if init.var['databytes']:	parameter_opt=(" --data-length " + init.var['databytes'])
	if init.var['random']=="y":	parameter_opt=(parameter_opt + " --randomize-hosts")
	if init.var['mac']=="y":	parameter_opt=(parameter_opt + " --spoof-mac 0")
	if init.var['checksum']:	parameter_opt=(parameter_opt + " --badsum")
	if init.var['zombie']:		parameter_opt=(parameter_opt + " -sI " + init.var['zombie'])
	if init.var['sourceport']:	parameter_opt=(parameter_opt + " --source-port " + init.var['sourceport'])
	if init.var['port']:		parameter_opt=(parameter_opt + " -p " + init.var['port'])
	if init.var['decoy']=="y":	parameter_opt=(parameter_opt + " -D RND:20")
	
	printAlert(0,"Scanning Target: "+init.var['target']+" wait it may take a few minutes.")

	OSMATCHs=[]
	SERVICEs=[]
	INFORMEs=[]
	MAC="Unknow"
	VENDOR="Unknow"
	Space()
	#print(NMAP_PATH+" "+parameter+" "+init.var['target']+" -oX tmp/portScanner-tmp.xml > null "+parameter_opt)
	commands.getoutput(NMAP_PATH+" "+parameter+" "+init.var['target']+" -oX tmp/portScanner-tmp.xml "+parameter_opt+" > null")
	tree = ET.parse('tmp/portScanner-tmp.xml')
	root = tree.getroot()
	for host in root.findall('host'):
		for address in host.findall('address'):
			p=address.get('addr')
			if not address.get('vendor'):
				VENDOR=VENDOR 
			else:
				VENDOR=address.get('vendor')
			if p.find(":") <= 0 :
				IP=address.get('addr')
			else: 
				MAC=address.get('addr')
		for ports in host.findall('ports'):
			for port in ports.findall('port'):
				PROTOCOL=port.get('protocol')
				PORT=port.get('portid')
				for service in port.findall('service'):
					if not service.get('product'):
						product="{NULL}"
						version="{NULL}"
						info="{NULL}"	
					else:
						product=service.get('product')
						version=service.get('version')
						info=service.get('extrainfo')
					product=str("{NULL}" if product is None else product)
					version=str("{NULL}" if version is None else version)
					info=str("{NULL}" if info is None else info)
					SERVICEs.append(colors[7]+service.get('name')+colors[0]+" ["+product+"] "+version+info+" "+colors[10]+colors[3]+PROTOCOL+"-Port: "+PORT+colors[0])

		for hostscript in host.findall('hostscript'):
			for script in hostscript.findall('script'):
				if script.get('id') == 'smb-os-discovery':
					INFORMEs.append(script.get('output'))

		for os in host.findall('os'):
			for osmatch in os.findall('osmatch'):
				OSMATCHs.append(osmatch.get('name'))
		print " Ip address: "+colors[2]+init.var['target']+colors[0]
		print " Mac       : "+MAC
		print " Vendor    : "+VENDOR
		print " OS Matchs : "
		for os in OSMATCHs:
			print "             "+os
		print " Services  : " 				
		for services in SERVICEs:
			print "             "+str(services) 
		print " Report    :"
		for informer in INFORMEs:
			informer=str("{NULL}" if informer is "" else informer)
			print str(informer) 
	if init.var['save']:
		commands.getoutput('cp tmp/portScanner-tmp.xml tmp/'+init.var['save']+' > null')
		print("\n  Copy of scanning saved: tmp/"+init.var['save'])
	commands.getoutput('rm tmp/portScanner-tmp.xml > null')
	Space()

# END CODE MODULE ############################################################################################
