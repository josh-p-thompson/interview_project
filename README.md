# Software Engineer - Data Engineering Team Interview Exercise

## Description

### marvel.py

Handles the core logic of the solution: 
* ```store_characters()``` - executes calls to the /Characters endpoint and stores the results in a SQLite database
* ```CharacterFinder``` - populates character attributes and provides overlapping comics with additionally provided character

### marvel_client.py

Simple client for relevant Marvel endpoints.

### db.py

Handles connection, storage, and queries to SQLite database.  

## Getting Started

I developed this solution with Python. 

### Dependencies

Dependencies are (also outlined in the Pipfile): 
* pandas - manipulating and storing data
* requests - making requests to the Marvel API 
* python-dotenv - importing api keys in .env file

### Prerequisites

Add a .env file in this directory and add your Marvel API keys like so: 

```
PUBLIC_KEY = 'your_key_goes_here'
PRIVATE_KEY = 'your_key_goes_here'
```

### Installing

If you haven't downloaded pipenv, do so: 

```
pip install pipenv
```

From this directory, install dependent packages: 
```
pipenv install
```

### Running the Solution

Activate the Pipenv shell: 
```
pipenv shell
```

Execute the solution: 
```
python marvel.py
```

## Tests

Execute all tests: 
```
python -m unittest discover 
```