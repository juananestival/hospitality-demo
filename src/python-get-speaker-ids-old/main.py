import json
import sqlalchemy
from google.cloud import secretmanager
import os

def get_speaker_ids(request):
    initial_requst = request.get_json()
    print(initial_requst)
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # Get the version of the CF for proper
    ver = os.environ.get('K_REVISION')
    print(f"Python Function version: {ver}")
          
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    request_json = request.get_json()
    client = secretmanager.SecretManagerServiceClient()
    
    # The String below is the secret name to be configured in Secret Manager
    db_user_prod = "DB_USER_PROD"
    db_pass_prod = "DB_PASS_PROD"
    project_id = os.environ["gcp_project_id"]
    
    # Obtain the Secret Name Path
    db_user_prod_name = f"projects/{project_id}/secrets/{db_user_prod}/versions/latest"
    db_pass_prod_name = f"projects/{project_id}/secrets/{db_pass_prod}/versions/latest"
    
    # Obtain the Latest Secret Version
    db_user_prod_response = client.access_secret_version(db_user_prod_name)
    db_pass_prod_response = client.access_secret_version(db_pass_prod_name )
    
        # Parse the Secret Response & Decode Payload
    user_prod_secret = db_user_prod_response.payload.data.decode('UTF-8')  
    pass_prod_secret = db_pass_prod_response.payload.data.decode('UTF-8') 


    # You may need to edit the following line if you are not using the
    # Dialogflow CX Phone Gateway. It may be helpful to uncomment the following:
    # print(request_json)
    # Using the printed JSON, look for the phone number provided by the
    # phone gateway and fetch it from the dictionary below.
    #if request_json['payload']:
    #    if request_json['payload']['telephony']:
    #        phone_number = request_json.get['payload']['telephony']['caller_id']
    db_user = user_prod_secret
    db_pass = pass_prod_secret
    db_name = 'postgres'
    db_socket_dir = '/cloudsql'
    cloud_sql_connection_name = 'hospitality-demo-361210:us-central1:dfcxlabs'
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername='postgresql+pg8000',
            username=db_user,
            password=db_pass,
            database=db_name,
            query={
                'unix_sock': '{}/{}/.s.PGSQL.5432'.format(
                    db_socket_dir,
                    cloud_sql_connection_name)
            }
        ),
    )
    phone_number = request_json.get('payload',{}).get('telephony',{}).get('caller_id')
    print(f'the ANI of the phone number is {phone_number}')

    with db.connect() as conn:
        account = conn.execute(
            "SELECT account_id FROM account JOIN phone ON phone.account_id = account.id WHERE phone_number = '{}'".format(phone_number)).fetchall()
            #"SELECT account_id, account_name, first_name, last_name, gender FROM account JOIN phone ON phone.account_id = account.id WHERE phone_number = '{}'".format(phone_number)).fetchall()
        print(f'the account is {account}')
            
    account_id = None
    for row in account:
        account_id = row[0]
        #account_name = row[1]
        #first_name = row[2]
        #last_name = row[3]
        #gender = row[4]
    print(f'the account id is {account_id}')
    if not account_id:
        print("No account found for phone number:", phone_number)
        return '{}'

    with db.connect() as conn:
        speaker_ids = conn.execute(
            "SELECT gcp_resource_name FROM speaker_id WHERE account_id = '{}'".format(account_id)).fetchall()

    speaker_ids = [row[0] for row in speaker_ids]

    if len(speaker_ids) > 0:
        print("Speaker ID found")
        response_json = json.dumps({
            'sessionInfo': {
                'parameters': {
                    'speaker-ids': speaker_ids,
                    'account-name': 'account_name',
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'gender': 'gender'
                }
            }
        })
    else:
        print("No speaker IDs associated with phone number:", phone_number, "Account:", account_id)
        response_json = json.dumps({
            'sessionInfo': {
                'parameters': {
                    #'account-name': 'account_name',
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'gender': 'gender'
                }
            }
        })
    return response_json