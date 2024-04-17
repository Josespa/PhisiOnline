"""
run this file to generate the token.json file needed for google calendar,
go to src/googlecalendar to valite the json file
once google calendar is working it is possible to run the application
"""
from src.googlecalendar.googlecalendar import auth_googlecalendar


if __name__ == "__main__":
    auth_googlecalendar()