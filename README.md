## Development

### Install virtualenv

[Read more on virtualenv here.](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

```
sudo pip install virtualenv
```

### Setup environment

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run in debug mode with your bot API key

`EVEBOT_TOKEN="TOKEN" EVEBOT_DEBUG=1 ./evebot.py`

### Freeze deps

```
pip freeze > requirements.txt
```