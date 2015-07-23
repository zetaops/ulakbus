**DEVELOPMENT ENVIRONMENT SETUP**
=============================

First update and upgrade base system

``` bash
apt-get update
apt-get upgrade
```

Change file size limit to 65536 for Riak.
To set `ulimit -n` value permanently :

```sudo vi /etc/security/limits.conf```

and add these lines EOF
```bash
* soft nofile 65536
* hard nofile 65536
```

Install Riak and requirements.
```bash
# first install Riak dependencies
apt-get install libssl-dev
apt-get install libffi-dev

# Install Java for Riak Solr search
apt-add-repository ppa:webupd8team/java -y && apt-get update
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
apt-get install -y oracle-java8-installer
```

```bash
# install riak
curl -s https://packagecloud.io/install/repositories/zetaops/riak/script.deb.sh |sudo bash
apt-get install riak=2.1.1-1
```

```bash
# activate search
sed -i "s/search = off/search = on/" /etc/riak/riak.conf

# restart riak service
service riak restart

# install Redis-Server.
apt-get install redis-server
```

Make all setups for installation of Zato.
```bash
apt-get install apt-transport-https
curl -s https://zato.io/repo/zato-0CBD7F72.pgp.asc | sudo apt-key add -
apt-add-repository https://zato.io/repo/stable/2.0/ubuntu
apt-get update
apt-get install zato
```

After installation of Zato, switch to zato(user) and create ulakbus folder at home directory.
```bash
sudo su - zato
mkdir ~/ulakbus
```


Create a Zato Cluster. This will set up a Certificate Authority (CA), web admin, a load-balancer, and Zato servers without asking password.

```bash
zato quickstart create ~/ulakbus sqlite localhost 6379 --kvdb_password='' --verbose
```

Create pwzato.config file under ~/ulakbus and write down below script in it.To use this script you should run ```zato from-config ~/ulakbus/pwzato.config```

```bash
command=update_password
path=/opt/zato/ulakbus/web-admin
store_config=True
username=admin
password=ulakbus  
```

Switch back to root user to start zato as service

Create symbolic links  for zato components

```bash
ln -s /opt/zato/ulakbus/load-balancer /etc/zato/components-enabled/ulakbus.load-balancer
ln -s /opt/zato/ulakbus/server1 /etc/zato/components-enabled/ulakbus.server1
ln -s /opt/zato/ulakbus/server2 /etc/zato/components-enabled/ulakbus.server2
ln -s /opt/zato/ulakbus/web-admin /etc/zato/components-enabled/ulakbus.web-admin
```

Start zato service

```bash
service zato start

```

Prepare python virtual environment for Ulakbus Application.

```bash
apt-get install virtualenvwrapper
```

Create app folder and add ulakbus(user) for app
```bash
mkdir /app
/usr/sbin/useradd --home-dir /app --shell /bin/bash --comment 'ulakbus operations' ulakbus
```

Make app owned by ulakbus user and switch to ulakbus user.
```bash
chown ulakbus:ulakbus /app -Rf
su ulakbus
cd ~
```
Create virtual environment and activate it.
```bash
virtualenv --no-site-packages env
source env/bin/activate
```
Upgrade pip and install ipython
```bash
pip install --upgrade pip
pip install ipython

```

Clone pyoko from ``` https://github.com/zetaops/pyoko.git  ``` and install requirenments.

```bash

pip install riak
pip install enum34
pip install six

pip install git+https://github.com/zetaops/pyoko.git
```

Add PYOKO_SETTINGS variable to env as root(user)

```bash
echo "export PYOKO_SETTINGS='ulakbus.settings'" >> /etc/profile

```

Clone ulakbus from ``` https://github.com/zetaops/ulakbus.git  ``` and install requirenments.

```bash
pip install falcon
pip install beaker
pip install redis
pip install passlib
pip install git+https://github.com/didip/beaker_extensions.git#egg=beaker_extensions
pip install git+https://github.com/zetaops/SpiffWorkflow.git#egg=SpiffWorkflow
pip install git+https://github.com/zetaops/zengine.git#egg=zengine

git clone https://github.com/zetaops/ulakbus.git

```
Clone ulakbus-ui from ``` https://github.com/zetaops/ulakbus-ui.git  ```

```bash
git clone https://github.com/zetaops/ulakbus-ui.git
```
Add ulakbus to PYTHONPATH

```bash
echo '/app/ulakbus' >> /app/env/lib/python2.7/site-packages/ulakbus.pth
```

Create __init__.py file to make google library working as ulakbus(user)

```bash
touch /app/env/lib/python2.7/site-packages/google/__init__.py
```

Download solr_schema_template for pyoko as ulakbus(user)

```bash
cd ~/env/local/lib/python2.7/site-packages/pyoko/db
wget https://raw.githubusercontent.com/zetaops/pyoko/master/pyoko/db/solr_schema_template.xml

```

Create symbolic links for zato(user)

```bash
ln -s /app/pyoko/pyoko /opt/zato/2.0.5/zato_extra_paths/
ln -s /app/env/lib/python2.7/site-packages/riak /opt/zato/2.0.5/zato_extra_paths/
ln -s /app/env/lib/python2.7/site-packages/riak_pb /opt/zato/2.0.5/zato_extra_paths/
ln -s /app/env/lib/python2.7/site-packages/google /opt/zato/2.0.5/zato_extra_paths/
ln -s /app/env/lib/python2.7/site-packages/passlib /opt/zato/2.0.5/zato_extra_paths/

```

Create a bucket type named models and activate it with following commands as root(user)
```bash
riak-admin bucket-type create models '{"props":{"last_write_wins":true, "allow_mult":false}}'
riak-admin bucket-type activate models
```

To update schemas run the following command for ulakbus(user)
```bash
source env/bin/activate
cd ~/ulakbus/ulakbus
python manage.py update_schema --bucket all
```

Start server on port 8000 default
```bash
python server.py
```
