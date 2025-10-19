#!/usr/bin/env python
#
from setuptools import setup
from glob import glob

def install_locale(lang):
	return "share/locale/%s/LC_MESSAGES" %lang, glob("locale/%s/LC_MESSAGES/*.mo" %lang)

def install_plugin(plugin_name):
	return "share/pytrainer/plugins/%s" %plugin_name, glob("plugins/%s/*.*" %plugin_name)

def install_extension(extension_name):
	return "share/pytrainer/extensions/%s" %extension_name, glob("extensions/%s/*" %extension_name) 

setup(
	data_files=[
		('share/pytrainer/glade/',glob("glade/*.ui")),
		('share/pytrainer/icons/',glob("data/icons/*.svg")),
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
		('share/pytrainer/plugins/garmin-fit/bin/', ["plugins/garmin-fit/bin/fit2tcx.pl"]),
		('share/pytrainer/plugins/garmin-fit/bin/Geo/', ["plugins/garmin-fit/bin/Geo/FIT.pm"]),
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
	test_suite='pytrainer.test',
)
