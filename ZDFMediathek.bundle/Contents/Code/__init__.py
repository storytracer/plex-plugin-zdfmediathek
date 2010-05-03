# +++++ ZDF Mediathek Plugin for Plex v0.1 alpha +++++
#
# (C) 2010 by Sebastian Majstorovic
# 
# Licensed under the GPL, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#    http://www.gnu.org/licenses/gpl-3.0-standalone.html
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/zdfmediathek"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art.png'
ICON          = 'icon.png'

SHORT_CACHE_INTERVAL        = 300 #five minutes
CACHE_INTERVAL              = 1800 #half hour
LONG_CACHE_INTERVAL         = 604800 #one week
DEBUG                       = False

BASE_URL = "http://www.zdf.de"
URL_DATES = "http://www.zdf.de/ZDFmediathek/hauptnavigation/sendung-verpasst?flash=off"

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def VideoMainMenu():
    dir = MediaContainer(viewGroup="List")
    site = XML.ElementFromURL(URL_DATES, True)
	
    dateElements = site.xpath("//ul[@class='subNavi']/li/a")
    elementsCount = len(dateElements)
    for i in range(0, elementsCount):
      dateElement = dateElements[i]
      url = str(dateElement.xpath('@href')[0])
      date = dateElement.text
      description = date[2:]
      dir.Append(Function(DirectoryItem(DateMenu, title = description), arg = url))

    return dir

def DateMenu(sender, arg):
  dir = MediaContainer(viewGroup="InfoList")
  Log(BASE_URL + arg)
  site = XML.ElementFromURL(BASE_URL + arg, True)
  
  showElements = site.xpath("//div[@class='beitragListe']//li")
  elementsCount = len(showElements)
  for i in range(0, elementsCount):
    showElement = showElements[i]
    link_element = showElement.xpath(".//b/a")[0]
    show_url = str(link_element.xpath('@href')[0])
    show_title = str(link_element.text)
    subtitleElements = showElement.xpath(".//p[@class='grey']/a")
    showSubtitle = subtitleElements[len(subtitleElements)-1].text
    
    img_url = str(showElement.xpath(".//img")[0].xpath("@src")[0])
    img_url_parts = img_url.split("/")
    img_url_parts.pop()
    large_img_url = "/".join(img_url_parts)
    large_img_url = BASE_URL + large_img_url.replace("94x65", "485x273")
    
    showDetails = LoadShowDetails(show_url)
    if (len(showDetails) > 0):
      dir.Append(VideoItem(showDetails[0], title = show_title, subtitle = showSubtitle, summary = showDetails[1], thumb = large_img_url))
    
  return dir
  
def LoadShowDetails(url):
  site = XML.ElementFromURL(BASE_URL + url, True, errors='ignore')
  summaryElements = site.xpath("//p[@class='kurztext']")
  if (len(summaryElements) > 0):
    summaryElement = summaryElements[0]
    summaryText = summaryElement.text
    
    streamURLElements = site.xpath("//ul[@class='dslChoice']/li/a")
    streamURL = str(streamURLElements[1].xpath('@href')[0])
    
    return [streamURL, summaryText]
    
  return []