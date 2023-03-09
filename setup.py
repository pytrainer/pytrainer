#!/usr/bin/env python
#
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
from glob import glob

def install_locale(lang):
	return "share/locale/%s/LC_MESSAGES" %lang, glob("locale/%s/LC_MESSAGES/*.mo" %lang)

def install_plugin(plugin_name):
	return "share/pytrainer/plugins/%s" %plugin_name, glob("plugins/%s/*.*" %plugin_name)

def install_extension(extension_name):
	return "share/pytrainer/extensions/%s" %extension_name, glob("extensions/%s/*" %extension_name) 

# Dynamically calculate the version based on pytrainer.VERSION.
version = __import__('pytrainer').get_version()

setup( 	name = "pytrainer",
	version = version,
	description="The free sport tracking center",
	long_description="Pytrainer is a tool to log all your sport excursion coming from GPS devices (with a focus on ForeRunner 205, 305 and 405) or GPX (http://www.topografix.com) files. Pytrainer supports GPS track files and displays it in graphs, maps... ",
	author="Fiz Vazquez, John Blance, David Garcia Granda, Arnd Zapletal, Nathan Jones, Arto Jantunen",
	maintainer_email="pytrainer-devel@lists.sourceforge.net",
	url="https://github.com/pytrainer",
	license="GNU General Public License (GPL)",
	packages=[	'pytrainer',
			'pytrainer.util',
			'pytrainer.core',
			'pytrainer.gui',
			'pytrainer.extensions',
			'pytrainer.lib',
			'pytrainer.upgrade'
			],
	package_data={
		'pytrainer.upgrade': ['migrate.cfg', 'versions/*.sql', 'versions/*.py']
	},
	data_files=[
		('share/pytrainer/glade/',glob("glade/*.ui")),
		('share/pytrainer/glade/',glob("glade/*.png")),
		('share/pytrainer/glade/',glob("glade/*.jpg")),
		('share/pytrainer/schemas/',glob("schemas/*.xsd")),
		('share/pytrainer/imports/',glob("imports/*.py")),
		('share/pytrainer/imports/',glob("imports/*.xsl")),
		('share/pytrainer/',glob("*.style")),
		install_plugin("garmin-gpx"),
		install_plugin("garmin-hr"),
		install_plugin("garmin-hr-file"),
		install_plugin("garmin-tcxv2"),
		install_plugin("googleearth"),
		install_plugin("garmintools"),
		install_plugin("garmintools_full"),
		install_plugin("garmin-fit"),
		('share/pytrainer/plugins/garmin-fit/bin/', ["plugins/garmin-fit/bin/fit2tcx"]),
		('share/pytrainer/plugins/garmin-fit/bin/Garmin/', ["plugins/garmin-fit/bin/Garmin/FIT.pm"]),
		install_extension("wordpress"),
		install_extension("openstreetmap"),
		install_extension("fixelevation"),
		install_extension("gpx2garmin"),
		install_extension("stravaupload"),
		(install_locale("ca")),
		(install_locale("cs")),
		(install_locale("da")),
		(install_locale("de")),
		(install_locale("es")),
		(install_locale("eu")),
		(install_locale("fr")),
		(install_locale("gl")),
		(install_locale("no")),
		(install_locale("pl")),
		(install_locale("pt")),
		(install_locale("ru")),
		(install_locale("sv")),
		('share/pixmaps/',['pytrainer.png']),
		('share/applications/',['pytrainer.desktop'])
		],
	scripts=['bin/pytrainer'],
	install_requires=['sqlalchemy-migrate',
			'SQLAlchemy<2.0',
			'python-dateutil',
			'matplotlib',
			'lxml'],
	test_suite='pytrainer.test',
	tests_require=['mysqlclient', 'psycopg2'],
	zip_safe=False
)
