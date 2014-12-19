import os
import cPickle as pickle
import nltk
import numpy as np
import string
from sklearn.feature_extraction.text import TfidfVectorizer

def compare_artists(artist_1, artist_2, songs_dict):
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
   tfidf = vect.fit_transform(artist_1_songs + artist_2_songs)
   comparison_matrix = (tfidf * tfidf.T).A
   closest_songs = []
   song_indices_1 = range(0,len(artist_1_songs))
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

def all_comparisons():
   file_names = os.listdir("lyrics_files")
   songs_dict = {song_file[:-8]: pickle.load(open("lyrics_files/" + song_file, 'rb')) for song_file in file_names} # filenames end with _songs.p, so we use -8 to delete that
   artists = artist_song_dict.keys()
   output_dict = {}
   artist_pairs = []
   for i in xrange(0, len(artists) - 1):
      for j in xrange(i+1, len(artists)):
         artist_pairs.append((artists[i],artists[j]))
   for pair in artist_pairs:
      output_dict[pair] = compare_artists(pair[0], pair[1], songs_dict)
      print pair, output_dict[pair]
   pickle.dump(output_dict, open("artist_comparisons.p", "wb"))