DEVELOPMENT ENVIRONMENT SETUP
=============================

 . First update and upgrade base system
``` 
     apt-get update
     apt-get upgrade
```     
 . Change file size limit to 65536 for Riak.
 
    ulimit -n 65536
     
 . Install Riak and requirements. 
     # install java for riak solr search
```
     apt-add-repository ppa:webupd8team/java -y && apt-get update
     echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
     apt-get install -y oracle-java8-installer```

    # install riak
    curl -s https://packagecloud.io/install/repositories/zetaops/riak/script.deb.sh |sudo bash
     apt-get install riak=2.1.1-1
```
    # activate search
    sed -i "s/search = off/search = on/" /etc/riak/riak.conf 
     
    # restart riak service
    service riak restart     
    
    
    # Install Redis-Server.
    apt-get install redis-server ```
     
 . Make all setups for installation of Zato.
```
     apt-get install apt-transport-https
     curl -s https://zato.io/repo/zato-0CBD7F72.pgp.asc | sudo apt-key add -
     apt-add-repository https://zato.io/repo/stable/2.0/ubuntu
     apt-get update
     apt-get install zato
```     
  . After installation of Zato, switch to zato(user) and create ulakbus folder at home directory.
```
     sudo su - zato
     mkdir ~/ulakbus
```     
     
     
 .  Create a Zato Cluster. This will set up a Certificate Authority (CA), web admin, a load-balancer, and Zato servers without asking password.

```zato quickstart create ~/ulakbus sqlite localhost 6379 --kvdb_password='' --verbose``` 
 
 .  Install Pyoko
```    pip install git+https://github.com/zetaops/pyoko.git ```
    

 . Switch back to root user to prepare python virtual environment for Ulakbus Application.
```
     logout
     apt-get install virtualenvwrapper
```     
 
 . Create app folder and add a user for app
```
     mkdir /app
     /usr/sbin/useradd --home-dir /app --shell /bin/bash --comment 'ulakbus operations' ulakbus
```
 . Make app owned by ulakbus user and switch to ulakbus user.
```
     chown ulakbus:ulakbus /app -Rf
     su ulakbus
     cd ~
``` 
 . Create virtual environment and activate it.
```  
     virtualenv --no-site-packages env
     source env/bin/activate
``` 
 . Clones ulakbus from https://github.com/zetaops/ulakbus.git and installs requirenments.
```  
     pip install --upgrade pip
     git clone https://github.com/zetaops/ulakbus.git
     cd /app/ulakbus
     pip install -r requirements.txt
     pip install git+https://github.com/zetaops/pyoko.git
``` 
 . Start server port 8000 default
```     python server.py  ```

