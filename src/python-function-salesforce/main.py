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
        # Get Tag
        tag = request_json['fulfillmentInfo']['tag']
        print(f"tag : {tag}")
        customer_id = request_json['sessionInfo']['parameters']['customerid']
        print(f"customer {customer_id}")

        # Evaluate Tag
        if tag == 'phoneLookup':
            print(f"Tag flow for: {tag}")
            whatDoIHave = sf_phoneLookup(initial_request)
            print(f'Answer from phonelookup {whatDoIHave}')

        else:
            print("Else: ")

        # Check sf_request
        tag = request_json['fulfillmentInfo']['tag']
        msg = 'hola'
        WebhookResponse=answer_webhook(msg)
        return WebhookResponse
    except:
        print("")


# Add your functions here

###############################################################################
def sf_phoneLookup(initial_request):
    try:
        request_json = initial_request.get_json()
        customer_id = request_json['sessionInfo']['session']['parameters']['customerid']
        print(f"customer {customer_id}")
        returnMessage = "Just text"
        return returnMessage
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
def sf_login():
    print("control -1")
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    print("control -2")
    # Organize the Secret Keys
    sf_user_prod = "SF_USER_PROD"
    sf_pass_prod = "SF_PASS_PROD"
    sf_token_prod = "SF_TOKEN_PROD"
    
    # Pass in the GCP Project ID
    # This will be found on the Secret Manager > Secret > Secret Details
    # projects/[gcp_project_id]/secrets/[secret]
    print("control -3")
    project_id = os.environ["gcp_project_id"]
    
    # Obtain the Secret Name Path
    print("control -4")
    sf_user_prod_name = f"projects/{project_id}/secrets/{sf_user_prod}/versions/latest"
    sf_pass_prod_name = f"projects/{project_id}/secrets/{sf_pass_prod}/versions/latest"
    sf_token_prod_name = f"projects/{project_id}/secrets/{sf_token_prod}/versions/latest"   
    
    # Obtain the Latest Secret Version
    print("control -5")
    sf_user_prod_response = client.access_secret_version(sf_user_prod_name)
    sf_pass_prod_response = client.access_secret_version(sf_pass_prod_name)
    sf_token_prod_response = client.access_secret_version(sf_token_prod_name)

    # Parse the Secret Response & Decode Payload
    print("control -6")
    sf_user_prod_secret = sf_user_prod_response.payload.data.decode('UTF-8')  
    sf_pass_prod_secret = sf_pass_prod_response.payload.data.decode('UTF-8') 
    sf_token_prod_secret = sf_token_prod_response.payload.data.decode('UTF-8')     

    # Assign Variables to Pass into Salesforce Login
    print("control -7")
    sf_username = sf_user_prod_secret
    sf_password = sf_pass_prod_secret
    sf_token = sf_token_prod_secret
 
    try:
        print("control 1")
        # call salesforce Login
        # return Session ID and Instance
        session_id, instance = SalesforceLogin(
            username = sf_username,
            password = sf_password,
            security_token = sf_token
            )
        # c_id = instance.query("SELECT Id FROM Contact WHERE LastName = 'Next201'")
        print ("session id")
        print (session_id)
        
        print ("instance id")
        print (instance)
        
        sf = Salesforce(instance=instance, session_id=session_id)
        c_id = sf.query("SELECT Id FROM Contact WHERE Phone = '+34664004600'")
        print(c_id)
        print("control 2")

        return session_id, instance
    
 

    except Exception as error:
        
        print('Login Error: ' + repr(error)) 