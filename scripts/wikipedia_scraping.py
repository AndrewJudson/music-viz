#!/usr/bin/python
# -*- coding: utf-8 -*-
import cPickle as pickle
import re
import requests
import sys
import time
from bs4 import BeautifulSoup

def get_alternative_rock_band_list():
   """ This returns all alternative rock bands from the Wikipedia article on alternative rock bands.
   The scraper needs to be specific because each Wiki article is formatted differently 
   and a universal method can't be applied easily at the moment. TODO: Make more general scraper
   """     
   url = "http://en.wikipedia.org/wiki/List_of_alternative_rock_artists"   
   soup = BeautifulSoup(requests.get(url).text)
   data = soup.find_all("div", class_ = "div-col columns column-width", style = "-moz-column-width: 30em; -webkit-column-width: 30em; column-width: 30em;")
   bands_dict = {}
   for div in data[:-1]:
      links = div.find_all('a')
      for link in links:
         bands_dict[link.text] = u"http://en.wikipedia.org" + link["href"]
   for key in bands_dict.keys(): #adding duplicate entries with "(band)" strings deleted. We deleted them later.
      fixed_name = re.sub("\([^)]*\)", '', key)
      bands_dict[fixed_name] = bands_dict[key]
   paren_regex = re.compile("\(.*\)") #Todo: combine regex into one
   brace_regex = re.compile("\[.*\]")
   for key in bands_dict.keys():
      if re.search(paren_regex, key) or re.search(brace_regex, key): #delete names with e.g. (band) in them, and citation links like [18]
         del bands_dict[key]
   return bands_dict

def get_soup(link):
   return BeautifulSoup(requests.get(link).text)

def find_table_string(soup, string):
   """Searches artist page soup for specific string in the summary table"""
   table = soup.findAll("tr")
   for row in table:
      try:
         if row.contents[1].contents[0] == string:
            return row.contents[3]
      except:
         return None

def get_soup_city_link(soup):
   """Scans artist page soup for city of origin"""
   element = find_table_string(soup, u"Origin")
   if element != None:
      try:
         link = u"http://en.wikipedia.org" + element.find('a')["href"]
         return {element.find('a').text: link}
      except:
         return {element.text: None}
   return {None: None}

#http://stackoverflow.com/questions/10852955/python-batch-convert-gps-positions-to-lat-lon-decimals
def conversion(old):
    """Convert degrees to latitude and longitude"""
    direction = {'N': -1, 'S': 1, 'E': -1, 'W': 1}
    new = old.replace(u'°' ,' ').replace(u'\u2032' ,' ').replace(u'\u2033' ,' ')
    new = new.split()
    new_dir = new.pop()
    new.extend([0,0,0])
    return (int(float(new[0])) + int(float(new[1])) / 60.0 + int(float(new[2])) / 3600.0) * direction[new_dir]

def get_city_lon_lat(city_link):
   """Given a Wikipedia link to a city's page, find if it is in the U.S., and if so find and record its location."""
   soup = get_soup(city_link)
   coord_string = str(soup.findAll("span", {"class" : "plainlinks nourlexpansion"}))
   in_US = True
   if "region:US" not in coord_string:
      in_US = False
   if in_US:
      latitude = soup.findAll("span", {"class" : "latitude"})[0].text
      longitude = soup.findAll("span", {"class" : "longitude"})[0].text
      latitude, longitude = conversion(latitude), conversion(longitude)
      return (latitude, longitude)

def get_all_artist_data(cities, artists_seen, artists):
   """Collects all city data for artists. Cities dictionary records output, and artists seen dictionary
   allows us to keep track of who we have analyzed, in case the method fails due to internet issues
   or Wikipedia refusing access.
   """
   for artist in artists:
      if artist in artists_seen:
         continue
      time.sleep(1) #don't want to be refused by Wikipedia
      soup = get_soup(artists[artist])
      origin_city = get_soup_city_link(soup)
      origin_city_key = origin_city.keys()[0]
      if origin_city_key != None and origin_city[origin_city_key] != None:
         origin_city_no_commas = origin_city_key.split(',')[0] #some wikipedia articles have both the city and state name in the link
         if origin_city_no_commas not in cities:
            lat_lon = get_city_lon_lat(origin_city[origin_city_key])
            cities[origin_city_no_commas] = {"artists":[artist], "loc":lat_lon}
         else:
            cities[origin_city_no_commas]["artists"].append(artist)
      artists_seen.add(artist)
      print "Examined: " + artist
   return cities

def pickle_dump_cities(artists):
   """Write cities dictionary to pickle file so we can use it later. 
   Executes the get_all_artist_data method until we've seen all artists.
   Exclude cities with latitude and longitude data (all non-US and those with malformed Wiki pages)
   """
   print "Gathering city location/artist data."
   cities = {}
   artists_seen = set([])
   artists_set = set(artists.keys())
   while(len(artists_set.difference(artists_seen)) > 0):
      try:
         get_all_artist_data(cities, artists_seen, artists)
      except:
         print "Exception: ", sys.exc_info()[0]
         time.sleep(600) # Wikipedia refusing to answer, so wait a bit
   for city in cities:
      if cities[city]["loc"] == None:
         del cities[city]
   print "Collected city location/artist data."
   pickle.dump(cities, open("cities.p", 'wb'))


