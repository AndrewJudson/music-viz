import cPickle as pickle
import csv
#csv downloaded from http://ezlocal.com/blog/post/top-5000-us-cities-by-population.aspx

cities_list = []
with open("cities.csv", 'rU') as f:
   reader = csv.reader(f, dialect = csv.excel_tab)
   for row in reader:
      cities_list.append(row[0])
with open("cities.p", 'wb') as handle:
   pickle.dump(cities_list, handle)