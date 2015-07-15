Önce bilgisayarda yeni bir uzantı oluşturup içine girin.

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

Ardından ```nano Vagrantfile``` komutunu girip

```bash
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 8183, host: 8183
```

Son satırı böyle değiştiriyoruz. 

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

PostgreSQL Apt Repository altından sürüm seçimi yapın, deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main burdaki repoyu ```/etc/apt/sources.list.d/pgdg.list``` ' ya ekleyin.


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

Ardından sırası ile

```
create user zato createdb createuser password 'zatopassword';
create database zatodb;
```
diyerek zato için gerekli postgresql kurulumunu tamamlayınız.


Ardından iki kere ard arda``` exit ``` diyerek postgres ve root kullanıcısından çıkıp, bundan sonraki işlemlerde zato kullanıcısına geçilir ve yeni bir klasör oluşturulur.

```
sudo su - zato
mkdir aa
```

Vagrant'ı, Zato'yu ve Redis Server başarılı bir şekilde oluşturulduğa göre şimdi sırası ile 

```
1- ODB kurulumu
2- Cluster kurulumu
3- Server kurulumu
4- Web Admin kurulumu
5- Load Balancer kurulumu
```

işlemlerini gerçekleştiriyoruz.

1 - ODB KURULUMU ``` https://zato.io/docs/admin/cli/create-odb.html ```

Kurulum için aşağıdaki kullanımdan yararlanarak 

```
  zato create odb [-h] [--store-log] [--verbose] [--store-config]
  [--postgresql_schema POSTGRESQL_SCHEMA] [--odb_password ODB_PASSWORD]
  odb_type odb_host odb_port odb_user odb_db_name
```

veya

```
zato create odb postgresql --odb_host localhost --odb_port 5432 --odb_user zato --odb_db_name zatodb --postgresql_schema zato --odb_password 'zatopassword'
```

komutu ile sqlite türünde odb kurulumunu gerçekleştirilir.

2 - CLUSTER KURULUMU ``` https://zato.io/docs/admin/cli/create-cluster.html ```

Kurulum için aşağıdaki kullanımdan yararlanarak

```
    zato create cluster [-h] [--store-log] [--verbose] [--store-config]
    [--postgresql_schema POSTGRESQL_SCHEMA] [--odb_password ODB_PASSWORD]
    [--tech_account_password TECH_ACCOUNT_PASSWORD]
    odb_type odb_host odb_port odb_user odb_db_name
    lb_host lb_port lb_agent_port
    broker_host broker_port cluster_name tech_account_name
```
veya direk 

```
zato create cluster postgresql localhost 11223 20151 localhost 6379 PROD3 techacc --odb_host localhost --odb_port 5432 --odb_user zato --odb_db_name zatodb --postgresql_schema zato --odb_password 'zatopassword'
``` 

komutu ile PROD3 adında cluster eklenir. Şifre için herhangi birşey girebilir.


3 - SERVER KURULUMU

Önce ``` mkdir aa/server ``` ile bir uzantı oluşturulur,

CA kurulumları gerçekleştirilir,

```
mkdir aa/ca1
zato ca create ca ~/aa/ca1
zato ca create lb_agent ~/aa/ca1/ zato_lb_agent1
zato ca create server ~/aa/ca1/ PROD3 server
zato ca create web_admin ~/aa/ca1/
```

İsterseniz kendiniz aşağıdaki komutlar yardımı ile,

```
zato create server [-h] [--store-log] [--verbose] [--store-config]
    [--postgresql_schema POSTGRESQL_SCHEMA] [--odb_password ODB_PASSWORD]
    [--kvdb_password KVDB_PASSWORD]
    path odb_type odb_host odb_port odb_user odb_db_name
    kvdb_host kvdb_port pub_key_path priv_key_path
    cert_path ca_certs_path cluster_name server_name
```

isterseniz de,

```
zato create server ~/aa/server postgresql localhost 6379 ~/aa/ca1/out-pub/PROD3*.pem ~/aa/ca1/out-priv/PROD3*.pem ~/aa/ca1/out-cert/PROD3*.pem ~/aa/ca1/ca-material/ca-cert.pem PROD3 server --odb_host localhost --odb_port 5432 --odb_user zato --odb_db_name zatodb --postgresql_schema zato --odb_password 'zatopassword'
```

komutu ile kurulumu gerçekleştirebilirsiniz.

4 - WEB ADMIN KURULUMU

Öncelikle sırası ile aşağıdaki komutları çalıştırarak gerekli sertifikalar kurulur 

```
mkdir aa/ca2
zato ca create ca ~/aa/ca2
zato ca create lb_agent ~/aa/ca2/ zato_lb_agent1
zato ca create server ~/aa/ca2/ PROD3 server
zato ca create web_admin ~/aa/ca2/
```

ardından, ``` mkdir aa/web-admin ``` ile bir uzantı oluşturulur ve

```
zato create web_admin ~/aa/web-admin postgresql ~/aa/ca2/out-pub/web-admin*.pem ~/aa/ca2/out-priv/web-admin*.pem ~/aa/ca2/out-cert/web-admin*.pem ~/aa/ca2/ca-material/ca-cert.pem techacc --odb_host localhost --odb_port 5432 --odb_user zato --odb_db_name zatodb --postgresql_schema zato --odb_password 'zatopassword'
```

komutu ile kurulum gerçekleştirilir.

5 - LOAD BALANCER KURULUMU

```
mkdir aa/ca3
zato ca create ca ~/aa/ca3
zato ca create lb_agent ~/aa/ca3/ zato_lb_agent1
zato ca create server ~/aa/ca3/ PROD3 server
zato ca create web_admin ~/aa/ca3/
```

komutları ile sertifikalar kurulur.

``` mkdir aa/load-balancer ``` diye uzantı oluşturulur ve gerekli kurulum yapılır

```
zato create load_balancer ~/aa/load-balancer/ ~/aa/ca3/out-pub/lb*.pem ~/aa/ca3/out-priv/lb*.pem ~/aa/ca3/out-cert/lb*.pem ~/aa/ca3/ca-material/ca-cert.pem
```

veya 

```
    zato create load_balancer [-h] [--store-log] [--verbose] [--store-config]
    path pub_key_path priv_key_path cert_path ca_certs_path
```


redis-cli 
CONFIG SET requirepass "1"
AUTH 1

