ULAKBUS_PATH=/worker/build/ulakbus
cd $ULAKBUS_PATH && pip install -r requirements/develop.txt
cd $ULAKBUS_PATH/ulakbus
python manage.py migrate --model all
python manage.py load_diagrams
python manage.py load_data --path fixtures/base.csv
python manage.py load_data --path ../tests/fixtures
python manage.py load_fixture --path fixtures
python manage.py preparemq
cd $ULAKBUS_PATH/tests && py.test --ignore=fixture .
ln -s $ULAKBUS_PATH/ulakbus/ /usr/local/lib/python2.7/site-packages/ulakbus/
