import re
import requests
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
         bands_dict[link.text] = u"http://en.wikipedia.org" + link['href']
   for key in bands_dict.keys():
      fixed_name = re.sub('\([^)]*\)', '', key)
      bands_dict[fixed_name] = bands_dict[key]
   paren_regex = re.compile('\(.*\)') #Todo: combine regex into one
   brace_regex = re.compile('\[.*\]')
   for key in bands_dict.keys():
      if re.search(paren_regex, key) or re.search(brace_regex, key): #delete names with e.g. (band) in them, and citation links like [18]
         del bands_dict[key]
   return bands_dict

def get_soup(link):
   return BeautifulSoup(requests.get(link).text)

def find_table_string(soup, string):
   table = soup.findAll('tr')
   for row in table:
      try:
         if row.contents[1].contents[0] == string:
            return row.contents[3]
      except:
         return None

def get_soup_city_link(soup):
   element = find_table_string(soup, u'Origin')
   print element
   if element != None:
      try:
         link = u"http://en.wikipedia.org" + element.find('a')['href']
         return {element.find('a').text: link}
      except:
         return {element.text: None}
   return {None: None}

def get_soup_origin_date(soup):
   element = find_table_string(soup, u'Years active')
   print element
   if element != None:
      date = element.text.replace(u'\u2013', u'\xa0').replace(u'-', u'\xa0').split(u'\xa0')#unicode for '-', unicode for ' '
      return date[0]
   return None

def get_city_lon_lat(city_link):
   soup = get_soup(city_link)
   element = find_table_string(soup, u'Country')
   in_US = True
   print element
   if element != None:
      try:
         if element.find('a').text != u'United States':
            in_US = False
      except:
         pass 
   
   if in_US:
      latitude = soup.findAll('span', {"class" : "latitude"})[0].text
      longitude = soup.findAll('span', {"class" : "longitude"})[0].text
      latitude, longitude = conversion(latitude), conversion(longitude)
      return (latitude, longitude)

#http://stackoverflow.com/questions/10852955/python-batch-convert-gps-positions-to-lat-lon-decimals
def conversion(old):
    direction = {'N':-1, 'S':1, 'E': -1, 'W':1}
    new = old.replace(u'°',' ').replace(u'\u2032',' ').replace(u'\u2033',' ')
    new = new.split()
    new_dir = new.pop()
    new.extend([0,0,0])
    return (int(new[0])+int(new[1])/60.0+int(new[2])/3600.0) * direction[new_dir]

def get_all_artist_data():
   artists = get_alternative_rock_band_list()
   for artist in artists:
      soup = get_soup(artists[artist])
      print artist
      origin_date = get_soup_origin_date(soup)
      origin_city = get_soup_city_link(soup)
      lat_lon = get_city_lon_lat(origin_city)
      print origin_date, origin_city
