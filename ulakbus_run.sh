PYTHON="python"
ULAKBUS_PATH=/worker/build/ulakbus
cd $ULAKBUS_PATH && pip install -r requirements/develop.txt
cd $ULAKBUS_PATH/ulakbus
$PYTHON manage.py migrate --model all
$PYTHON manage.py load_diagrams
$PYTHON manage.py load_data --path fixtures/base.csv
$PYTHON manage.py load_data --path ../tests/fixtures
$PYTHON manage.py load_fixture --path fixtures
$PYTHON manage.py preparemq
cd $ULAKBUS_PATH/tests && py.test --ignore=fixture .
ln -s $ULAKBUS_PATH/ulakbus/ /usr/local/lib/python2.7/site-packages/ulakbus/
