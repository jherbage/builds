# -*- coding: utf-8 -*-
import json
import boto3
import shutil
import urllib2
import bz2
from bz2 import decompress
import tarfile
import zipfile
import os
import base64
from urllib2 import urlopen, URLError, HTTPError
import pip
import subprocess
from os.path import expanduser

def dlfile(url):
  # Open the url
  try:
    f = urlopen(url)
    print "downloading " + url
    # Open our local file for writing
    with open(os.path.basename(url), "wb") as local_file: 
      local_file.write(f.read())

  #handle errors
  except HTTPError, e:
    print "HTTP Error:", e.code, url
  except URLError, e:
    print "URL Error:", e.reason, url

# read the required data from env.runtime.json
with open('/vagrant/env.json') as data_file:    
  data = json.load(data_file)

print "checking if role exists"
iam_client = boto3.client('iam')
roles=iam_client.list_roles()['Roles']
roleArn = None
if not any(x['RoleName'] == "newshound" for x in roles):
  print "creating role"
  roleArn = iam_client.create_role(
    RoleName="role/newshound",
    AssumeRolePolicyDocument='{ "Version": "2012-10-17", "Statement": [ { "Action": "sts:AssumeRole", "Effect": "Allow", "Principal": { "Service": "lambda.amazonaws.com" } } ] }'
  )['Arn']
  print "created role"  
else:
  roleArn=filter(lambda x:  x['RoleName'] == 'newshound', roles)[0]['Arn']
  
lambda_client = boto3.client('lambda')
functions = lambda_client.list_functions()['Functions']

# Zip the fucntion lib contents and encode them ready to upload
if not os.path.exists('lambda-function'):
  os.makedirs('lambda-function')
else:
  shutil.rmtree('lambda-function')
  os.makedirs('lambda-function')  
shutil.copy2('newshound.py', 'lambda-function/newshound.py')
shutil.copy2('env.json', 'lambda-function/env.json')
home=expanduser("~vagrant")
subprocess.call(['python', '-m', 'textblob.download_corpora'])
shutil.copytree(home+'/nltk_data', 'lambda-function/nltk_data')

if not os.path.isfile('phantomjs-1.9.8-linux-x86_64.tar.bz2'): 
  dlfile('https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2')

tar = tarfile.open("phantomjs-1.9.8-linux-x86_64.tar.bz2")
os.chdir('lambda-function')
tar.extractall()
tar.close()	
os.chdir('..')

#if not os.path.isfile('chromedriver_linux64.zip'): 
#  dlfile('https://chromedriver.storage.googleapis.com/2.28/chromedriver_linux64.zip')
#os.chdir('lambda-function')
#zip = zipfile.ZipFile("../chromedriver_linux64.zip", 'r')
#zip.extractall()
#zip.close()	
#os.chdir('..')

# Download selenium python lib into dir
pip.main(['install', '-t','./lambda-function', 'selenium'])
pip.main(['install', '-t','./lambda-function', 'textblob'])

# Zip the functions update
os.chdir('lambda-function')
zf = zipfile.ZipFile("../newshound.zip", "w")
for dirname, subdirs, files in os.walk("."):
    zf.write(dirname)
    for filename in files:
        zf.write(os.path.join(dirname, filename))
zf.close()
os.chdir('..')

# Would rather not do this but sending the zip file up directly to lambda seems to timeout.
# So instead load the zip file to an S3 bucket, use that to load the function, then trash the bucket
s3client = boto3.client('s3', region_name=data['aws_region'])
s3client.create_bucket(ACL='private', Bucket='newshound-s3', CreateBucketConfiguration={
    'LocationConstraint': data['aws_region']})

with open('newshound.zip', "rb") as file:
  s3client.upload_fileobj(file, 'newshound-s3', 'newshound.zip')

# check for existence of the function
print "checking if function exists"
if any(x['FunctionName'] == "newshound" for x in functions):
  print "deleting function"
  lambda_client.delete_function(FunctionName='newshound')
  print "function deleted"
print "creating newshound lambda function"
lambda_client.create_function(    
FunctionName='newshound',
  Runtime='python2.7',
  Role=roleArn,
  MemorySize=512,
  Handler='newshound.handler',
  Code={
        'S3Bucket': 'newshound-s3',
		'S3Key': 'newshound.zip'
  },
  Description='Scrapes the newsapi for stuff in the news and populates a database with the info returned',
  Timeout=300,
  #Publish=True
)
print "created lambda function"

s3client.delete_object(Bucket = 'newshound-s3', Key = 'newshound.zip')
s3client.delete_bucket(Bucket = 'newshound-s3')

dynamodb_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb', aws_secret_access_key = data['aws_secret_access_key'], aws_access_key_id=data['aws_access_key_id'], region_name=data['aws_region'])

# Clear the function_ran table for the function	
table = dynamodb.Table('function_ran')
for funcname in ['newshound']:
	table.delete_item(Key={'function': funcname})

  
