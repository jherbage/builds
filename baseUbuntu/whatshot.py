# -*- coding: utf-8 -*-
from textblob import TextBlob
import urllib2
import json
import re
import boto3
import time
import datetime
import os

def isNotInt(s):
    try: 
        int(s)
        return False
    except ValueError:
        return True
		
def convertTimePeriodToEarliestTime(timeperiod):
	# Get now minus the timeperiod as epoch
	if not timeperiod or timeperiod.rstrip().lstrip() == "":
	  timeperiod='24 hours'
	# format OK?
	timeperiodArr = timeperiod.split()
	if len(timeperiodArr) != 2 or timeperiodArr[1].lower() not in ["hours", "minutes", "days"] or isNotInt(timeperiodArr[0]):
	  # invalid format
	  print "invalid format for TIMEPERIOD "+timeperiod+ " therefore using 24 hours"
	  timeperiod='24 hours'
	  timeperiodArr = timeperiod.split()
 
	if timeperiodArr[1] == 'hours':
		earliest = datetime.datetime.now() - datetime.timedelta(hours=int(timeperiodArr[0]))
	elif timeperiodArr[1] == 'minutes':
		earliest = datetime.datetime.now() - datetime.timedelta(minutes=int(timeperiodArr[0]))	
	elif timeperiodArr[1] == 'days':
		earliest = datetime.datetime.now() - datetime.timedelta(days=int(timeperiodArr[0]))	
		
	return int(earliest.strftime("%s"))
	
def handler(event, context):
	
	# read the required data from env.runtime.json
	with open('env.json') as data_file:    
	  data = json.load(data_file)

	# data is in the database
	client = boto3.client('dynamodb')
	request_history_table = dynamodb.Table('request_history')
	
	starttime = time.strftime("%Y-%m-%d %H:%M:%S")
	request_history_table.put_item(Item={ 'starttime': starttime })
	
	# what is the request TYPE - defaults to LIST
	# Types - LIST - shows me a list a things in news in past 24 hours
	# User TIMEPERIOD to limit the timeframe - defaults to 24 hours - can specify as N hours, days, minutes
	TYPE='list'
	TIMEPERIOD='24 hours'
	if event['TYPE']:
		TYPE=event['TYPE']	
	if event['TIMEPERIOD']:
		TIMEPERIOD=event['TIMEPERIOD']	
		
	
	# We need to exit whatever happens so wrap in try
	try:
		news_items = dynamodb.Table('news_items')
		# Find the items in table that match datetime
		response = news_items.scan( Key={'item': thing, 'url': article['url']})

	except Exception as e:
		print "EXCEPTION: "+str(e)
	finally:
		lock_table.delete_item( Key={'lock': 'newshound'})
		run_history_table.update_item( Key={ 'starttime': starttime},
			UpdateExpression="set endtime = :x",
			ExpressionAttributeValues={ ':x': time.strftime("%Y-%m-%d %H:%M:%S") })
			
handler(None, None)