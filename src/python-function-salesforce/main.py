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

        request_json = initial_request.get_json()
        print("main - print: {}".format(request_json))
    
        #retrieve salesforce session and instance reference
        session_id, instance = sf_login()
        tag = request_json['fulfillmentInfo']['tag']
        print("tag : {}".format(tag))
        print(tag)

        if tag == 'phoneLookup':
            print("Tag flow for: {tag}")
        else:
            print("Else: ")




        # Check sf_request
        tag = request_json['fulfillmentInfo']['tag']


        msg = 'hola'
        WebhookResponse=answer_webhook(msg)
        return WebhookResponse

     
        """
        record = SFType(sftype_object,session_id,instance)

        #send payload to Salesforce API
        record.create(request_json)

        #parse response from Salesforce API
        record_submit = record.describe()

        print("main - record_submit: {}".format(record_submit))

        return "Main Request Passed"
        """

    except Exception as error:

        print('Main Error: ' + repr(error))    

def answer_webhook(msg):
    message= {"fulfillment_response": {
      
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
    sf_instance_url='contactcenter-dev-ed.my.salesforce.com'
 
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