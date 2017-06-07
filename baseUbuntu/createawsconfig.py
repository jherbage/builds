import json
from os.path import expanduser
with open('/vagrant/env.json') as data_file:    
  data = json.load(data_file)
awsSecret=data["aws_secret_access_key"]
awsAccess=data["aws_access_key_id"]
awsRegion=data["aws_region"]
awsData=data["aws_data_type"]
home=expanduser("~vagrant")
f = open(home+'/.aws/credentials', 'w')
f.write('[default]\n')
f.write('aws_access_key_id = '+awsAccess+'\n')
f.write('aws_secret_access_key = '+awsSecret+'\n')
f.close()
f = open(home+'/.aws/config', 'w')
f.write('[default]\n')
f.write('region = '+awsRegion+'\n')
f.write('output = '+awsData+'\n')
f.write('[preview]\n')
f.write('cloudfront=true\n')
f.close()
f = open('/etc/boto.cfg', 'w')
#f.write('[Credentials]\n')
#f.write('aws_access_key_id = '+awsAccess+'\n')
#f.write('aws_secret_access_key = '+awsSecret+'\n')
f.write('[Boto]\n')
f.write('http_socket_timeout = 600\n')
f.close()
