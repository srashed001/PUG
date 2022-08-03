# PUG V1 (Server-side Rendering)

PUGV1 is web-application that connects users interested in creating and joining pickup games. Application is integrated with Google Maps API, to help users find basketball courts in their area. This version of PUG contains very basic functionality. 

Features include: 
- create/update pickup games 
- find users 
- find basketball courts in area

Tech Stack: Python, SQL, SQLAlchemy, PostgreSQL, Flask, Flask-WTF, Bcrypt, Jinja



## Installation

Create Python Virtual Environment
```bash
  $ python3 -m venv venv
  $ source venv/bin/activate
  (venv) $ pip install -r requirements.txt
```

Setup Database
```bash
  (venv) $ createdb pugV1db
  (venv) $ python seed.py
```

## Usage

Start Server
```bash
  (venv) $ flask run
```


## License
Sami Rashed
