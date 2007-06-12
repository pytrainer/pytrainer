#!/usr/bin/env python

"""
	Small example script that publish post with JPEG image
"""

# import library
import wordpresslib

print 'Example of posting.'
print

wordpress = "http://www.e-oss.net/wordpress/xmlrpc.php"
user = "admin"
password = "MhNe13dD"

# prepare client object
wp = wordpresslib.WordPressClient(wordpress, user, password)

# select blog id
wp.selectBlog(0)
	
# upload image for post
imageSrc = wp.newMediaObject('python.jpg')

if imageSrc:
	# create post object
	post = wordpresslib.WordPressPost()
	post.title = 'Test post'
	post.description = '''
	Python is the best programming language in the earth !
	
	<img src="%s" />
	
	''' % imageSrc
	post.categories = (['Blogging'])
	
	#pubblish post
	idNewPost = wp.newPost(post, False)
	
	print
	print 'posting successfull!'
	

