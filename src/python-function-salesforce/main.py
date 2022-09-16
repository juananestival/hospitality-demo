from simple_salesforce import Salesforce, SalesforceLogin
from simple_salesforce import SFType
from google.cloud import secretmanager
from flask import Flask
from flask import Response, request
import requests
import json
import os

def main(initial_request):

    sftype_object = os.environ["sftype_object"]

    try:
        # Get http request and parse it. 
        ver = os.environ.get('K_REVISION')
        print(f"Function version: {ver}")
        request_json = initial_request.get_json()
        print("main - print: {}".format(request_json))
    
        # Retrieve salesforce session and instance reference
        session_id, instance = sf_login()
        sf = Salesforce(instance=instance, session_id=session_id)
        
        # Get Tag
        tag = request_json['fulfillmentInfo']['tag']
        print(f"tag : {tag}")


        # Evaluate Tag
        if tag == 'phoneLookup':
            whatDoIHave = sf_phoneLookup(initial_request, sf)
            WebhookResponse=answer_webhook(whatDoIHave)
            return WebhookResponse
        
        elif tag == 'caseLookup':
            sf_case_id, sf_case_number, sf_case_subject, sf_case_description, sf_case_last_comment = get_sf_cases(initial_request, sf)
            #WebhookResponse=answer_webhook(sf_case_subject)
            # for multilanguage is not usable to send text via webhook
            message = " "
            #message = "We have found an open case: "
            WebhookResponse=answer_webhook_param(message, sf_case_id, sf_case_number, sf_case_subject, sf_case_description, sf_case_last_comment) 
            
            return WebhookResponse
            
        else:
            msg = 'Error'
            WebhookResponse=answer_webhook(msg)
            return WebhookResponse
            
    except:
        print("")


# Add your functions here
def get_sf_cases(initial_request, sf):
    
    cid, name, lastName = get_sf_contact_id(initial_request, sf)
    query_cases_string = "SELECT Id, CaseNumber, Description, LastComment__c, CreatedDate, Status, Subject, ContactId FROM Case Where ContactId = '{}' Order by CaseNumber DESC Limit 5".format(cid)
    print(query_cases_string)
    cases_by_contact = sf.query(query_cases_string)
    total_sf_records= cases_by_contact.get("totalSize")
    if total_sf_records == 1:
        print("One record returned")
        case_records = cases_by_contact.get("records")
        get_customer_record = case_records[0]

        sf_case_id = get_customer_record["Id"]
        sf_case_number = get_customer_record["CaseNumber"]
        sf_case_subject = get_customer_record["Subject"]
        sf_case_description = get_customer_record["Description"],
        sf_case_last_comment = get_customer_record["LastComment__c"]
        
        return sf_case_id, sf_case_number, sf_case_subject, sf_case_description, sf_case_last_comment 
    
    elif (total_sf_records > 1 ) and (total_sf_records <= 3):
        print("total cases {}".format(total_sf_records))
        case_records = cases_by_contact.get("records")
        print(type(case_records))
        get_customer_record = case_records[0]
        sf_case_subject = get_customer_record["Subject"]
        print(sf_case_subject)
        get_customer_record = case_records[1]
        sf_case_subject = get_customer_record["Subject"]
        print(sf_case_subject)
        
        for x in case_records:
            #get_customer_record = case_records[x]
            #sf_case_subject = get_customer_record["Subject"]
            print("hola")
            print(case_records[x]["Subject"])
        return "between 1 and 3"
    
    else:
        return "tbe implemented"
        
  

###############################################################################
def sf_phoneLookup(initial_request, sf):
    request_json = initial_request.get_json()
    param_customer_id = request_json['sessionInfo']['parameters']['customerid']
    query_string = "SELECT Id FROM Contact  WHERE Phone = '{}'".format(param_customer_id)
    
    try:
        sf_customer_id, last_name, first_name = get_sf_contact_id(initial_request,sf)
        #customers_by_phone = sf.query(query_string)
        #print("customers by phone {}".format(customers_by_phone))
        #total_records = customers_by_phone.get("totalSize")
        #if total_records == 1:
        #    print("one")
        #    customer_records = customers_by_phone.get("records")
        #    c_firstItem = customer_records[0]
        #    customer_id = c_firstItem["Id"]
        #    print (customer_id)
        #    contact_dict = sf.Contact.get(customer_id)
        #    print("Contact data {}".format(contact_dict))
            #for key, value in contact_dict.items():
            #    print(key, value)
            #last_name = contact_dict.get("LastName")
            #first_name = contact_dict.get("FirstName")
            #print("Last Name: {}".format(last_name))
            #print("First Name: {}".format(first_name))
            #query_cases_string = "SELECT Id, CaseNumber, CreatedDate, Status, Subject, ContactId FROM Case Where ContactId = '{}' Order by CaseNumber DESC Limit 5 '{}'".format(customer_id)
            #print(query_cases_string)
            #cases_by_contact = sf.query(query_cases_string)
            #print(cases_by_contact)   
        return first_name + " " + last_name
            
        #elif total_records == 0:
        #    print("zero")   
        #else:
        #    print("more")
        #returnMessage = "Just text"
        #return returnMessage
    except Exception as error:
        print("Phone Lookup error " + repr(error))    
        
###############################################################################
def answer_webhook_param(message, sf_case_id, sf_case_number, sf_case_subject, sf_case_description, sf_case_last_comment):
    message_resp = {
        "session_info": {
            "parameters" : {
                "caseid":sf_case_id,
                "casenumber":sf_case_number,
                "casesubject":sf_case_subject,
                "casedescription":sf_case_description,
                "caselastcomment":sf_case_last_comment
            }    
        },
        "fulfillment_response": {
            "messages": [
                {   
                    "text": {
                        "text": [message]
                    }
                }
            ]
        }
    }
    return Response(json.dumps(message_resp), 200)
    #return Response(json.dumps(message), 200, mimetype='application/json')
###############################################################################
def answer_webhook(msg):
    message= { "fulfillment_response": {
        "messages": [
            {   
                "text": {
                    "text": [msg]
                }
            }
      ]
    }
    }
    return Response(json.dumps(message), 200)
    #return Response(json.dumps(message), 200, mimetype='application/json')

###############################################################################
def get_sf_contact_id(initial_request, sf):
    request_json = initial_request.get_json()
    channel = request_json['sessionInfo']['parameters']['channel']
    documentId = ""
    if channel == "voice":
        print("this is a voice Call")
        if request_json['payload']:
            documentId = request_json['payload']['telephony']['caller_id']
            print(documentId)
    else:
        print("this is a text interaction")
        documentId = request_json['sessionInfo']['parameters']['customerid']
        print(documentId)

    param_customer_id = documentId
    query_string = "SELECT Id FROM Contact  WHERE Phone = '{}'".format(param_customer_id)
    print(query_string)
    
    try:
        get_sf_customers_by_phone = sf.query(query_string)
        total_sf_records = get_sf_customers_by_phone.get("totalSize")
        
        if total_sf_records == 1:
            print("One record returned")
            customer_records = get_sf_customers_by_phone.get("records")
            get_customer_record = customer_records[0]
            sf_customer_id = get_customer_record["Id"]
            print ("Salesforce Id: {}".format(sf_customer_id))
            sf_contact_dict = sf.Contact.get(sf_customer_id)
            print("Contact data {}".format(sf_contact_dict))
            #for key, value in contact_dict.items():
            #    print(key, value)
            last_name = sf_contact_dict.get("LastName")
            first_name = sf_contact_dict.get("FirstName")
            cid = sf_contact_dict.get("Id")
            print("First Name: {}".format(first_name) + "Last Name: {}".format(last_name) +"CID: {}".format(cid))
       

            return cid, last_name, first_name
            
        elif total_sf_records == 0:
            print("Zero records returned")   
            sf_customer_id = "none"
            return sf_customer_id
        else:
            print("More than one record match the query")
            sf_customer_id = "multiple"
            return sf_customer_id
        
    except Exception as error:
        print("Phone Lookup error " + repr(error))    
    
###############################################################################
def sf_login():
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    # Organize the Secret Keys
    sf_user_prod = "SF_USER_PROD"
    sf_pass_prod = "SF_PASS_PROD"
    sf_token_prod = "SF_TOKEN_PROD"
    
    # Pass in the GCP Project ID
    # This will be found on the Secret Manager > Secret > Secret Details
    # projects/[gcp_project_id]/secrets/[secret]
    project_id = os.environ["gcp_project_id"]
    
    # Obtain the Secret Name Path
    sf_user_prod_name = f"projects/{project_id}/secrets/{sf_user_prod}/versions/latest"
    sf_pass_prod_name = f"projects/{project_id}/secrets/{sf_pass_prod}/versions/latest"
    sf_token_prod_name = f"projects/{project_id}/secrets/{sf_token_prod}/versions/latest"   
    
    # Obtain the Latest Secret Version
    sf_user_prod_response = client.access_secret_version(sf_user_prod_name)
    sf_pass_prod_response = client.access_secret_version(sf_pass_prod_name)
    sf_token_prod_response = client.access_secret_version(sf_token_prod_name)

    # Parse the Secret Response & Decode Payload
    sf_user_prod_secret = sf_user_prod_response.payload.data.decode('UTF-8')  
    sf_pass_prod_secret = sf_pass_prod_response.payload.data.decode('UTF-8') 
    sf_token_prod_secret = sf_token_prod_response.payload.data.decode('UTF-8')     

    # Assign Variables to Pass into Salesforce Login
    sf_username = sf_user_prod_secret
    sf_password = sf_pass_prod_secret
    sf_token = sf_token_prod_secret
 
    try:
        # call salesforce Login
        # return Session ID and Instance
        session_id, instance = SalesforceLogin(
            username = sf_username,
            password = sf_password,
            security_token = sf_token
            )
        
  
        
 
        
      
       

        return session_id, instance
    
 

    except Exception as error:
        
        print('Login Error: ' + repr(error)) 