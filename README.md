## Development

### Install virtualenv

For best results use [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

```
sudo pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run in debug mode with your bot API key

`EVEBOT_TOKEN="TOKEN" ./evebot.py -d`
