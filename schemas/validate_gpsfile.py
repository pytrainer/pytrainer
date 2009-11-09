#!/usr/bin/python

import os, sys
from optparse import OptionParser
from lxml import etree

def main():
	#Setup usage and permitted options
	usage = "usage: %prog [options] filename"
	parser = OptionParser(usage=usage)
	parser.add_option("-s", "--schema",
        dest="schema",
        help="specify schema to validate FILE against")
	parser.add_option("-v", "--verbose",
		action="store_true", dest="verbose", default=False,
		help="show extra information (including why validation fails)")
	(options, args) = parser.parse_args()
	xmlfiles = []
	for arg in args:
		if not os.path.isfile(arg):
				print "File %s does not exist. Removing from list" % arg
		else:
			xmlfiles.append(arg)
	#Ensure that at least one file has been supplied to validate
	if len(xmlfiles) < 1:
		parser.error("must supply at least one file to validate")
	#If a specific schema has been passed, ensure the file exists
	if options.schema:
		if os.path.isfile(options.schema):
			schemas = [options.schema]
		else:
			parser.error("Schema specified must exist")
	else:
		schemas = ["Topografix_gpx11.xsd", "Cluetrust_gpxdata10.xsd", "GarminTrainingCenterDatabase_v1.xsd", "GarminTrainingCenterDatabase_v2.xsd"]

	for schema in schemas:
		print "Validating against schema: %s" % schema
		#Parse XML schema
		xmlschema_doc = etree.parse(schema)
		xmlschema = etree.XMLSchema(xmlschema_doc)
		#Load an XML file and try to validate it
		for xmlfile in xmlfiles:
			xmldoc = etree.parse(xmlfile)
			if (xmlschema.validate(xmldoc)):
				print "\033[0;32mFile %s validates against %s\033[m" % (xmlfile, schema)
			else:
				print "\033[0;31mFile %s does not validate against %s\033[m" % (xmlfile, schema)
				if options.verbose:
					log = xmlschema.error_log
					error = log.last_error
					print error

if __name__ == "__main__":
    main()

