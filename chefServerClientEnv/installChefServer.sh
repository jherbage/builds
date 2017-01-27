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

# ensure the time is up to date
echo "Synchronizing time..."
apt-get -y install ntp
service ntp stop
ntpdate -s time.nist.gov
service ntp start

# download the Chef server package
echo "Downloading the Chef server package..."
if [ ! -f /downloads/chef-server-core_12.11.1_amd64.deb ]; then
  wget -nv -P /downloads https://packages.chef.io/files/stable/chef-server/12.11.1/ubuntu/14.04/chef-server-core_12.11.1-1_amd64.deb
fi

# install the package
echo "Installing Chef server..."
sudo dpkg -i /downloads/chef-server-core_12.11.1-1_amd64.deb

# reconfigure and restart services
echo "Reconfiguring Chef server..."
sudo chef-server-ctl reconfigure
echo "Restarting Chef server..."
sudo chef-server-ctl restart

# wait for services to be fully available
echo "Waiting for services..."
until (curl -D - http://localhost:8000/_status) | grep "200 OK"; do sleep 15s; done
while (curl http://localhost:8000/_status) | grep "fail"; do sleep 15s; done

# create admin user
echo "Creating a user and organization..."
sudo chef-server-ctl user-create admin Jason Admin admin@bclaritytesting.com insecurepassword --filename admin.pem
sudo chef-server-ctl org-create bclaritytesting "Business Clarity Ltd" --association_user admin --filename bclarity-validator.pem

# copy admin RSA private key to share
echo "Copying admin key to /vagrant/secrets..."
mkdir -p /vagrant/secrets
cp -f /home/vagrant/admin.pem /vagrant/secrets

echo "Your Chef server is ready!"


