import requests
import json
import cPickle as pickle
import os
import time
import urllib2
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer

artist_dict = {}
def get_lyrics(lyrics_link):
   time.sleep(0.5) # add waiting limit
   data = {'link':lyrics_link, 'genre':'rock'}
   url = 'http://genius-api.com/api/lyricsInfo'
   headers = {'Content-type': 'application/json'}
   r = requests.post(url, data=json.dumps(data), headers=headers, verify=False) 
   data_dict = json.loads(r.text)
   return data_dict[u'lyrics'][u'sections']

def get_popular_songs_by_artist(artist):
   data = {'name':artist, 'genre':'rap'}
   url = 'http://genius-api.com/api/artistInfo'
   headers = {'Content-type': 'application/json'}
   r = requests.post(url, data=json.dumps(data), headers=headers, verify=False) 
   data_dict = json.loads(r.text)
   popular_songs = data_dict[u'popularSongs']
   return popular_songs

def get_lyric_blob(lyrics_dict):
   output = ""
   for section in lyrics_dict:
     verses = section[u'verses']
     for verse in verses:
        if u'content' in verse:
           verse_lyrics = verse[u'content']
           output += ' ' + verse_lyrics
   return output.replace('\n', ' ')

def get_popular_song_lyrics(artist):
   popular_songs = get_popular_songs_by_artist(artist)
   artist_lyrics_dict = {}
   for song in popular_songs:
      link = song[u'link'].replace('http://rapgenius.com','')
      artist_lyrics_dict[song[u'name']] = get_lyric_blob(get_lyrics(link))
   return artist_lyrics_dict

def compare_artists(artist_1, artist_2, artist_dict):
   vect = TfidfVectorizer(min_df=1)
   artist_1_song_dict = artist_dict[artist_1]
   artist_1_songs = [artist_1_song_dict[key] for key in artist_1_song_dict.keys()]
   artist_2_song_dict = artist_dict[artist_2]
   artist_2_songs = [artist_2_song_dict[key] for key in artist_2_song_dict.keys()]
   tfidf = vect.fit_transform(artist_1_songs + artist_2_songs)
   comparison_matrix = (tfidf * tfidf.T).A
   closest_songs = []
   num_artist_1, num_artist_2 = len(artist_1_songs), len(artist_2_songs)
   for i in xrange(0, num_artist_1): #loop artist 1 songs
      closest_song = max(comparison_matrix[num_artist_1:,i])
      closest_songs.append(closest_song)
   for i in xrange(0, num_artist_1): #loop artist 2 songs
      closest_song = max(comparison_matrix[i,num_artist_1:])
      closest_songs.append(closest_song)
   return comparison_matrix

fail_dict = {}

def gather_all_songs(artist_list, fail_dict):
   for artist in artist_list:
      artist_filename = 'lyrics_files/'+artist+'_songs.p'
      time.sleep(1) #don't want to get blocked from the website
      if not os.path.isfile(artist_filename) and artist not in fail_dict:
         print artist
         try:
            songs = get_popular_song_lyrics(artist)
            print 'got songs'
            pickle.dump(open(artist_filename, 'wb'), songs)
         except: fail_dict[artist] = None

def get_all_NLP_data(artist_dict):
   artists = artist_dict.keys()
   comparison_dict = {}
   num_artists = len(artists)
   for i in xrange(0,num_artists - 1):
      for j in xrange(i+1, num_artists):
        output_dict[(artists[i], artists[j])] = compare_artists(artists[i],artists[j], artist_dict)
   return comparison_dict







#return list of different values, using different averaging techniques   