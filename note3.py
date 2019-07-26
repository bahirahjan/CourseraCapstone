
# coding: utf-8

# # Coursera Capstone Project
# ## The Battle of Neighborhoods 

# ## A description of the problem and a discussion of the background

# Tourist Attractions and venues in the state of Massachusetts US Data 
# Type of data being extracted is json 
# Source: https://geodata.lib.berkeley.edu/catalog/MEATOUR95PT
# Data Includes: 
# * Museum locations
# * Attractions
# * Shows the Longitude and latitude of each museum and the geometry
# * Addresses of museums 
# * Analysis the difference in names in each portal name 
# * The city of each museum 
# * postal code of each tourist attraction 
# 
# 
# 
# 

# ## What we wish to extract or solve.

# 
# 
# Finding the closest nearby museum and tourist attraction close to the main city of Boston

# In[6]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

get_ipython().system(u"conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab")
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

get_ipython().system(u"conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab")
import folium # map rendering library

print('Libraries imported.')


# In[7]:


get_ipython().system(u"wget -q -O 'data.json'  https://geodata.lib.berkeley.edu/download/file/MEATOUR95PT-geojson.json")
print('Data downloaded!')


# In[8]:


with open('data.json') as json_data:
    d_data = json.load(json_data)


# In[9]:


d_data


# In[10]:


neighborhoods_data = d_data['features']


# In[11]:


neighborhoods_data[1]


# In[12]:


# define the dataframe columns
column_names = [ 'Community','Museum', 'Latitude', 'Longitude'] 

# instantiate the dataframe
neighborhoods = pd.DataFrame(columns=column_names)


# In[13]:


neighborhoods


# In[14]:


for data in neighborhoods_data:
    borough = neighborhood_name = data['properties']['MUSEUM_ATT'] 
    neighborhood_name = data['properties']['COMMUNITY']

    neighborhood_latlon = data['geometry']['coordinates']
    neighborhood_lat = neighborhood_latlon[1]
    neighborhood_lon = neighborhood_latlon[0]

    
    neighborhoods = neighborhoods.append({'Museum': borough,
                                          'Community': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)
    


# In[15]:


neighborhoods.head()


# In[16]:


neighborhoods.describe()


# In[17]:


neighborhoods.info()


# In[18]:


get_ipython().magic(u'matplotlib inline')

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.style.use('ggplot') # optional: for ggplot-like style

# check for latest version of Matplotlib
print ('Matplotlib version: ', mpl.__version__) # >= 2.0.0


# In[27]:


neighborhoods.sort_values(['Community'], ascending=False, axis=0, inplace=True)

# get the top 5 entries
top5 = neighborhoods.head()



top5.head()


# In[36]:


print('The dataframe has {} communities and {} museums.'.format(
        len(neighborhoods['Museum'].unique()),
        neighborhoods.shape[0]
    )
)


# In[37]:


address = '267 East Main St,01930'

geolocator = Nominatim(user_agent="n_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of The community are {}, {}.'.format(latitude, longitude))


# In[38]:


# create map of Massachusets using latitude and longitude values
map_mass = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'], neighborhoods['Museum'], neighborhoods['Community']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='red',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_mass)  
    
map_mass


# In[51]:


#map boston museums
boston_data = neighborhoods[neighborhoods['Museum'] == 'Boston'].reset_index(drop=True)
boston_data.head()


# In[52]:


address = '955 Boylston Street,02115'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Boston  955 Boylston Street are {}, {}.'.format(latitude, longitude))


# In[53]:


# create map of Boston using latitude and longitude values
map_boston = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(boston_data['Latitude'], boston_data['Longitude'], boston_data['Museum']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#c4e518',
        fill_opacity=0.7,
        parse_html=False).add_to(map_boston)  
    
map_boston


# In[41]:


CLIENT_ID = '1U5GBTL1KEHWHMMFH25BKFHGD1201XISMRZ04WGMXJQTZAQJ' # your Foursquare ID
CLIENT_SECRET = 'JLAJM1S3JCZUNSAKGOVE34IBSDRLKHWG25PX54QBNV30PS41' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[45]:


neighborhood_latitude = boston_data.loc['Latitude'] # neighbourhood latitude value
neighborhood_longitude = boston_data.loc['Longitude'] # neighbourhood longitude value

neighborhood_name = boston_data.loc[1, 'Museum'] # neighbourhood name

print('Latitude and longitude values of boston"{}" are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))


# In[46]:



boston_data.loc[0, 'Community']


# In[47]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[205]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[48]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
          # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)

