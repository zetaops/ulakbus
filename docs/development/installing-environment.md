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

Switch back to root user to prepare python virtual environment for Ulakbus Application.

```bash
logout
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
Clone ulakbus from ``` https://github.com/zetaops/ulakbus.git  ``` and install requirenments.

```bash
pip install falcon
pip install beaker
pip install redis
pip install git+https://github.com/didip/beaker_extensions.git#egg=beaker_extensions
pip install git+https://github.com/zetaops/SpiffWorkflow.git#egg=SpiffWorkflow
pip install git+https://github.com/zetaops/zengine.git#egg=zengine

git clone https://github.com/zetaops/ulakbus.git

```
Clone ulakbus-ui from ``` https://github.com/zetaops/ulakbus.git  ```

```bash
git clone https://github.com/zetaops/ulakbus-ui.git
```
Add ulakbus and ulakbus-ui to PYTHONPATH

```bash
echo '/app/ulakbus' >> /app/env/lib/python2.7/site-packages/ulakbus.pth
echo '/app/ulakbus-ui' >> /app/env/lib/python2.7/site-packages/ulakbus-ui.pth
```

Start server on port 8000 default
```bash
python server.py
```
