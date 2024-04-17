import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def connect():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('src/googlecalendar/token.json'):
        creds = Credentials.from_authorized_user_file('src/googlecalendar/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'src/googlecalendar/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('src/googlecalendar/token.json', 'w') as token:
            token.write(creds.to_json())
    return(creds)    

def createcalendar(user):
    creds = connect()
    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        calendar = {
            #'summary': str(user_id)+first_name+last_name,
            'summary': str(user.id)+'_'+user.first_name+'_'+user.last_name,
            'timeZone': 'Europe/Berlin'
        }
        #Crear calendario para cada fisio
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_created = created_calendar['id']
        #Guardar en base de datos
        cal = calendar_created
    except HttpError as error:
        print('An error occurred: %s' % error)
        cal = None
    return (cal)

def createevent(physio,user,times):
    creds = connect()
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        event = {
        'summary': 'PhysiOnline-'+physio.last_name+' '+physio.first_name,
        'description': 'Online appointment for user: '+user.last_name+ ' '+user.first_name,
        'start': {
            'dateTime': times['starting_time']+'+01:00',
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': times['ending_time']+'+01:00',
            'timeZone': 'Europe/Berlin',
        },
        'attendees': [
            {'email': physio.email},
            {'email': user.email},
        ],
        'conferenceData': {
            'createRequest': {'requestId': "7qxalsvy0e"}
        }
        }
        event = service.events().insert(calendarId=physio.calendarid, body=event, conferenceDataVersion=1).execute()
        
    except HttpError as error:
        print('An error occurred: %s' % error)
        event = None
        
    return (event)

def update_event(calendarid, eventid,times):
    creds = connect()
    print(creds)
    try:
        service = build('calendar', 'v3', credentials=creds)

        
        # First retrieve the event from the API.
        event = service.events().get(calendarId=calendarid, eventId=eventid).execute()
        
        event['start']['dateTime'] = times['starting_time']+'+01:00'
        event['end']['dateTime'] = times['ending_time']+'+01:00'
        #print(event['start']['dateTime'])
        
        updated_event = service.events().update(calendarId=calendarid, eventId=event['id'], body=event).execute()

        # Print the updated date.
        #print (updated_event['updated'])

    except HttpError as error:
        print('An error occurred: %s' % error)

def delete_event(calendarid, eventid):
    creds = connect()
    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId=calendarid, eventId=eventid).execute()
    
    except HttpError as error:
        print('An error occurred: %s' % error)

def auth_googlecalendar():
    creds = connect()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        print("Google calendar is working")
    except HttpError as error:
        print(f"An error occurred: {error}") 