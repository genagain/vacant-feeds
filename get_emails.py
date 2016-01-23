from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import ipdb
import base64
from bs4 import BeautifulSoup
import requests

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Vacant Feeds'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'vacant-feeds.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    messages_list = service.users().messages().list(userId='me').execute()
    messID = str(messages_list['messages'][0]['id'])
    userID = "me"
    test_email = service.users().messages().get(userId=userID,id=messID).execute()
    email_content = ""
    parts = test_email['payload']['parts']
    for part in parts:
      test_data = part['body']['data']
      decoded=base64.urlsafe_b64decode(test_data.encode('ASCII'))
      email_content += decoded

    soup = BeautifulSoup(email_content,'html.parser')
    unique_content = []
    unique_links = []
    for link in soup.find_all('a'):
      url = link.get('href')
      response = requests.get(url)
      if response.__dict__['_content'] in unique_content:
        pass
      else:
        unique_content.append(response.__dict__['_content'])
        unique_links.append(response.url)

if __name__ == '__main__':
    main()
