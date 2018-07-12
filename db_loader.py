#!/usr/bin/python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sqlite3
import dateutil.parser as parser


def main():
	conn = sqlite3.connect('gmail.db')
	print ("Opened database successfully");
	conn.execute('''CREATE TABLE IF NOT EXISTS GMAIL_MESSAGES
	         (id INTEGER PRIMARY KEY AUTOINCREMENT,
	         message_id TEXT  UNIQUE     NOT NULL,
	         message_subject TEXT NOT NULL,
	         message_from TEXT NOT NULL,
	         message_to TEXT NOT NULL,
	         message_date TEXT
	         );''')
	# Setup the Gmail API
	SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
	store = file.Storage('credentials.json')
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	service = build('gmail', 'v1', http=creds.authorize(Http()))

	# Call the Gmail API
	response = service.users().messages().list(userId='me',labelIds=['INBOX']).execute()

	messages = []
	if 'messages' in response:
		messages.extend(response['messages'])
	while 'nextPageToken' in response:
		page_token = response['nextPageToken']
		response = service.users().messages().list(userId='me',labelIds=['INBOX'],pageToken=page_token).execute()
		messages.extend(response['messages'])
	final_message_list = [ ]

	for message in messages:
		temp_dict = { }
		message_id = message['id'] 
		message_info = service.users().messages().get(userId='me', id=message_id).execute()
		payload = message_info['payload']
		headers = payload['headers'] 
		temp_dict['message_id']=message_id
		for header in headers: 
			if header['name'] == 'Subject':
				msg_subject = header['value']
				temp_dict['message_subject'] = msg_subject
			if header['name'] == 'Date':
				msg_date = header['value']
				date_parse = (parser.parse(msg_date))
				m_date = (date_parse.date())
				temp_dict['message_date'] = str(m_date)
			elif header['name'] == 'From':
				msg_from = header['value']
				temp_dict['message_from'] = msg_from
			elif header['name'] == 'Delivered-To':
				msg_to = header['value']
				temp_dict['message_to'] = msg_to
			else:
				pass
		final_message_list.append(temp_dict)

	for message_dict in final_message_list:
		conn.execute("INSERT OR IGNORE INTO GMAIL_MESSAGES (message_id,message_subject,message_from,message_to,message_date)\
			VALUES (?,?,?,?,?)",(message_dict['message_id'],message_dict['message_subject'],message_dict['message_from'],message_dict['message_to'],message_dict['message_date']));
	conn.commit()
	print("Finished successfully")
	conn.close()


if __name__ == "__main__":
    main()