#data from http://openflights.org/data.html
import csv
import cPickle as pickle
cities_list = []
with open("airports.dat", 'rb') as f:
   reader = csv.reader(f)
   for row in reader:
      if row[3]=="United States":
         cities_list.append({row[2]:(row[6],row[7])})
with open("cities.p", 'wb') as handle:
   pickle.dump(cities_list, handle)