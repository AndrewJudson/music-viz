#Lyrical Similarity By City: An Experiment in NLP and Data Visualization
This project is a web visualization of NLP data gathered from data scraped from the internet. The list of musicians, and their respective origin (as well as city latitude and longitude) were scraped from Wikipedia. The lyrics data was scraped from Rap Genius using the Genius API.

**Dataset:** List of alternative rock musicians/their origin cities from Wikipedia, their most popular song lyrics from Genius.

**Methodology** Scraping/dataset construction was done in Python. Visualization in d3.js and HTML/CSS.  We construct the TF-IDF comparision using 1-grams, and only include cities with more than one artist with lyrics data. More implementation details are visible in the source.

I would be very interested if someone wanted to do a more rigorous, robust exploration of the data, or related datasets. Additionally, it would be interesting to have a better source of data - much of the limitations in this dataset were due to limitations in the data provided by Wikipedia/Genius.