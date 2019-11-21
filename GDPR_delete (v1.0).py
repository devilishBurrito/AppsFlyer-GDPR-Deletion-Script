#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
from tqdm import tqdm
from datetime import *
import uuid
import warnings
from math import isnan
import time


## throttling based on AF's 80 request per 2 minute rule
def throttle(tm):
    i = 0
    while i < tm:
        print ("PAUSED FOR THROTTLING!" + "\n" + str(delay-i) + " minutes remaining")
        time.sleep(60)
        i = i + 1
    return 0

## function for reformating the dates
def date():
    dt = datetime.utcnow()  # # <-- get time in UTC
    dt = dt.isoformat('T') + 'Z'
    tz = dt.split('.')
    tz = tz[0] + 'Z'
    return str(tz)

def requestDeletion(mplatform, mdevice_id, mtime, muuid, app, token, endpoint, mdf, position):   
    identity_type = ''
    if mplatform.lower() == 'android':
        mdevice_id = mdevice_id.lower()
        identity_type = 'android_advertising_id'
    elif mplatform.lower() == 'ios':
        mdevice_id = mdevice_id.upper()
        identity_type = 'ios_advertising_id'
    else:
        return

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    params = {'api_token': token }
 
    body = {
        'subject_request_id': muuid,
        'subject_request_type': 'erasure',
        'submitted_time': mtime,
        "subject_identities": [
            { "identity_type": identity_type, 
               "identity_value": mdevice_id, 
               "identity_format": "raw" }
            ], 
        "property_id": app
        }

    body = json.dumps(body)


    endpoint = 'https://hq1.appsflyer.com/gdpr/opengdpr_requests'

    res = requests.request('POST', endpoint, headers=headers,
                           data=body, params=params)

    if res:
        #checks if the response was within 200-400 range
        mdf['subject_request_id'][position] = muuid
    else: 
        mdf['subject_request_id'][position] = ''
        mdf['error status'][position] = (str(res.status_code) + ': ' + res.text)

    global logs_enabled
    if logs_enabled:
        # printing in case we need to check things
        print(mplatform.upper() + ' status: ' + str(res.status_code) + '\nresponse: ' + res.text + '\nendpoint: ' + res.url + '\n')

## main run function. Determines whether it is iOS or Android request and sends if not LAT-user
def run(output, mdf, throt_rate, throt_delay):
    global is_test
    global app_id
    global api_key

    print ('Sending requests! Stand by...')
    platform = mdf.platform
    device = mdf.device_id

    if is_test == True:
        app_id = mdf.app_id
        token = api_key
        endpoint = 'https://hq1.appsflyer.com/gdpr/stub'
    else:
        app_id = mdf.app_id
        token = api_key
        endpoint = 'https://hq1.appsflyer.com/gdpr/opengdpr_requests'
    
    for position in tqdm(range(len(device))):

        if position % throt_rate == 0 and position != 0: 
            throttle(throt_delay)

        # else:
        req_id = str(uuid.uuid4())
        timestamp = str(date())
        validate = str(device[position])
        if validate == '' or validate == 'nan':
            mdf['subject_request_id'][position] = ''
            mdf['error status'][position] = 'Limit Ad Tracking Users Unsupported. Device ID Required'  
        else:
            requestDeletion(str(platform[position]), str(device[position]), timestamp, req_id, app_id[position], token, endpoint, mdf, position)
    
             ## write to CSV DURING the loop. Doing  t the end was bad idea.
             ## Too many possibilites and lost logs / request IDs
        mdf.to_csv(output, sep=',', index = False, header=True)
    
    print ('\nDONE. Please see ' + output 
        + ' for the subject_request_id and/or error messages\n')

## just used to create the renamed file with _LOGS.csv
def addLogExt(nm):
    nm = stripExtension(nm) + '_LOGS.csv'
    return nm

## adds relevant columns to the log file
def logs_csv(out, df):
    df['subject_request_id'] = ''
    df['error status'] = ''
    df['device_id'].fillna('')
    df.to_csv(out, sep=',', index=None, header=True)

    return df

## solely for reading in the file name from the user. creates string out of filename
## due to current limitations, this file MUST be located with the python script. 
## moving forward will add file finder so user can type file path or drag and drop file into terminal
def stripExtension(fn):
    fn = fn.split('.')
    fn = fn[0]
    return str(fn)

def readin_name():
    mprefix = input('FILE NAME (CSV ONLY): ')
    mprefix = stripExtension(mprefix)
    mname = str(mprefix + '.csv')
    print ('Reading in file: ' + mname)
    return mname

def validateToken(key):
    key = key.strip()
    if len(key) != 36:
        print('\ninvalid API Key format, please try again.')
        return False
    return True


def start():
    print ('\nWelcome to GDPR STREAMLINE')
    global api_key
    api_key = input('Please provide your API key: ')
    while validateToken(api_key) == False:
        api_key = input(' API key : ')
        validateToken(api_key)
    # # blue = OpenFile()

    global throttle_rate
    global throttle_delay

    testing = input('Is this a test? (y/n) : ')
    if testing == "y":
      global is_test 
      is_test = True
      print('\nGreat! We\'ll use the StubAPI endpoint (testing endoint')
      debugging = input('\nDebug mode (logging) enabled? (y/n) : ')
      throttle_delay = 1 # minutes
      if debugging == 'y':
        global logs_enabled
        logs_enabled = True

    # return a CSV
    name = readin_name()
    import_csv = pd.read_csv(name)
    output_name = addLogExt(name)

    output_file = logs_csv(output_name, import_csv)

    run(output_name, output_file, throttle_rate, throttle_delay)


## to disable all warnings in console logs

warnings.filterwarnings('ignore')
is_test = False
logs_enabled = False
api_key = ''
# OpenGDPR has a throttle mechanism in which only 80 requests can be sent every 3 minutes.
throttle_delay = 3 # minutes
throttle_rate = 80 # requests per throttle_delay
start()

# REQUESTED ASSISTANCE:
# https://stackoverflow.com/questions/54082240/nested-json-values-cause-typeerror-object-of-type-int64-is-not-json-serializ