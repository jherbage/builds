# -*- coding: utf-8 -*-
import json
import boto3
import time


# read the required data from env.runtime.json
with open('/vagrant/env.json') as data_file:    
  data = json.load(data_file)

# delete the event calling the lambda
events_client = boto3.client('events')
rules=events_client.list_rules()['Rules']
if any(x['Name'] == "newshound" for x in rules):
  targets=events_client.list_targets_by_rule( Rule='newshound')['Targets']
  if len(targets) > 0: 
    events_client.remove_targets(
	  Rule = 'newshound',
	  Ids=['newshound']
	)
  events_client.delete_rule(
    Name="newshound",
  )
  print "deleted rule"  
  
# delete the lambda function
lambda_client = boto3.client('lambda')
functions = lambda_client.list_functions()['Functions']
if any(x['FunctionName'] == "newshound" for x in functions):
  print "deleting newshound"
  lambda_client.delete_function(    
    FunctionName='newshound',
  )

# delete the role
iam_client = boto3.client('iam')
roles=iam_client.list_roles()['Roles']
if 'newshound' in roles:
  print "deleting role"
  iam_client.delete_role(
    RoleName="newshound"
  )
  print "deleted role" 
  
# delete the database
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

tables = dynamodb_client.list_tables()['TableNames']
for tablename in ['news_urls', 'news_items', 'locks', 'run_history','function_ran']:
  if tablename in tables:
    dynamodb.Table(tablename).delete()
    while any(x == tablename for x in dynamodb_client.list_tables()['TableNames']):
      time.sleep(5)
    print "Database table "+tablename+" has been deleted"
print "All tables have been deleted"  