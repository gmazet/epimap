# -*- coding: utf-8 -*-

import sys

try:
    evtlat=float(sys.argv[1])
    evtlon=float(sys.argv[2])
    evtname=sys.argv[3]
    distmax=float(sys.argv[4]) #emprise en km
    zoomlevel=int(sys.argv[5]) #9, 10 or 11
except:
    print("Missing arguments")
    exit()

import pandas as pd
import datetime
import math

import matplotlib.pyplot as plt

import cartopy
import cartopy.crs as ccrs
from cartopy.io.img_tiles import *
import cartopy.feature as cfeature
from cartopy.io import shapereader
#from owslib.wmts import WebMapTileService
from cartopy.geodesic import Geodesic
import shapely

from matplotlib import patheffects
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
# -------------------------------
stafile="./stations.txt"


# Exemple
# distmax, zoomlevel = 15 , 11
# distmax, zoomlevel = 30 , 10
# distmax, zoomlevel = 50 , 9
# distmax, zoomlevel = 100 , 8

if (distmax>50):
    circles=range(20,120,20) # km
    circlestep=20
else:
    circles=range(10,60,10) # km
    circlestep=10
# -------------------------------

maintitle="%s" % (evtname)

deg2km=111.19
km2deg=1.0/deg2km
distdeg=distmax*km2deg

latmin,latmax=evtlat-distdeg,evtlat+distdeg
#lonmin,lonmax=evtlon+distdeg,evtlon-distdeg
lonmin,lonmax=evtlon-distdeg/math.cos(evtlat/180.0*math.pi),evtlon+distdeg/math.cos(evtlat/180.0*math.pi)

print ("----------------------------------------------")
print ("lat/lon, min/max:",latmin,latmax,lonmin,lonmax)
print ("zoomlevel=",zoomlevel)
print ("dist max=",distmax)
print ("")

# -----------------------------------------
# Differents fonds de cartes possibles
# -----------------------------------------
#tiler = Stamen('terrain-background')
#tiler = QuadtreeTiles() # TEST
tiler = Stamen('terrain')
#tiler = OSM() # TEST
#tiler = GoogleTiles(style='street') 
#exit()


PC=ccrs.PlateCarree()
MERC=ccrs.Mercator()

bigmap=MERC
smallmap=MERC

# -----------------------------

#BORDERS2_10m = cartopy.feature.NaturalEarthFeature('cultural', 'admin_1_states_provinces_lines', '10m', edgecolor='black', facecolor='none')
BORDERS2_110m = cartopy.feature.NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land', '110m', edgecolor='black', facecolor='none')
#country boundaries.
#LAND_10m = cartopy.feature.NaturalEarthFeature('physical', 'land', '10m', edgecolor='face', facecolor=cartopy.feature.COLORS['land'])
#land polygons, including major islands.
#RIVERS_10m = cartopy.feature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m', edgecolor=cartopy.feature.COLORS['water'], facecolor='none')
####ROADS_10m = shapereader.natural_earth(category='cultural', name='roads', resolution='10m')
#ROADS_10m = cartopy.feature.NaturalEarthFeature('cultural', 'roads', '10m')

# For legends
# handles is a list of patch handles
# names is the list of corresponding labels to appear in the legend
handles = []
names = []

#fig = plt.figure(figsize=(8,5))
fig = plt.figure()

# ------------------------------- Surrounding frame ------------------------------
# set up frame full height, full width of figure, this must be called first
left = -0.05
bottom = -0.05
width = 1.1
height = 1.05
rect = [left,bottom,width,height]
ax3 = plt.axes(rect)

# turn on the spines we want, ie just the surrounding frame
ax3.axis('off')
ax3.set_visible(False)
ax3.spines['right'].set_visible(True)
ax3.spines['top'].set_visible(True)
ax3.spines['bottom'].set_visible(True)
ax3.spines['left'].set_visible(True)

#ax3.text(0.01,0.01,'© Don Cameron, 2017: net-analysis.com. '+ 'Map generated at '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fontsize=8)
# ---------------------------------  Main Map -------------------------------------
#
# set up main map almost full height (allow room for title), right 80% of figure
left = 0.28
bottom = 0.05
width = 0.65
height = 0.85
rect = [left,bottom,width,height]

ax = plt.axes(rect, projection=MERC)
#print (ax)
ax.set_extent((lonmin, lonmax, latmin, latmax), crs=PC)

gl=ax.gridlines(draw_labels=True, linewidth=0.6, color='lightgrey', zorder=2)
gl.xlabel_style = {'size': 8, 'color': 'grey'}
gl.ylabel_style = {'size': 8, 'color': 'grey'}


#land polygons, including major islands, use cartopy default color
ax.add_image(tiler, zoomlevel, interpolation='spline36', regrid_shape=2000, zorder=1)
###ax.coastlines(resolution='10m', zorder=2)
###ax.add_feature(RIVERS_10m)
###ax.add_feature(LAND_10m)
###ax.stock_img()
###ax.add_feature(RIVERS_10m)
###ax.add_feature(BORDERS2_10m, edgecolor='grey')


# ---------------------------
# Plot LDG stations
# ---------------------------
dfsta=pd.read_csv(stafile, delimiter="|", header=0)
#print (dfsta)

h2=ax.scatter([x for x in dfsta.Longitude], [y for y in dfsta.Latitude], transform=PC, s=40, c='brown', marker="^", label='Stations sismiques', zorder=4)
handles.append(h2)
names.append('Stations')
for i in range(0,len(dfsta.Latitude)):
    if ( (dfsta.Longitude[i]>lonmax) | (dfsta.Longitude[i]<lonmin) | (dfsta.Latitude[i]>latmax) | (dfsta.Latitude[i]<latmin) ):
        continue
    print ("Plot station:",i, dfsta.Longitude[i], dfsta.Latitude[i], dfsta.Station[i])
    ax.text(dfsta.Longitude[i], dfsta.Latitude[i], dfsta.Station[i] , transform=PC, horizontalalignment='left', verticalalignment='bottom', fontsize=7, zorder=5)

#single-line drainages, including lake centerlines.
lon0, lon1, lat0, lat1 = ax.get_extent()
print (lon0)

# bar offset is how far from bottom left corner scale bar is (x,y) and how far up is scale bar text
bar_offset = [0.05, 0.05, 0.07]
bar_lon0 = lon0 + (lon1-lon0)*bar_offset[0]
bar_lat0 = lat0 + (lat1-lat0)*bar_offset[1]

text_lon0 = bar_lon0
text_lat0 = lat0 + (lat1-lat0)*bar_offset[2]
bar_tickmark = 20000 # metres
bar_ticks = 5
bar_alpha = 0.3

bar_color = ['black', 'red']

n_points=200
for r in circles:
    r=r*1000.0 # convert it into meters
    circle_points=Geodesic().circle(lon=evtlon, lat=evtlat, radius=r, n_samples=n_points, endpoint=False)
    geom = shapely.geometry.Polygon(circle_points)
    ax.add_geometries((geom,), crs=PC, facecolor='none', edgecolor='k', linewidth=0.5, alpha=0.5, ls='-', zorder=3)
    #if (r==10000):
    if (r==circles[0]*1000): # legend for the first circle
        axtext= "%d km"%circlestep
        dlat=float(circles[0])/110.0
        ax.text(evtlon, evtlat-dlat, axtext, transform=PC, horizontalalignment='center', verticalalignment='bottom', fontsize=7, color='k',)

h4=ax.scatter(evtlon,evtlat, transform=PC, s=40, c='k', marker="*", label='Epicentre', zorder=5)
handles.append(h4)
names.append('Epicentre')


# ---------------------------------Locating Map ------------------------
#
# set up index map 20% height, left 16% of figure
left = 0
bottom = 0.05
width = 0.20
height = 0.25
rect = [left,bottom,width,height]

ax2 = plt.axes(rect, projection=smallmap)
ax2.set_extent((41.0, 53.0, -11.0, -27.0))
#  ax2.set_global()  will show the whole world as context

ax2.coastlines(resolution='110m', zorder=2)
###ax2.add_feature(cfeature.LAND)
ax2.add_feature(BORDERS2_110m, edgecolor='grey')
###ax2.add_feature(cfeature.OCEAN)

ax2.gridlines()


lon0,lon1,lat0,lat1 = ax.get_extent()
box_x = [lon0, lon1, lon1, lon0, lon0]
box_y = [lat0, lat0, lat1, lat1, lat0]

#plt.plot(box_x, box_y, color='red',  transform=ccrs.Geodetic())
plt.plot(box_x, box_y, color='red',  transform=bigmap)
# -------------------------------- Title -----------------------------
# set up map title top 4% of figure, right 80% of figure
left = 0.2
bottom = 0.95
width = 0.8
height = 0.04
rect = [left,bottom,width,height]
ax6 = plt.axes(rect)
ax6.text(0.5, 0.0,maintitle, ha='center', fontsize=11)
ax6.axis('off')
# ---------------------------------North Arrow  ----------------------------
#
left = 0
bottom = 0.4
width = 0.16
height = 0.2
rect = [left,bottom,width,height]
rect = [left,bottom,width,height]
ax4 = plt.axes(rect)

# need a font that support enough Unicode to draw up arrow. need space after Unicode to allow wide char to be drawm?
ax4.text(0.5, 0.0,u'\u25B2 \nN ', ha='center', fontsize=15, family='Arial', rotation = 0)
ax4.axis('off')
# ------------------------------------  Legend -------------------------------------

# legends can be quite long, so set near top of map (0.4 - bottom + 0.5 height = 0.9 - near top)
left = 0.05
bottom = 0.6
width = 0.16
height = 0.3
rect = [left,bottom,width,height]
ax5 = plt.axes(rect)
ax5.axis('off')

# create legend
ax5.legend(handles, names, fontsize=8, loc='best')

#plt.show()
png="map.png"
print ("Save figure in %s"%png)
plt.savefig(png, dpi=120)
exit()

#ax5.set_title('Legend',loc='left')

