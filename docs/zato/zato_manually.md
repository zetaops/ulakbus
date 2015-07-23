Şimdi bilgisayara zatonun manuel kurulumunu gerçekleştireceğiz ve aşağıdaki stepleri izleyeceğiz

 * Vagrant ile sistem kurulumu
 * Gerekli ayarlar
 * Redis Server kurulumu
 * Postgresql kurulumu
 * Zato kurulumu
* ODB kurulumu
* Cluster kurulumu
* Server kurulumu
* Web Admin kurulumu
* Load Balancer kurulumu

İlk olarak bilgisayarda yeni bir dizin oluşturup içine girin.

```
mkdir zato
cd zato
```

Şimdi gerekli olan vagrant kurulumu

```
vagrant init ubuntu/trusty64
```

ve ardından

```
vagrant up
```

komutları ile gerçekleştirilir.

Ardından  oluşturduğumuz klasörün içindeki ```Vagrantfile``` dosyasını aşağıdaki gibi değiştiriyoruz.

```  bash
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 8183, host: 8183
```

Tüm bunlar bittikten sonra ``` vagrant ssh ``` diyerek sistemime bağlanılır.

Bağlantı başarılı bir şekilde gerçekleştikten sonra, ilk olarak ```sudo su``` ile root olup, Zato'nun kurulumunu gerçekleştirilir,

```
apt-get install apt-transport-https
curl -s https://zato.io/repo/zato-0CBD7F72.pgp.asc | sudo apt-key add -
apt-add-repository https://zato.io/repo/stable/2.0/ubuntu
apt-get update
apt-get install zato
```

Ardından, Redis-Server kurulumu

```
apt-get install redis-server
```

komutları ile yapılır.

Şimdi Postgresql kurulumu için öncelikle http://www.postgresql.org/download/ sitesine girip, linux sisteminize göre seçim yapın.

Ubuntu/trusty14.04 için

PostgreSQL Apt Repository altından sürüm seçimi yapın, ```deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main``` burdaki repoyu ```/etc/apt/sources.list.d/pgdg.list``` ' ya ekleyin.


Ardından gpg keyi terminale giriniz,

```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
```

Postgresql kurulumu için

```apt-get install postgresql-9.4```

komutunu giriniz.

Kurulum sonunda

```
su postgres
```

komutu ile postgres kullanıcısına geçiniz.

Ardından ```psql``` komutunu ve

```
create user zato createdb createuser password 'zatopassword';
create database zatodb;
```
komutları ile zato için gerekli postgresql kullanıcısı ve database kurulumunu tamamlayınız.


Ardından önce ```\q``` sonra iki kere ard arda``` exit ``` diyerek postgres ve root kullanıcısından çıkıp, bundan sonraki işlemlerde zato kullanıcısına geçilir ve yeni bir klasör oluşturulur.

```
sudo su - zato
mkdir aa
```

işlemlerini gerçekleştiriyoruz.

1 - ODB KURULUMU ``` https://zato.io/docs/admin/cli/create-odb.html ```

Kurulum için aşağıdaki kullanımdan yararlanarak

```
  zato create odb [-h] [--store-log] [--verbose] [--store-config]
                       [--odb_host ODB_HOST] [--odb_port ODB_PORT]
                       [--odb_user ODB_USER] [--odb_db_name ODB_DB_NAME]
                       [--postgresql_schema POSTGRESQL_SCHEMA]
                       [--odb_password ODB_PASSWORD]
                       odb_type
```

veya

```
zato create odb \
   postgresql \
   --odb_host localhost \
   --odb_port 5432 \
   --odb_user zato \
   --odb_db_name zatodb \
   --postgresql_schema zato \
   --odb_password 'zatopassword'
```

komutu ile sqlite türünde odb kurulumunu gerçekleştirilir.

2 - CLUSTER KURULUMU ``` https://zato.io/docs/admin/cli/create-cluster.html ```

Kurulum için aşağıdaki kullanımdan yararlanarak

```
zato create cluster [-h] [--store-log] [--verbose] [--store-config]
                           [--odb_host ODB_HOST] [--odb_port ODB_PORT]
                           [--odb_user ODB_USER] [--odb_db_name ODB_DB_NAME]
                           [--postgresql_schema POSTGRESQL_SCHEMA]
                           [--odb_password ODB_PASSWORD]
                           [--tech_account_password TECH_ACCOUNT_PASSWORD]
                           odb_type lb_host lb_port lb_agent_port broker_host
                           broker_port cluster_name tech_account_name
```
veya direk

```
zato create cluster \
    postgresql \
    localhost \
    11223 \
    20151 \
    localhost \
    6379 \
    PROD3 \
    techacc \
    --odb_host \
    localhost \
    --odb_port \
    5432 \
    --odb_user zato \
    --odb_db_name zatodb \
    --postgresql_schema zato \
    --odb_password 'zatopassword'
```

komutu ile PROD3 adında cluster eklenir. Şifre için herhangi birşey girebilir.


3 - SERVER KURULUMU

Önce ``` mkdir aa/server ``` ile bir uzantı oluşturulur,

CA kurulumları gerçekleştirilir,

```
mkdir aa/ca
zato ca create ca ~/aa/ca
zato ca create lb_agent ~/aa/ca/ zato_lb_agent1
zato ca create server ~/aa/ca/ PROD3 server
zato ca create web_admin ~/aa/ca/
```

İsterseniz kendiniz aşağıdaki komutlar yardımı ile,

```
zato create server [-h] [--store-log] [--verbose] [--store-config]
                          [--odb_host ODB_HOST] [--odb_port ODB_PORT]
                          [--odb_user ODB_USER] [--odb_db_name ODB_DB_NAME]
                          [--postgresql_schema POSTGRESQL_SCHEMA]
                          [--odb_password ODB_PASSWORD]
                          [--kvdb_password KVDB_PASSWORD]
                          path odb_type kvdb_host kvdb_port pub_key_path
                          priv_key_path cert_path ca_certs_path cluster_name
                          server_name
```

isterseniz de,

```
zato create server \
   ~/aa/server \
   postgresql \
   localhost \
   6379 \
   ~/aa/ca/out-pub/PROD3*.pem \
   ~/aa/ca/out-priv/PROD3*.pem \
   ~/aa/ca/out-cert/PROD3*.pem \
   ~/aa/ca/ca-material/ca-cert.pem \
   PROD3 \
   server \
   --odb_host \
   localhost \
   --odb_port \
   5432 \
   --odb_user zato \
   --odb_db_name zatodb \
   --postgresql_schema zato \
   --odb_password 'zatopassword'
```

komutu ile kurulumu gerçekleştirebilirsiniz.

4 - WEB ADMIN KURULUMU

Öncelikle ``` mkdir aa/web-admin ``` ile bir uzantı oluşturulur ve

```
zato create web_admin [-h] [--store-log] [--verbose] [--store-config]
                             [--odb_host ODB_HOST] [--odb_port ODB_PORT]
                             [--odb_user ODB_USER] [--odb_db_name ODB_DB_NAME]
                             [--postgresql_schema POSTGRESQL_SCHEMA]
                             [--odb_password ODB_PASSWORD]
                             [--tech_account_password TECH_ACCOUNT_PASSWORD]
                             path odb_type pub_key_path priv_key_path
                             cert_path ca_certs_path tech_account_name
```

komutundan yardım alınarak,

```
zato create web_admin \
   ~/aa/web-admin postgresql \
   ~/aa/ca/out-pub/web-admin*.pem \
   ~/aa/ca/out-priv/web-admin*.pem \
   ~/aa/ca/out-cert/web-admin*.pem \
   ~/aa/ca/ca-material/ca-cert.pem \
   techacc \
   --odb_host localhost \
   --odb_port 5432 \
   --odb_user zato \
   --odb_db_name zatodb \
   --postgresql_schema zato \
   --odb_password 'zatopassword'
```

komutu ile kurulum gerçekleştirilir.

5 - LOAD BALANCER KURULUMU


``` mkdir aa/load-balancer ``` diye uzantı oluşturulur ve gerekli kurulum yapılır

```
zato create load_balancer \
   ~/aa/load-balancer/ \
   ~/aa/ca/out-pub/lb*.pem \
   ~/aa/ca/out-priv/lb*.pem \
   ~/aa/ca/out-cert/lb*.pem \
   ~/aa/ca/ca-material/ca-cert.pem
```

veya

```
    zato create load_balancer [-h] [--store-log] [--verbose]
                                 [--store-config]
                                 path pub_key_path priv_key_path cert_path
                                 ca_certs_path
```

Ardından redis server a password atamak için ilk olarak ```redis-cli ``` komutunu giriniz.

Sonra aşağıdaki komutları girerek işlemi bitirebilirsiniz.

```
CONFIG SET requirepass "1"
AUTH 1
exit
```

Kurulumların hepsi başarı ile tamamlandı ise aşağıdaki komutlar ile sistemi aktif hale getirebilirsiniz.

```
zato start ~/aa/server
zato start ~/aa/load-balancer
zato start ~/aa/web-admin
```

Şimdi herhangi bir tarayıcı açarak http://localhost:8183 adresine bağlanınız.

kullanıcı adı:admin
şifre: 1

olarak giriş yapınız.

Gelen sayfada ilk sekme olan Cluster->Server-> add-to-lb ye basiniz.
Ardından Clusters -> (pick one from the table) -> Load-balancer -> Config GUI view 'den  server port'u 17010 olarak  değiştiriniz.
