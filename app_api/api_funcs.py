
from requests.exceptions import ConnectionError
import pandas as pd
import numpy as np
import s2sphere as s2
import requests
import json
import re
from ast import literal_eval
import datetime
from geopy.distance import vincenty
from geopy.geocoders import Nominatim
from shapely import geometry
from sklearn.linear_model import LinearRegression
from shapely.geometry import Point, LineString
import warnings
warnings.filterwarnings('ignore')

def safeEval(x):
    if type(x) == float:
        return x
    else:
        return eval(x)

def unpackLS(geometry):
    '''
    Unpacks a reformatted linestring from pipe delim to list of tuples
    with format (latitude, longtitude)
    '''
    if pd.isnull(geometry):
        return geometry
    coords = geometry.split('|')
    ls = [eval(i) for i in coords]
    linestring = LineString(ls)
    return linestring


def initDatasets():
    '''
    Cleans and initializes the necessary files, returns in the following order:
    streets, add_w_units, parking_census, ocu_prob, regulations
    '''
    streets = pd.read_csv('cleaned/streets.csv',index_col=0)
    streets['ls'] = streets.geometry.map(unpackLS)
    add_w_units = pd.read_csv('cleaned/add_w_units.csv',index_col=0)
    add_w_units['location'] = add_w_units.location.map(lambda x: eval(x))
    ocu_prob = pd.read_csv('cleaned/ocuprob.csv',index_col=0)
    regulations = pd.read_csv('cleaned/regulations.csv',index_col=0)
    regulations['ls'] = regulations.geometry.map(unpackLS)
    parking_census = pd.read_csv('cleaned/blockData.csv')
    parking_census['approx_location'] = parking_census.approx_location.map(lambda x: safeEval(x))
    meters = pd.read_csv('cleaned/meters.csv',index_col=0)
    meters['location'] = meters.location.map(safeEval)
    return streets, add_w_units, parking_census, ocu_prob, regulations, meters

streets, add_w_units, parking_census, ocu_prob, regulations, meters = initDatasets()

def safeEval(x):
    if type(x) == float:
        return x
    else:
        return eval(x)

def processCols(df):
    '''converts column names to lowercase and replaces speces with 
    underscores for convenient dot notation within pandas'''
    col_names = df.columns
    return [name.strip().lower().replace(' ','_') for name in col_names]

def processLat(tup):
    '''returns clean lat float value from a tuple stored as a string'''
    return float(tup.strip('()').replace(',','').split()[0])

def processLon(tup):
    '''returns clean lon float value from a tuple stored as a string'''
    return float(tup.strip('()').replace(',','').split()[1])

def parkingBlockcells(col):
    return list(swp_add[swp_add.cnn == col]['block_cell'].unique())

def reform_linestring(col):
    '''
    Takes a linestring formatted: LINESTRING (longitude latitude, longitude latitude) and returns a list of
    tuples where each tuple is formatted (latitude, longitude)
    '''
    if pd.isnull(col):
        return 
    else:
        tup = col.split(maxsplit=1)[1]
        coords = tup.split(',')
        formatted = []
        for c in coords:
            point = c.replace('(','').replace(')','').split()
            correct = float(point[1]),float(point[0])
            formatted.append(correct)
        return formatted


def reformLS(col):
    '''
    Takes a linestring formatted: LINESTRING (longitude latitude, longitude latitude) and returns a pipe
    delimited string of lat,long values
    '''
    if pd.isnull(col):
        return 
    else:
        tup = col.split(maxsplit=1)[1]
        coords = tup.split(',')
        formatted = []
        for c in coords:
            point = c.replace('(','').replace(')','').split()
            c1 = float(point[1])
            c2 = float(point[0])
            coord = (c1,c2)
            formatted.append(coord)
        return '|'.join([str(i) for i in formatted])


def unpackLS(geometry):
    '''
    Unpacks a reformatted linestring from pipe delim to list of tuples
    with format (latitude, longtitude)
    '''
    if pd.isnull(geometry):
        return geometry
    coords = geometry.split('|')
    ls = [eval(i) for i in coords]
    linestring = LineString(ls)
    return linestring

    
def sep_street(street_addy):
    if type(street_addy)==str:
        sa = street_addy.split(' ')
        if len(sa)>=1:
            return sa[0]

def cellIdtoLev(cell_id,lev):
    '''changes a cellId token into a specified level'''
    return cell_id.parent(lev)

def convertS2(lat, lng):
    '''converts a lat and lng point into a tuple, used when lat a lng are in seprate columns'''
    latlng = s2.LatLng.from_degrees(lat, lng)
    return s2.CellId.from_lat_lng(latlng)

def serializeS2(cell):
    return s2.CellId.to_token(cell)

def unserializeS2(token):
    return s2.CellId.from_token(token)

def reformDays(dayString):
    days = ['Mon','Tues','Wed','Thu','Fri','Sat','Sun','Holiday']
    if dayString == days[0]:
        return 0
    if dayString == days[1]:
        return 1
    if dayString == days[2]:
        return 2
    if dayString == days[3]:
        return 3
    if dayString == days[4]:
        return 4
    if dayString == days[5]:
        return 5
    if dayString == days[6]:
        return 6
    if dayString == days[7]:
        return 7

def reformHour(hour_string):
    return int(hour_string[:2])


def buildSched(w1, w2, w3, w4, w5):
    '''creates a pipe delimited schedule from the 5 week columns in the sweeper table'''
    schedlist = [w1,w2,w3,w4,w5]
    return '|'.join([str(y) for y, i  in enumerate(schedlist) if i == 'Y'])


def loadRateAdg(filename):
    '''takes a csv filename in the working dir and loads it must include following columns:
    ['Street & Block'] ['day type'] ['from time'] ['to time'] ['occupancy']'''
    df = pd.read_csv(filename)
    df.columns = processCols(df)
    df = df[['street_&_block','day_type', 'from_time','to_time','occupancy']]
    df.columns = ['street_block','day_type', 'from_time','to_time','occupancy']
    df['cnn'] = df.street_block.map(pilotProc)
    return df

def fixTime(n):
    if n == 'Open':
        return '09:00 AM'
    if n == 'Close':
        return'06:00 PM'
    if n == '3:00 PM':
        return '03:00 PM'
    else:
        return n
    
def timeband(fromTime):
    if fromTime == 9:
        return 0
    elif fromTime == 12:
        return 1
    elif fromTime == 15:
        return 2
    else:
        return 4
    
def pilotProc(col):
    '''Process the street_block column from the pilot meter adjustment programs into
    a CNN number for rapid joins with other tables'''
    l = col.split(' ')
    num = int(l[-1])
    street = ' '.join(l[:-1])
    nums = range(num, num+99)
    cnn = meters[(meters.streetname == street)
                     &(meters.street_num.isin(nums))]['cnn'].mode()
    if len(cnn)>0:
        return int(cnn.values[0])
    return 0


def S2_from_tuple(tup):
    '''converts a (lat,lng) tuple to a level 30 s2 cellId token'''
    lat = tup[0]
    lng = tup[1]
    latlng = s2.LatLng.from_degrees(lat, lng)
    return s2.CellId.from_lat_lng(latlng)



def s2CellToLat(cell_id):
    ll = cell_id.to_lat_lng()
    return ll.lat().degrees


def s2CellToLng(cell_id):
    ll = cell_id.to_lat_lng()
    return ll.lng().degrees
    


def findCnn(cellId, add_w_units=add_w_units):
    return add_w_units[add_w_units.block_cell == cellId]['cnn'].unique()


def findCnns(cellIds, add_w_units=add_w_units):
    return add_w_units[add_w_units.block_cell.isin(cellIds)]['cnn'].unique()


def findMeters(cellId, meters=meters):
    '''searches for meters via their block_cell s2 notation'''
    return meters[meters.block_cell.isin(cellId)]


def s2CellToLat(cell_id):
    ll = cell_id.to_lat_lng()
    return ll.lat().degrees


def s2CellToLng(cell_id):
    ll = cell_id.to_lat_lng()
    return ll.lng().degrees  


def respLocCentroid(location):
    '''Returns the centriod for the linestring returned from the sfpark api response
    formatting for the linestring is begin_lng, begin_lat, end_lng, end_lat '''
    coords = [float(x) for x in location.split(',')]
    if len(coords)==4:
        lat = (coords[1]+coords[3])/2
        lng = (coords[0]+coords[2])/2
        return (lat,lng)
    return [(coords[1],coords[0])]


def getTime():
    curtime = datetime.datetime.now()
    day = curtime.strftime('%A')
    hour = curtime.hour
    hour = 10
    band=1
    day_cat='Weekday'
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday']
    weekends = ['Saturday','Sunday']
    if day in weekdays:
        day_cat = 'Weekday'
    if day == 'Saturday':
        day_cat = 'Weekend'
    if day == 'Sunday':
        return 'Weekend',4
    b1 = range(9,12)
    b2 = range(12,15)
    b3 = range(15,18)
    b4 = list(range(18,24))+list(range(1,9))
    bands = [b1,b2,b3,b4]
    for i in bands:
        if hour in i:
            band = bands.index(i)
    return day_cat,band


def buildRequest(lat=None,long=None,radius=0.13,measurment='mile',parking_type=None,pricing='yes'):
    if lat:
        assert long != None
    if long:
        assert lat != None
    if radius:
        assert lat != None
        assert long != None
        assert measurment != None
    front = 'http://api.sfpark.org/sfpark/rest/availabilityservice' 
    tail = '&response=json'
    sep = '&'
    lati = 'lat='+str(lat)
    lngi = 'long='+str(long)
    rad = 'radius='+str(radius)
    uom = 'uom='+str(measurment)
    typ = 'type='+str(parking_type)
    pri = 'pricing='+str(pricing)
    if lat and long:
        llbase = front + '?' + lati + sep + lngi
        if radius and measurment:
            rmbase = llbase + sep + rad + sep + uom
            if parking_type:
                rmpr = rmbase + sep + typ
                if pricing:
                    return rmpr + sep + pri +tail
                return rmbase + tail
            if pricing:
                return rmbase + sep + pri + tail
            return rmbase + tail
        if parking_type:
            ptbase = llbase + sep + typ
            if pricing:
                return ptbase + sep + pri + tail
            return ptbase + tail
        if pricing:
            prbase = llbase + sep + pri
            return prbase + tail
        return llbase + tail
    if parking_type:
        ptbase = front + '?' + typ
        if pricing:
            return ptbase + sep + pri + tail
        return ptbase + tail
    if pricing:
        return front + '?' + pri + tail        
    return front + tail


def sendRequest(request):
    try:
        a = requests.get(request).json()
    except(ConnectionError,ConnectionRefusedError):
        a = {'NUM_RECORDS':0}
    return a



def processResp(response):
    '''creates a dataframe from an API response, reformats location to the centroid of the response linestring
    generates a level 16 s2 cell centered on that location'''
    recCount = int(response['NUM_RECORDS']) 
    if recCount > 0:
        dictdf = pd.DataFrame.from_dict(response['AVL'][:])
        dictdf.columns = processCols(dictdf)
        dictdf['loc_string'] = dictdf['loc']
        dictdf=dictdf.drop('loc',axis=1)
        dictdf['location'] = dictdf['loc_string'].map(respLocCentroid)
        dictdf['block_cell'] = dictdf.location.map(lambda x:S2_from_tuple(x).parent(16))
        dictdf['point_cell'] = dictdf.location.map(lambda x:S2_from_tuple(x))
        dictdf['cnn'] = dictdf.name.map(apiRespCnn)
        return dictdf
    else:
        return pd.DataFrame(columns=['bfid', 'name', 'pts', 'type', 
                                     'loc_string', 'location', 'block_cell',
                                     'point_cell', 'cnn'])



def apiRespCnn(col, meters=meters):
    l = col.strip().split(' ')
    num = literal_eval(l[-1].replace('-',','))
    c1 = list(l[0])[0]
    c2 = list(l[0])[1]
    if str.isnumeric(c1)&str.isalpha(c2):
        if int(c1)<=9:
            l[0] = '0'+l[0]
    street = str.upper(' '.join(l[:-1])).strip()
    nums = range(num[0],num[1])
    cnn = meters[(meters.streetname == street)
                     &(meters.street_num.isin(nums))]['cnn'].mode()
    if len(cnn)>0:
        return int(cnn.values[0])
    return 0 

def imputeAvailability(frame):
    '''uses linear regression to impute an availability probability 
    if there is enough ground truth in the nearby area to justify it'''
    threshold = len(frame[frame.availability_proba.isnull()==False])/len(frame.availability_proba)
    print("threshold: ", threshold)
    if threshold < .55:
        return (frame, 0)
    working_frame = frame #[['cnn','total_count','count_Grey','Grey_proba','availability_proba','block_length']]
    nulls = frame[(frame.total_count.isnull())&(frame.count_Grey.isnull())&(frame.Grey_proba.isnull())]
    working_frame_denull = working_frame.dropna(subset=['total_count','count_Grey','Grey_proba'])
    working_frame_train = working_frame_denull[working_frame_denull.availability_proba.notnull()]
    working_frame_fill = working_frame_denull[working_frame_denull.availability_proba.isnull()]
    X = working_frame_train[['total_count','count_Grey','block_length']]
    y = working_frame_train['availability_proba']
    mod = LinearRegression()
    fit = mod.fit(X,y)
    working_frame_fill['availability_proba'] = fit.predict(working_frame_fill[['total_count','count_Grey','block_length']])
    imputed = pd.concat([working_frame_train,working_frame_fill,nulls])
    return (imputed , 1)

def meterTypeTransform(cap_color='Grey', meter=None):
    '''Takes in a data frame of meters for a search area and transforms it into a dataframe of
    cnn, 
    total_count = total meters of all color on that cnn, 
    count_(cap_color)= sum of the color of interest passed
    (cap_color)_proba = probability of meter in cnn being color of interest
    '''
    t = meter.groupby(['cnn','cap_color'])['post_id'].count().reset_index()
    s = t.groupby('cnn')['post_id'].sum().reset_index()
    g = t[t.cap_color==cap_color]
    g = g.drop('cap_color',axis=1)
    g.columns = ['cnn', 'count_{}'.format(cap_color)]
    s.columns = ['cnn','total_count']
    met = pd.merge(s,g,on='cnn',how='left').fillna(0)
    met['{}_proba'.format(cap_color)] = met.iloc[:,2]/met.iloc[:,1]
    return met

def formatInputAddress(address):
    up = address.upper()
    rep = up.replace("STREET","ST").replace("AVENUE", "AVE").replace("DRIVE","DR")
    fixed = rep.split(' ')
    num = ['1ST','2ND','3RD','4TH','5TH','6TH','7TH','8TH','9TH']
    if fixed[1] in num:
        fixed[1]= '0'+fixed[1]
        rep = ' '.join(fixed)
    return rep


def getAddress9x9(address, add_w_units=add_w_units):
    addy = formatInputAddress(address)
    addy_series = add_w_units[add_w_units.address == addy].block_cell
    if len(addy_series)>=1:
        cell = s2.CellId.from_token(addy_series.values[0])
        lev = cell.level()
        neighbors = [serializeS2(item) for item in list(cell.get_all_neighbors(lev))]
        return serializeS2(cell),neighbors
    else: 
        incr = 2
        while len(addy_series)< 1:
            parts = addy.split(' ')
            num = int(parts[0])+incr
            street = ' '.join(parts[1:])
            inc_addy = str(num) +' '+ street
            addy_series = add_w_units[add_w_units.address == inc_addy].block_cell
            incr += 2
            if incr > 150:
                print('Your address appears to be invalid')
# TODO Error handeling needed here
                
                break
                return None,None
        if len(addy_series)>0:
            cell = s2.CellId.from_token(addy_series.values[0])
            print('Address not found, showing: {}'.format(inc_addy))
            lev = cell.level()
            neighbors = [serializeS2(item) for item in list(cell.get_all_neighbors(lev))]
            return serializeS2(cell),neighbors

def scoreBlock(distance, supply):
    return supply/(distance)**2


def getParkingExp(address):
    '''Frame feeds from parking_census,
        ap feeds from sfPark API, 
        meter feeds from meters
        ocu feeds from ocu_prob 
        locs feeds from '''
    # get a list of s2 cells which include the cnn in question
    addy,neighbors = getAddress9x9(address)
    #will always be neighbors
    if neighbors:
        cnn = findCnns(neighbors)
#         print(cnn)
        mets = findMeters(neighbors)
    if not neighbors:
        cnn = findCnn(addy)
        mets = findMeters(addy)
    # convert address cell to s2 cell id object and pull lat/lng from that 
#     this is a level 16 cell, and thus is inaccurate,   implement a geocoder here instead
    addy_cell = unserializeS2(addy)
    lat = s2CellToLat(addy_cell)
    lng = s2CellToLng(addy_cell)
    dest = (lat,lng)
#     end geocoder implement 
#   this is unnecessary and is ultimately probably not worth the time
    req = sendRequest(buildRequest(lat=lat,long=lng, parking_type='on',pricing='no'))
    ap = processResp(req)

#   this finds parking census data for the list of cnn's
    fr =parking_census[parking_census.cnn.isin(cnn)]
#     fr = meter_census[meter_census.cnn.isin(cnn)]
#     filterMeter = (list(cnn),'Grey')
#     changed this to filter a pre-computed multiindex table called meter_proba
#     met = meter_proba.loc[filterMeter,['meter_proba','color_count','total_count']].reset_index()
                           
#     met = meterTypeTransform(cap_color='Grey',meter=mets)

#     now we have meters and census data, and sfpark data (in theory)
# merge census data and sfPark data, with the api down this does nothing but add NAN cols
    fr_df_met = pd.merge(fr,ap,on='cnn',how='left')
    day_cat,band = getTime()
#     retreive values from ocu_prob corresponding to the day and time
    ocu = ocu_prob[(ocu_prob.day_type==day_cat)&(ocu_prob.band==band)]
#     merge ocu_prob search results 
    fr_df_met_ocu_locs = pd.merge(fr_df_met,ocu,on='cnn',how='left')
    
# can get rid of below with a merg of approx location into meter_census
#     fr_df_met_ocu_locs = pd.merge(fr_df_met_ocu,cnn_location, on='cnn', how='left')

    working_frame = fr_df_met_ocu_locs[['cnn','street',#'block_cell_x', 
                                        'bfid','location','approx_location', 'prkng_sply',
       'total_count', 'color_count', 'meter_proba','day_type','availability_proba','block_length']]

    working_frame['relative_distance_dest']= working_frame.approx_location.map(lambda x: vincenty((lat,lng), x).meters)
    imputed, ind = imputeAvailability(working_frame)

    if ind == 1:
        imputed['availability'] = imputed.apply(lambda row: row.availability_proba*row.meter_proba*row.color_count,axis=1) 
        imputed['score']=imputed.apply(lambda row: scoreBlock(row.relative_distance_dest, row.availability),axis=1)
        imp = imputed[['cnn','street','approx_location','relative_distance_dest','availability','score']]
        imp = imp[imp.cnn.duplicated() == False]
        return imp[imp.score.isin(heapq.nlargest(4,imp.score))].sort_values('score',ascending=False), dest 
    else:
        imputed['availability'] = imputed.apply(lambda row: row.prkng_sply*.1,axis=1)
        imputed['score']=imputed.apply(lambda row: scoreBlock(row.relative_distance_dest, row.availability),axis=1)
        imp = imputed[['cnn','street','approx_location','relative_distance_dest','availability','score']]
        imp = imp[imp.cnn.duplicated() == False] 
        return imp[imp.score.isin(imp.score.nlargest(4))].sort_values('score',ascending=False), dest



def parkGoog(origin,address):
    geolocator = Nominatim()
    search_o = origin+' San Francisco'
    loc_o = geolocator.geocode(search_o)
    org = (loc_o.latitude,loc_o.longitude)
    search_a = address + ' San Francisco'
    loc_a = geolocator.geocode(search_a)
    desti = (loc_a.latitude,loc_a.longitude)
    topFour, dest = getParkingExp(address)
    blocks = list(topFour.approx_location)
    src = "none"
    return org, desti, blocks, src   

