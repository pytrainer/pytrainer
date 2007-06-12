#!/usr/bin/env python
import wordpresslib

def main():
	user="admin"
	password="MhNe13dD"
	server="www.kernet.es"
	wordpress="http://www.e-oss.net/wordpress/xmlrpc.php"
	profile_image = ""
	googlemaps_html = ""

	# prepare client object
	wp = wordpresslib.WordPressClient(wordpress, user, password)

	# select blog id
	wp.selectBlog(0)
	
	# upload image for post
	imageSrc = wp.newMediaObject('img.jpg')

	if imageSrc:
		# create post object
		post = wordpresslib.WordPressPost()
		post.title = 'Test post'
		post.description = '''
		Python is the best programming language in the earth !
	
		<img src="%s" />
	
		''' % imageSrc
		post.categories = (wp.getCategoryIdFromName('Python'),)
	
		# pubblish post
		idNewPost = wp.newPost(post, True)
	
		print
		print 'posting successfull!'
	
print main()
