#!/usr/bin/python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sqlite3
import json

def actions(service,actions,message_id_list):
	for message_id in message_id_list:
		for action in actions:
			if  "mark_as_read" in action['action']:
				message_labels={'removeLabelIds': ['UNREAD'], 'addLabelIds': ['INBOX']}
				message = service.users().messages().modify(userId='me', id=message_id,
											body=message_labels).execute()
			elif "mark_as_unread" in action['action']:
				message_labels={'removeLabelIds': [], 'addLabelIds': ['UNREAD','INBOX']}
				message = service.users().messages().modify(userId='me', id=message_id,
											body=message_labels).execute()
			elif "archive" in action['action']:
				message_labels={'removeLabelIds': ['INBOX'], 'addLabelIds': []}
				message = service.users().messages().modify(userId='me', id=message_id,
											body=message_labels).execute()
			elif "add_label" in action['action']:
				new_label=action['value']
				message_labels={'removeLabelIds': [], 'addLabelIds': ['INBOX',new_label]}
				message = service.users().messages().modify(userId='me', id=message_id,
											body=message_labels).execute()
	print("Actions performed successfully")

def main():
	# Setup the Gmail API
	SCOPES = 'https://mail.google.com/'
	store = file.Storage('credentials.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('gmail', 'v1', http=creds.authorize(Http()))
	# Call the Gmail API
	response = service.users().messages().list(userId='me').execute()
	conn = sqlite3.connect('gmail.db')
	print ("Opened database successfully")
	with open('rules.json') as outfile:
		jsondata=json.load(outfile)
		for rule in jsondata['rules']:
			value={}
			if rule['overall_predicate']=="all":
				message_id_list=[]
				condition_string=""
				query_string="SELECT * from GMAIL_MESSAGES WHERE "
				for condition in rule['conditions']:
					if condition['field']=="from" and condition['predicate']=="contains":
						condition_string=condition_string+"message_from LIKE '%"+condition['value'] +"%'"
					if condition['field']=="to" and condition['predicate']=="contains":
						condition_string=condition_string+"message_to LIKE '%"+condition['value'] +"%'"
					if condition['field']=="subject" and condition['predicate']=="contains":
						condition_string=condition_string+"message_subject LIKE '%"+condition['value'] +"%'"
					if condition['field']=="from" and condition['predicate']=="equals":
						condition_string=condition_string+"message_from = '"+condition['value'] +"' "
					if condition['field']=="to" and condition['predicate']=="equals":
						condition_string=condition_string+"message_to = '"+condition['value'] +"' "
					if condition['field']=="subject" and condition['predicate']=="equals":
						condition_string=condition_string+"message_subject = '"+condition['value'] +"' "

					if condition['field']=="from" and condition['predicate']=="not_contains":
						condition_string=condition_string+"message_from NOT LIKE '%"+condition['value'] +"%'"
					if condition['field']=="to" and condition['predicate']=="not_contains":
						condition_string=condition_string+"message_to NOT LIKE '%"+condition['value'] +"%'"
					if condition['field']=="subject" and condition['predicate']=="not_contains":
						condition_string=condition_string+"message_subject NOT LIKE '%"+condition['value'] +"%'"
					if condition['field']=="from" and condition['predicate']=="not_equals":
						condition_string=condition_string+"message_from != '"+condition['value'] +"' "
					if condition['field']=="to" and condition['predicate']=="not_equals":
						condition_string=condition_string+"message_to != '"+condition['value'] +"' "
					if condition['field']=="subject" and condition['predicate']=="not_equals":
						condition_string=condition_string+"message_subject != '"+condition['value'] +"' "

					if condition['field']=="date" and condition['predicate']=="less_than_days":
						condition_string=condition_string+"message_date >= date('now','-"+condition['value']+" day') "
					if condition['field']=="date" and condition['predicate']=="greater_than_days":
						condition_string=condition_string+"message_date < date('now','-"+condition['value']+" day') "
					if condition['field']=="date" and condition['predicate']=="less_than_months":
						condition_string=condition_string+"message_date >= date('now','-"+condition['value']+" month') "
					if condition['field']=="date" and condition['predicate']=="greater_than_months":
						condition_string=condition_string+"message_date < date('now','-"+condition['value']+" month') "

					if(rule['conditions'][-1]!=condition):
						condition_string=condition_string+" AND "
				query_string=query_string+condition_string
				cursor = conn.execute(query_string)
				for row in cursor:
					message_id_list.append(row[1])
				actions(service,rule['actions'],message_id_list)
				
			else:
				message_id_list=[]
				for condition in rule['conditions']:
					if condition['field']=="from" and condition['predicate']=="contains":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(message_from LIKE '%"+condition['value']+"%' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="to" and condition['predicate']=="contains":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(message_to LIKE '%"+condition['value']+"%' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="subject" and condition['predicate']=="contains":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(message_subject LIKE '%"+condition['value']+"%' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="from" and condition['predicate']=="equals":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(message_from = '"+condition['value']+"' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="to" and condition['predicate']=="equals":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(message_to = '"+condition['value']+"' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="subject" and condition['predicate']=="equals":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(message_subject = '"+condition['value']+"' );")
						for row in cursor:
							message_id_list.append(row[1])

					if condition['field']=="from" and condition['predicate']=="not_contains":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(NOT message_from LIKE '%"+condition['value']+"%' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="to" and condition['predicate']=="not_contains":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(NOT message_to LIKE '%"+condition['value']+"%' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="subject" and condition['predicate']=="not_contains":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(NOT message_subject LIKE '%"+condition['value']+"%' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="from" and condition['predicate']=="not_equals":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(NOT message_from != '"+condition['value']+"' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="to" and condition['predicate']=="not_equals":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(NOT message_to != '"+condition['value']+"' );")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="subject" and condition['predicate']=="not_equals":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE(NOT message_subject != '"+condition['value']+"' );")
						for row in cursor:
							message_id_list.append(row[1])

					if condition['field']=="date" and condition['predicate']=="less_than_days":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE message_date >= date('now','-"+condition['value']+" day') ")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="date" and condition['predicate']=="greater_than_days":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE message_date < date('now','-"+condition['value']+" day') ")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="date" and condition['predicate']=="less_than_months":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE message_date >= date('now','-"+condition['value']+" month') ")
						for row in cursor:
							message_id_list.append(row[1])
					if condition['field']=="date" and condition['predicate']=="greater_than_months":
						cursor = conn.execute("SELECT * from GMAIL_MESSAGES WHERE message_date < date('now','-"+condition['value']+" month') ")
						for row in cursor:
							message_id_list.append(row[1])
	conn.close()

if __name__ == "__main__":
	main()




