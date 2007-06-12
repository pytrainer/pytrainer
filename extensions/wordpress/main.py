#!/usr/bin/env python
import wordpresslib
from optparse import OptionParser
import os


def main():
	profile_image = ""
	googlemaps_html = ""

	wordpress = "http://www.e-oss.net/wordpress/xmlrpc.php"
	user = "admin"
	password = "MhNe13dD"

	# prepare client object
	try: 
		wp = wordpresslib.WordPressClient(wordpress, user, password)
	except:
		return "Url, user or pass are incorrect. Check your configuration"

	# select blog id
	wp.selectBlog(0)
	
	# upload image for post
	#imageSrc = wp.newMediaObject('python.jpg')
	htmlfile = wp.newMediaObject('/tmp/virtual_dir/index.html')
	print htmlfile

	# create post object
	post = wordpresslib.WordPressPost()
	post.title = 'Test post'
	post.description = '''
	Python is the best programming language in the earth !
	
	<iframe width="520" height="480" src="%s"> Se necesitan frames para ver esta pagina </iframe>
	
	''' % htmlfile
	post.categories = (['Blogging'])
	
	#pubblish post
	idNewPost = wp.newPost(post, False)
	
parser = OptionParser()
parser.add_option("-d", "--device", dest="device")
(options,args) =  parser.parse_args()

tmpgpx = "/tmp/reg.gpx"
os.system("gpsbabel -t -i garmin -f %s -o gpx -F %s" %(options.device,tmpgpx))

print tmpgpx
print main()
