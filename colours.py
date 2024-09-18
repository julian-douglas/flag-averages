from PIL import Image
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pycountry


df = pd.read_csv('states.csv')
states = df['State_Code']

def average_colour(image_path):
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img_array = np.array(img)
        avg_color = img_array.mean(axis=(0, 1))
        avg_color = avg_color.astype(int)
        avg_color_hex = '#{:02x}{:02x}{:02x}'.format(avg_color[0], avg_color[1], avg_color[2])
        return avg_color_hex
    
mean_colours = {}
for state in states:
    image_path = f'flags/{state.lower()}.png'
    avg_colour = average_colour(image_path)
    mean_colours[state] = avg_colour

df = pd.DataFrame(list(mean_colours.items()), columns=['State_Code', 'Colour'])

states = gpd.read_file('States_shapefile.shp')
if states.crs != 'EPSG:4326':
    states = states.to_crs(epsg=4326)

states = states.merge(df, left_on='State_Code', right_on='State_Code')

fig, ax = plt.subplots(figsize=(12, 8))
states.plot(ax=ax, color=states['Colour'], edgecolor='black')

plt.savefig('American_flags.png')

def iso_a3_to_a2(iso_a3_code):
    try:
        country = pycountry.countries.get(alpha_3=iso_a3_code)
        return country.alpha_2
    except KeyError:
        return None


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'XKX'
world = world[world['name'] != 'N. Cyprus']
world = world[world['name'] != 'Somaliland']
world = world[world['name'] != 'Kosovo']


world['iso_a2'] = world['iso_a3'].apply(iso_a3_to_a2)

mean_colours = {}
for country in world['iso_a2']:
    image_path = f'country_flags/{country.lower()}.png'
    avg_colour = average_colour(image_path)
    mean_colours[country] = avg_colour

df = pd.DataFrame(list(mean_colours.items()), columns=['Country_Code', 'Colour'])

world = world.merge(df, left_on='iso_a2', right_on='Country_Code')

fig, ax = plt.subplots(figsize=(12, 8))
world.plot(ax=ax, color=world['Colour'], edgecolor='black')

world.to_csv('world.csv', index=False)
plt.savefig('World_flags.png')
plt.show()