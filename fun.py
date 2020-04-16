import requests
from xml.dom import minidom

def get_bruce_fact():
    raw = requests.get("https://www.schneierfacts.com/rss/random").text
    dom = minidom.parseString(raw)
    return dom.getElementsByTagName("description")[1].firstChild.data
