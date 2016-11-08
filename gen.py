import os
from os import path
import shutil

import cleancss

import db

levelwig_dir = path.normpath(path.dirname(path.abspath(__file__)))
public_dir = path.join(levelwig_dir, 'public')
css_dir = path.join(levelwig_dir, 'css')

def generate(app):
	try:
		os.mkdir(public_dir)
	except FileExistsError:
		pass
	# do this instead of shutil.rmtree in case public is a symlink
	for filename in os.listdir(public_dir):
		abspath = path.join(public_dir, filename)
		if path.isdir(abspath):
			shutil.rmtree(abspath)
		else:
			os.unlink(abspath)

	posts = db.iter_posts(allowed_flags=0)
	stream = app.template_engine.stream('root.jinja2', {'posts': posts})
	with open(path.join(public_dir, 'index.html'), 'wb') as f:
		for buf in stream:
			f.write(buf)

	for post in db.iter_posts(allowed_flags=db.PostFlag.draft):
		stream = app.template_engine.stream('post.jinja2', {'post': post})
		with open(path.join(public_dir, '%d.html' % post.id), 'wb') as f:
			for buf in stream:
				f.write(buf)

	os.mkdir(path.join(public_dir, 'css'))
	for absdir, _, filenames in os.walk(css_dir):
		for filename in filenames:
			ccss_path = path.join(absdir, filename)
			reldir = absdir[len(css_dir):]
			relname, _ = path.splitext(path.join(reldir, filename))
			css_path = path.join(public_dir, 'css', relname) + '.css'
			with open(ccss_path, 'r') as ccss, open(css_path, 'w') as css:
				css.write(cleancss.convert(ccss))
