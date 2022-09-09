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
        else:
            print("Else: ")
            
        msg = 'hola'
        WebhookResponse=answer_webhook(msg)
        return WebhookResponse
    except:
        print("")


# Add your functions here

###############################################################################
def sf_phoneLookup(initial_request, sf):
    request_json = initial_request.get_json()
    param_customer_id = request_json['sessionInfo']['parameters']['customerid']
    query_string = "SELECT Id FROM Contact  WHERE Phone = '{}'".format(param_customer_id)
    print(query_string)
    
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
    param_customer_id = request_json['sessionInfo']['parameters']['customerid']
    query_string = "SELECT Id FROM Contact  WHERE Phone = '{}'".format(param_customer_id)
    print(query_string)
    
    try:
        get_sf_customers_by_phone = sf.query(query_string)
        print("SFDC Customers by phone {}".format(get_sf_customers_by_phone ))
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
            print("Last Name: {}".format(last_name))
            print("First Name: {}".format(first_name))
            return sf_customer_id, last_name, first_name
            
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
    

    sf_contact_id = ""
    return sf_contact_id
    print("to implement")



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