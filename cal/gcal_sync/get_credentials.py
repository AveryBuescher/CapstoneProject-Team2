from __future__ import print_function
import pickle
import os.path
from os.path import dirname, join
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# Returns user's credentials if they are already saved. Lets the user
# log in if they aren't, saves them, and then returns them.
def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    cred_filepath = join(dirname(__file__), "credentials.json")
    token_filepath = join(dirname(__file__), "token.json")
    creds = None
    if os.path.exists(token_filepath):
        creds = Credentials.from_authorized_user_file(token_filepath, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_filepath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_filepath, 'w') as token:
            token.write(creds.to_json())
    return creds
