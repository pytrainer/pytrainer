from lxml import etree
from pytrainer.upgrade.context import UPGRADE_CONTEXT

def upgrade(migrate_engine):
    config_file = UPGRADE_CONTEXT.conf_dir + "/conf.xml"
    parser = etree.XMLParser(encoding="UTF8", recover=True)
    xml_tree = etree.parse(config_file, parser=parser)
    config_element = xml_tree.getroot()
    del config_element.attrib["DB_version"]
    xml_tree.write(config_file, xml_declaration=True, encoding="UTF-8")
