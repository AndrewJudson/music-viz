#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import nltk
import numpy as np
import os
import cPickle as pickle
import string
from sklearn.feature_extraction.text import TfidfVectorizer

#modified from http://stackoverflow.com/questions/8897593/similarity-between-two-text-documents
def compare_artists(artist_1, artist_2, songs_dict):
   """Takes in two artist names and dictionary of all songs, 
   computes tfidf values of their respective song collections.
   We then take the best match for each song, and take the weighted average (by artist).
   """
   stemmer = nltk.stem.porter.PorterStemmer()
   remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
   def stem_tokens(tokens):
     return [stemmer.stem(item) for item in tokens]
   def normalize(text):
      return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
   vect = TfidfVectorizer(min_df=1, stop_words = "english", strip_accents = "unicode", tokenizer = normalize)
   artist_1_song_dict = songs_dict[artist_1]
   artist_1_songs = [artist_1_song_dict[key] for key in artist_1_song_dict.keys()]
   artist_2_song_dict = songs_dict[artist_2]
   artist_2_songs = [artist_2_song_dict[key] for key in artist_2_song_dict.keys()]
   try:
      tfidf = vect.fit_transform(artist_1_songs + artist_2_songs)
   except:
      print "tfidf error"
      return 0
   comparison_matrix = (tfidf * tfidf.T).A
   closest_songs = []
   song_indices_1 = range(0, len(artist_1_songs))
   song_indices_2 = range(len(artist_1_songs), len(artist_1_songs) + len(artist_2_songs))
   maxes = []
   for i in song_indices_1:
      cur_max = 0
      for j in song_indices_2:
         if comparison_matrix[i][j] > cur_max:
            cur_max = comparison_matrix[i][j]
      maxes.append(cur_max)
   for i in song_indices_2:
      cur_max = 0
      for j in song_indices_1:
         if comparison_matrix[i][j] > cur_max:
            cur_max = comparison_matrix[i][j]
      maxes.append(cur_max)
   return np.average(maxes, weights = [len(artist_1_songs) / float((len(artist_1_songs) + len(artist_2_songs))) for i in xrange(0, len(artist_1_songs))] 
                             + [len(artist_2_songs) / float((len(artist_1_songs) + len(artist_2_songs))) for i in xrange(0, len(artist_2_songs))])

def artist_comparisons():
  """Compares every artist and dumps to pickle file"""
   file_names = os.listdir("lyrics_files")
   songs_dict = {song_file[:-8]: pickle.load(open("lyrics_files/" + song_file, 'rb')) for song_file in file_names} # filenames end with _songs.p, so we use -8 to delete that
   artists = songs_dict.keys()
   output_dict = {}
   artist_pairs = []
   print "Comparing artists"
   for i in xrange(0, len(artists) - 1):
      for j in xrange(i + 1, len(artists)):
         artist_pairs.append((artists[i], artists[j]))
   for pair in artist_pairs:
      print pair
      output_dict[pair] = compare_artists(pair[0], pair[1], songs_dict)
      print output_dict[pair]   
   pickle.dump(output_dict, open("artist_comparisons.p", "wb"))
   print "Pickled artist comparisons"

def compare_cities(city_1, city_2, cities_dict, artists_dict):
  """Compares two cities by getting every pair of artist comparisons
  for those cities, and averaging.
  """
   similarities = []
   for artist_1 in cities_dict[city_1]["artists"]:
      for artist_2 in cities_dict[city_2]["artists"]:
         pair_1 = (artist_1, artist_2)
         pair_2 = (artist_2, artist_1)
         if pair_1 in artists_dict:
            similarities.append(artists_dict[pair_1])
         if pair_2 in artists_dict:
            similarities.append(artists_dict[pair_2])
   return np.average(similarities)

def city_comparisons():
  """Collect every comparison for each pair of cities and dump to pickle file."""
   cities = pickle.load(open("cities.p", 'rb')) #Cities is a dict of style {New York: {artists:[Artist 1, artist 2], loc = [156, 78]}, Los Angeles:[Artist 3]}... etc
   artists = pickle.load(open("artist_comparisons.p", 'rb'))
   city_list = cities.keys()
   comparisons = {}
   self_comparisons = {}
   print "Comparing cities"
   for i in xrange(0, len(city_list) - 1):
      for j in xrange(i, len(city_list)):
         print city_list[i], city_list[j]
         if i != j:
            city_1, city_2 = city_list[i], city_list[j]
            comparisons[(city_1, city_2)] = compare_cities(city_1, city_2, cities, artists)
         else:
            city_1, city_2 = city_list[i], city_list[j]
            self_comparisons[city_1] = compare_cities(city_1, city_2, cities, artists)
   pickle.dump(comparisons, open("city_comparisons.p", 'wb'))
   pickle.dump(self_comparisons, open("city_diversity.p", 'wb'))
   print "Pickled city comparisons"