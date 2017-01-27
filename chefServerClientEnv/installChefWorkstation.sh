#!/usr/bin/env bash
#
# Copyright 2013 Rackspace US, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apt-get update
apt-get -y install curl
apt-get -y install git

# ensure the time is up to date
echo "Synchronizing time..."
apt-get -y install ntp
service ntp stop
ntpdate -s time.nist.gov
service ntp start

# download the Chef server package
echo "Downloading the Chef server package..."
if [ ! -f /downloads/chefdk_1.1.16-1_amd64.deb ]; then
  wget -nv -P /downloads https://packages.chef.io/files/stable/chefdk/1.1.16/ubuntu/14.04/chefdk_1.1.16-1_amd64.deb
fi

if [ `dpkg -l chefdk | grep 1.1.16| wc -l` == "0" ]; then
  echo "Installing Chef DK..."
  sudo dpkg -i /downloads/chefdk_1.1.16-1_amd64.deb
fi 

if [ ! -d /home/vagrant/learn-chef ]; then
  mkdir /home/vagrant/learn-chef
fi
if [ ! -d /home/vagrant/learn-chef/.chef ]; then
  mkdir /home/vagrant/learn-chef/.chef
fi
chown -R vagrant /home/vagrant/learn-chef
cd /home/vagrant/learn-chef/.chef
cat << KNIFE > knife.rb
current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "admin"
client_key               "#{current_dir}/admin.pem"
chef_server_url          "https://chefsrv.test/organizations/bclaritytesting"
cookbook_path            ["/home/vagrant/learn-chef/.chef/cookbooks/chef-cookbooks"]
KNIFE

cp -p /vagrant/secrets/admin.pem ./.



knife ssl fetch
output=`knife ssl check`
echo $output | grep "Successfully"
if [ "$?" != "0" ]; then
  echo "SSL certificates problem. Chef client configuration issue!"
else
  echo "Your Chef workstation is ready!"
fi

if [ ! -d /home/vagrant/learn-chef/.chef/cookbooks ]; then
#  cd ..
#  git clone https://github.com/learn-chef/learn_chef_apache2.git
#   make a change to the recipe before uploading
  
  cd /home/vagrant/learn-chef/.chef
  mkdir cookbooks
  cd cookbooks
  git init
  git config --global user.email "jasonherbage@googlemail.com"
  git config --global user.name "jherbage"
  git clone https://github.com/jherbage/chef-cookbooks
  
  for f in *; do
    if [ -d ${f} ]; then
        # Will not run if no directories are available
        knife cookbook upload $f
    fi
  done

fi

