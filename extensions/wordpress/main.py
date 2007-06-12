#!/usr/bin/env python
from ftplib import FTP

def main():
	user="vud1"
	password=""
	server="www.kernet.es"
	path = ""
	profile_image = ""
	googlemaps_html = ""

	#probamos la conexion ftp con el servidor
	try: 
		ftp = FTP(server)
	except:
		return "Cant established server connection"
	
	try:
		ftp.login(user,password)
	except:
		return "User or password incorrect"

	ftp.cwd(path)
	fimage = open(profile_image, 'wb')
	fhtml = open(googlemaps_html, "w")

	ftp.quit()

print main()
