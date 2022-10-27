# CupApp2

CupApp is an django-based web application written for manage FIFA/PES cups organized among friends.

# Instalation

```sh
$ git clone https://github.com/sequencer-pl/cupapp2.git
$ cd cupapp2/
$ poetry install
$ poetry shell
$ cd cupapp2/
$ python manage.py migrate
$ python manage.py runserver 8000
```
and in browser go to:
```
http://127.0.0.1:8000/
```

If you do not have enough permissions and got error like this:
```
ValueError: Unable to configure handler 'error_file_handler': [Errno 2] No such file or directory: '/var/log/cupapp2/errors.log'
```
make sure you have 'write' access to /var/log/cupapp2 directory and it's exists or change logging paths in logging.yaml like this:
```
$ sed -i 's/\/var\/log\/cupapp2\///g' logger/logging.yaml
```

For beeing able to log in to application, you have to create user account. First create superuser (admin) with:
```
$ python manage.py createsuperuser
```
and with this credentials you can log in to admin page:
```
http://127.0.0.1:8000/admin/
```
