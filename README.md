# twitter cleaner


## Setup

Create a zappa and tweepy (and dependencies) virtual environment.
This will ensure that the Zappa deploy is as small as possible.

```
python3 -m venv ~/venv
. ~/venv/bin/activate
pip install tweepy
pip install zappa
```

## Initialise Zappa

```zappa init```

This creates a zappa_settings.json file. 
