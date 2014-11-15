import json
import random
import sys
import cPickle as pickle

def generate_nodes(n):
   """Create a list of n nodes with various attributes.
   Current attributes:
   Name
   City
   Date of Origin
   Image Link
   Wikipedia Link
   List of genres
   List of labels
   List of associated acts
   """
   nodes = []
   names = {}
   labels = {}
   name_list = [chr(i) for i in xrange(65,123)]
   city_list = pickle.load(open( "cities.p", "rb"))
   usable_names = set(name_list)
   image_list = ["http://upload.wikimedia.org/wikipedia/commons/6/62/Jaco_pastorius_87.jpg", 
                 "http://upload.wikimedia.org/wikipedia/commons/0/0a/Charles_Mingus_1976.jpg"]
   wiki_list = ["http://en.wikipedia.org/wiki/Jaco_Pastorius", 
                "http://en.wikipedia.org/wiki/Charles_Mingus"]
   genre_list = [chr(i) for i in xrange(65,123)]
   label_list = [chr(i) for i in xrange(65,123)]
   for i in xrange(0, n):
      current_dict = {"index": i,
                   "name": random.sample(usable_names,1)[0],
                   "origin_city": random.choice(city_list + ["NULL"]),
                   "origin_date": random.choice(range(1975,2014) + ["NULL"]),
                   "image_link": random.choice(image_list + ["NULL"]),
                   "wiki_link": random.choice(wiki_list),
                   "genre_list": random.sample(genre_list, random.choice(range(1,6))),
                   "label_list": random.sample(label_list, random.choice(range(1,4))),
                   "associated_acts": random.sample(name_list, random.choice(range(1,4)))
      }
      nodes.append(current_dict)
      usable_names.remove(current_dict["name"])
   
   return nodes

def generate_links(nodes):
   """Create a list of O(n^2) set of nodes with various attributes
   Current attributes:
   NLP score 1
   NLP score 2
   List of shared labels
   List of shared genres
   Associated acts
   """
   links = []
   for i in xrange(0,len(nodes)):
      for j in xrange(i+1, len(nodes)):
         current_dict = {"index": (i, j),
         "source": i,
         "target": j,
         "nlp_1": random.random(),
         "nlp_2": random.random(),
         "shared_genres": list(set(nodes[i]["genre_list"]) & set(nodes[j]["genre_list"])),
         "shared_labels": list(set(nodes[i]["label_list"]) & set(nodes[j]["label_list"])),
         "associated_acts": nodes[i]["name"] in nodes[j]["associated_acts"] or nodes[j]["name"] in nodes[i]["associated_acts"]
         }   
         links.append(current_dict)
   
   return links

def main():
   """Generates a json graph of fake data so that I can play around with it in d3.js before my scrapers are set up"""
   if len(sys.argv) != 3:
      raise Exception("Incorrect number of arguments, please input number of nodes, number of links, and filename")
   num_nodes = int(sys.argv[1])
   filename = sys.argv[2]
   nodes = generate_nodes(num_nodes)
   links = generate_links(nodes)
   output_dict = {"nodes": nodes, "links": links}
   with open(filename, 'wb') as fp:
      json.dump(output_dict, fp)

if __name__ == "__main__":
   main()