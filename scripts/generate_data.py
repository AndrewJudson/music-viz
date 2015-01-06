from nlp import *
from rap_genius import *
from wikipedia_scraping import *

def json_dump(filename):
   """Prepare all of the previously gathered data for use in the d3 visualization"""
   print "Transferring data to json file."
   cities = pickle.load(open("cities.p", 'rb'))
   comparisons = pickle.load(open("city_comparisons.p", 'rb'))
   diversity = pickle.load(open("city_diversity.p", 'rb'))
   nodes = []
   to_delete = []
   for city in cities: #redundant if I fix it in the data gathering file
      if cities[city]["loc"] == None or np.isnan(diversity[city]):
         to_delete.append(city)
   for city in to_delete:
       del cities[city]
   city_keys = cities.keys()
   city_indices = {}
   for i in xrange(0, len(city_keys)):
      current_dict = {"index": i,
                      "name": city_keys[i],
                      "lat": cities[city_keys[i]]["loc"][0],
                      "lon": cities[city_keys[i]]["loc"][1],
                      "artists": cities[city_keys[i]]["artists"],
                      "diversity": diversity[city_keys[i]]
                     }
      city_indices[city_keys[i]] = i
      nodes.append(current_dict)
   print "Created graph nodes."
   links = []
   comparison_pairs = comparisons.keys()
   for pair in comparison_pairs:
      if pair[0] in cities and pair[1] in cities:
         if not np.isnan(comparisons[pair]):
            current_dict = {"index": (city_indices[pair[0]], city_indices[pair[1]]),
                            "source": city_indices[pair[0]],
                            "target": city_indices[pair[1]],
                            "source_name":city_keys[city_indices[pair[0]]], 
                            "target_name":city_keys[city_indices[pair[1]]],
                            "nlp_1": comparisons[pair]
                           }   
            links.append(current_dict)
   print "Created graph links."
   destinations = set([links[i]["source_name"] for i in xrange(0, len(links))] + [links[i]["target_name"] for i in xrange(0, len(links))])
   nodes = [node for node in nodes if node["name"] in destinations] #may be redudant after fixes in other gathering methods
   output_dict = {"nodes": nodes, "links": links}
   with open(filename, 'wb') as fp:
      json.dump(output_dict, fp)
   print "json file created."

def main():
   """Gather all the data necessary for the project. I originally gathered
   the data via the interpreter running the seperate wikipedia, nlp, and genius gathering
   methods. I have combined it all here in case anyone wants an easier way to just run
   everything. There are a lot of improvements that could be made to the data gathering
   in regards to parallelizing a lot of the scraping/computation.

   """
   artists = get_alternative_rock_band_list()
   pickle_dump_cities(artists)
   pickle_dump_songs(artists)
   artist_comparisons()
   city_comparisons()
   json_dump("data/city_data.json")

if __name__ == "__main__":
   main()