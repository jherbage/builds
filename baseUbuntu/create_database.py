# -*- coding: utf-8 -*-
import json
import boto3
import time


# read the required data from env.runtime.json
with open('/vagrant/env.json') as data_file:    
  data = json.load(data_file)
  
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')
tables = dynamodb_client.list_tables()['TableNames']
# check for existence of the tables
# if they dont exist create them
print "checking if tables exist"
if not 'function_ran' in tables:
  print "creating function_ran table"
  dynamodb_client.create_table(    AttributeDefinitions=[
        {
            'AttributeName': 'function',
            'AttributeType': 'S'
        },
    ],
    TableName='function_ran',
    KeySchema=[
        {
            'AttributeName': 'function',
            'KeyType': 'HASH'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
	)
if not 'locks' in tables:
  print "creating locks table"
  dynamodb_client.create_table(    AttributeDefinitions=[
        {
            'AttributeName': 'lock',
            'AttributeType': 'S'
        },
    ],
    TableName='locks',
    KeySchema=[
        {
            'AttributeName': 'lock',
            'KeyType': 'HASH'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
	)
if not 'run_history' in tables:
  print "creating run_history table"
  dynamodb_client.create_table(    AttributeDefinitions=[
        {
            'AttributeName': 'starttime',
            'AttributeType': 'S'
        }
    ],
    TableName='run_history',
    KeySchema=[
        {
            'AttributeName': 'starttime',
            'KeyType': 'HASH'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
	)
if not 'news_urls' in tables:
  print "creating news_urls table"
  dynamodb_client.create_table(    AttributeDefinitions=[
        {
            'AttributeName': 'url',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'country',
            'AttributeType': 'S'
        },
    ],
    TableName='news_urls',
    KeySchema=[
        {
            'AttributeName': 'url',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'country',
            'KeyType': 'RANGE'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
	)
if not 'news_items' in tables:
  print "creating news_items table"
  dynamodb_client.create_table(    AttributeDefinitions=[
        {
            'AttributeName': 'item',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'url',
            'AttributeType': 'S'
        },
    ],
    TableName='news_items',
    KeySchema=[
        {
            'AttributeName': 'item',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'url',
            'KeyType': 'RANGE'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
	)
# check the table creation is finished
# if they havent wait
status='unknown'
for tablename in ['news_urls', 'news_items', 'locks', 'function_ran']:
  while not status == 'ACTIVE':
    status=dynamodb_client.describe_table( TableName = tablename )['Table']['TableStatus']
    time.sleep(5)
  print "table "+tablename+" is now active"

