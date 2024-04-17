# PhysiOnline
The web application project aims to create a virtual physiotherapy platform that connects patients and therapists online. This platform called PhysiOnline makes it easy to schedule appointments, virtual consultations, and manage user profiles. The technology stack includes Python (Flask), PostgreSQL, Google Calendar API, and Bootstrap for the frontend. 

## Requirements

- Phython 3.12 or greater. 

- pip

- Gmail account

## Installation

Read the documentation related to Google Calendar in: https://developers.google.com/calendar/api/quickstart/python

```bash
py -m venv venv
```

```bash
venv\Scripts\activate
```

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
### Google calendar

Prerequisites:
- A Google Cloud project.
- A Google account with Google Calendar enabled.
- Set up the environment.
- Enable the API.
- Configure the OAuth consent screen.
- Authorize credentials for a desktop application.

The credentials.json file should be moved to the src/googlecalendar directory in the source code, the file in the is for the reference.

#### To test the connection with google calendar
Go to the terminal and run:

```bash
py google_calendar.py
```

Accept and provide access in the browser.

Go to src/googlecalendar to see the token.json file.

After this, the environment it is not needed, can use deactivate it in the terminal.

```bash
deactivate
```

## Docker 

Run in the terminal for docker:

```bash
docker compose up -d flask_db
```

```bash
docker compose build
```

```bash
docker compose up flask_app
```

Create an admin user typing /createadmin in the browser.

## Run in local

Go to the _init_.py file in the source code, it contains the configuration for the environment.

Change 

- app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
To

- app.config["SQLALCHEMY_DATABASE_URI"] = Config.connection_string_config

It will allow to connect to the PostgreSQL database locally install.

Create the database in PostgreSQL. 
The information related to the database is in src/database/db.py

Activate the environment and install the requirements running:

```bash
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

To run the program just:

```bash
flask run 
```
