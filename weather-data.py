#!/usr/bin/env python

# Grab weather / irrigation data from the web and compute the irrigation water needed.

# NOTICE: You will need to change some items in this program to configure it for your location.
#         Change the GENERAL SETTINGS jut below, then go to the bottom and select and configure
#         the DATA SOURCES for your location.

# You will need to install BeatifulSoup - it processes web pages (HTML, XML, etc.)
# On my Raspberry Pi all I did this to install it: apt-get install python-bs4

# Note: To install a missing python module foo do "easy_install foo"
#   (or the new way is "pip install foo" but you might have to do 
#    "easy_install pip" first)

from bs4 import BeautifulSoup
import urllib2
import re
import sys
import unicodedata
#from time import sleep


#### GENERAL SETTINGS ####

# For an average day over the growing season (ie. Spring, Summer and Fall),
# how much water (in inches) does your plants (ie. grass) need each day?
water_needed_daily = 0.15  

#### END OF GENERAL SETTINGS ####


# from http://stackoverflow.com/questions/1197981/convert-html-entities
def asciify2(s):
  matches = re.findall("&#\d+;", s)
  if len(matches) > 0:
    hits = set(matches)
    for hit in hits:
      name = hit[2:-1]
      try:
        entnum = int(name)
        s = s.replace(hit, unichr(entnum))
      except ValueError:
        pass

  matches = re.findall("&\w+;", s)
  hits = set(matches)
  amp = "&amp;"
  if amp in hits:
    hits.remove(amp)
  for hit in hits:
    name = hit[1:-1]
    if htmlentitydefs.name2codepoint.has_key(name):
      #s = s.replace(hit, unichr(htmlentitydefs.name2codepoint[name]))
      s = s.replace(hit, "")
  s = s.replace(amp, "&")
  return s

def opensoup(url):
  request = urllib2.Request(url)
  request.add_header("User-Agent", "Mozilla/5.0")
  # To mimic a real browser's user-agent string more exactly, if necessary:
  #   Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.14) 
  #   Gecko/20080418 Ubuntu/7.10 (gutsy) Firefox/2.0.0.14
  pagefile = urllib2.urlopen(request)
  soup = BeautifulSoup(pagefile)
  pagefile.close()
  return soup

def asciify(s):
  #print "DEBUG[", type(s), "]"
  return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

# remove extra whitespace, including stripping leading and trailing whitespace.
def condense(s):
  s = re.sub(r"\s+", " ", s, re.DOTALL);  #$s =~ s/\s+/\ /gs;
  return s.strip()

# this gets rid of tags and condenses whitespace
def striptags(s):
  #print "DEBUG[", type(s), "]"
  s = re.sub(r"\<span\s+style\s*\=\s*\"display\:none[^\"]*\"[^\>]*\>[^\<]*\<\/span\>",
             "", s)
  s = re.sub(r"\&\#160\;", " ", s)
  return condense(re.sub(r"\<[^\>]*\>", " ", s))


#### DATA SOURCES ####

# WeatherReach
# An excellent data source, perhaps the best
# Only covers parts of the USA
# Gives the inches of water lawn needs per day, based on weather conditions
# Go to this map (http://access.weatherreach.com/map_stations) and click on closest station
# Copy URL (web address) from browser and paste in place of defalut one below
soup = opensoup('http://access.weatherreach.com/StationDetail?StationID=138&TableTimeInt=60')
# Shouldn't need to change anything below this line
irrigation_section = soup.find(id='irrigateinfo')  # Extract the irrigation section of the webpage
rows = irrigation_section.find_all('td')  # Extract the two table rows
irrigation_required = float(re.findall("\d+\.\d+", row[1].contents[0])[0])  # From the 2nd row [1], extract the irrigation required
print 'Weather adjustment: {:.0%}'.format(irrigation_required / water_needed_daily)
