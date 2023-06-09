import os
import pathlib
import requests

from flask import Flask, redirect, request, session
from google.oauth2 import id_token
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from googleapiclient.discovery import build
import google.auth.transport.requests
import webbrowser 

app = Flask("Pov6")
app.secret_key = 'your_secret_key'

# Set up OAuth 2.0 client credentials
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/spreadsheets', 
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.email', 
    'https://www.googleapis.com/auth/userinfo.profile'
    ]
CLIENT_SECRETS_FILE = 'OAuth_2.json'
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, 
    SCOPES, 
    redirect_uri="http://127.0.0.1:5000/oauth2callback")

# Env var for local testing to allow for OAuth to work on Http 
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "430942459750-qerrg3bduqqnjc6lqtus0qaavgu5af6n.apps.googleusercontent.com"

@app.route('/')
def index():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Retrieve the authorization code and exchange it for credentials
    # flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri="http://127.0.0.1:5000/oauth2callback")
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500) #State does not match! 

    flow_credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=flow_credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["gogole_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    # Create a new Google Sheet with hard-coded values
    spreadsheet_id = create_google_sheet(flow_credentials)

    # # Open the Google Sheet URL in the default browser
    sheet_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'
    
    return redirect(sheet_url, code=302)


# Create a new Google Sheet with hard-coded values
def create_google_sheet(flow_credentials):
    # Initialize the Google Sheets API
    service = build('sheets', 'v4', credentials=flow_credentials)

    # creds = credentials.Credentials.from_authorized_user_info(session['credentials'])
    # service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)

    spreadsheet = {
        'properties': {
            'title': 'My Sheet'
        },
        'sheets': [
            {
                'properties': {
                    'title': 'Sheet 1'
                },
                'data': [
                    {
                        'rowData': [
                            {'values': [{'userEnteredValue': {'stringValue': 'Value 1'}}]},
                            {'values': [{'userEnteredValue': {'stringValue': 'Value 2'}}]},
                            {'values': [{'userEnteredValue': {'stringValue': 'Value 3'}}]}
                        ]
                    }
                ]
            }
        ]
    }

    request = service.spreadsheets().create(body=spreadsheet)
    response = request.execute()
    spreadsheet_id = response['spreadsheetId']

    return spreadsheet_id

if __name__ == '__main__':
    app.run(debug=True)
