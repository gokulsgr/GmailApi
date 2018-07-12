# GmailApi

Version 
Python 3.5.3


User should get the authentication (credentials.json) file by following  the [Gmail API link](https://developers.google.com/gmail/api/quickstart/python)
Also, client_secret.json should be saved in the same directory as this file

For loading the mails to the Sqlite DB

    python db_loader.py 
    
For parsing the rules.json and perform the actions
    
    python rule_parser.py
    
# Json file conventions:

* Fields - "from" , "to" , "subject" , "date"
* Predicate - "contains" , "not_contains" , "equals" ,"not_equals" ,"less_than_months" ,"less_than_days" , "greater_than_days" , "greater_than_months"
* actions - "mark_as_read" , "add_label" , "archive" , "mark_as_unread"
* overall_predicate - "any" ,"all"






