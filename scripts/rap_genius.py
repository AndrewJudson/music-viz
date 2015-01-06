#!/usr/bin/python
import cPickle as pickle
import json
import os
import requests
import time
import urllib2
from bs4 import BeautifulSoup

artist_dict = {}
def get_lyrics(lyrics_link):
   """Given a song link to Genius, return a dictionary of the verses"""
   time.sleep(0.5) # add waiting limit to prevent getting blocked
   data = {"link": lyrics_link, "genre": "rock"}
   url = "http://genius-api.com/api/lyricsInfo"
   headers = {"Content-type": "application/json"}
   r = requests.post(url, data = json.dumps(data), headers = headers, verify = False) 
   data_dict = json.loads(r.text)
   return data_dict[u"lyrics"][u"sections"]

def get_popular_songs_by_artist(artist):
   """Queries Genius for all popular songs for a particular artist"""
   data = {"name": artist, "genre": "rap"}
   url = "http://genius-api.com/api/artistInfo"
   headers = {"Content-type": "application/json"}
   r = requests.post(url, data = json.dumps(data), headers = headers, verify = False) 
   data_dict = json.loads(r.text)
   popular_songs = data_dict[u"popularSongs"]
   return popular_songs

def get_lyric_blob(lyrics_dict):
   """Collate all verses in a song"""
   output = ""
   for section in lyrics_dict:
     verses = section[u"verses"]
     for verse in verses:
        if u"content" in verse:
           verse_lyrics = verse[u"content"]
           output += ' ' + verse_lyrics
   return output.replace('\n', ' ')

def get_popular_song_lyrics(artist):
   """Collects all popular song lyrics for the artist"""
   popular_songs = get_popular_songs_by_artist(artist)
   artist_lyrics_dict = {}
   for song in popular_songs:
      link = song[u"link"].replace("http://rapgenius.com",'')
      artist_lyrics_dict[song[u"name"]] = get_lyric_blob(get_lyrics(link))
   return artist_lyrics_dict

def gather_all_songs(artist_list, fail_dict):
   """Gathers all of the songs for a given list of artists,
   with a certain amount of failures allowed
   """
   for artist in artist_list:
      artist_filename = "lyrics_files/" + artist + "_songs.p"
      time.sleep(1) #don't want to get blocked from the website
      if not os.path.isfile(artist_filename) and (artist not in fail_dict or fail_dict[artist] < 3): #retry 3 times
         print artist
         try:
            songs = get_popular_song_lyrics(artist)
            print "got songs for " + artist
            pickle.dump(songs, open(artist_filename, 'wb'))
         except: 
            if artist in fail_dict:
               fail_dict[artist] += 1
            else: 
               fail_dict[artist] = 1

def pickle_dump_songs(artists):
   """Write artist lyrics to pickle file so we can use them later. 
   Executes the gather_all_songs method until we've seen all artists.
   """
   print "Gathering lyrics data."
   if not os.path.exists("lyrics_files"):
      print "Creating lyrics_files directory"
      os.makedirs("lyrics_files")
   fail_dict = {}
   artist_list = artists.keys()
   for i in xrange(0, 3): #Genius API can fail for unknown reasons, want to make sure we gather everything so try a few times.
      print "try: ", i
      gather_all_songs(artist_list, fail_dict)
   print "Collected song data."