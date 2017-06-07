import json
from os.path import expanduser
with open('/vagrant/env.json') as data_file:    
  data = json.load(data_file)
awsSecret=data["aws_secret_access_key"]
awsAccess=data["aws_access_key_id"]
awsRegion=data["aws_region"]
f = open('/etc/boto.cfg', 'w')
f.write('[Credentials]\n')
f.write('aws_access_key_id = \n')
f.write('aws_secret_access_key = '+awsSecret+'\n')
f.write('[Boto]\n')
f.write('http_socket_timeout = 600\n')
f.write('ec2_region_name = '+awsRegion+'\n')
f.close()
