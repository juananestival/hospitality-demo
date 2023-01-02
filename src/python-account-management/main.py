import json
import sqlalchemy
from google.cloud import secretmanager
import os

def create_account(db, parameters):
    print("create account")
    account = {k.replace("account_",""):v for k,v in parameters.items() if k.startswith('account_')}
    if not {'first_name','last_name','pin','gender', 'preferred_language'} <= account.keys():
        raise ValueError("Not all parameters provided")
    with db.connect() as conn:
        account_id = conn.execute(f"INSERT INTO account (account_name, first_name, last_name, pin, gender, preferred_language) VALUES ('{account['gender']} {account['last_name']}', '{account['first_name']}', '{account['last_name']}', {account['pin']}, '{account['gender']}', '{account['preferred_language']}') RETURNING id").scalar()
    print(account_id)
    parameters['account_id'] = account_id
    return parameters

def get_account_by_name(db, parameters):
    print("get account by name")
    account = {k.replace("account_",""):v for k,v in parameters.items() if k.startswith('account_')}
    if not {'first_name','last_name'} <= account.keys():
        raise ValueError("Not all parameters provided")
    with db.connect() as conn:
        rows = conn.execute(f"SELECT * FROM account WHERE first_name = '{account['first_name']}' AND last_name = '{account['last_name']}' LIMIT 1").fetchall()
    account = dict(rows[0]._mapping)
    parameters = {"account_" + k:v for k,v in account.items() if not(k.startswith('account_'))}
    return parameters

def get_account_by_id(db, parameters):
    print("get account by name")
    if not {'account_id'} <= parameters.keys():
        raise ValueError("Not all parameters provided")
    parameters['account_id'] = str(parameters['account_id']).replace(" ","").replace("-","")
    with db.connect() as conn:
        rows = conn.execute(f"SELECT * FROM account WHERE id = '{parameters['account_id']}' LIMIT 1").fetchall()
    account = dict(rows[0]._mapping)
    parameters = {"account_" + k:v for k,v in account.items() if not(k.startswith('account_'))}
    return parameters

def add_phone_number(db, parameters):
    print("add phone number")
    if not {'account_id','account_phone_number'} <= parameters.keys():
        raise ValueError("Not all parameters provided")
    with db.connect() as conn:
        rows = conn.execute(f"INSERT INTO phone (account_id, phone_number) VALUES ({parameters['account_id']}, '{parameters['account_phone_number']}')")
    return {}

def delete_speaker_ids(db, parameters):
    print("delete speaker IDs")
    if not {'account_id'} <= parameters.keys():
        raise ValueError("Not all parameters provided")
    with db.connect() as conn:
        rows = conn.execute(f"DELETE FROM speaker_id WHERE account_id = {parameters['account_id']}")
    return {}

def account_management(request):
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
    tag = ''
    parameters = {}

    if 'fulfillmentInfo' in request_json and request_json['fulfillmentInfo']:
        if 'tag' in request_json['fulfillmentInfo'] and request_json['fulfillmentInfo']['tag']:
            tag = request_json['fulfillmentInfo']['tag']
    if 'sessionInfo' in request_json and request_json['sessionInfo']:
        parameters = request_json['sessionInfo']['parameters']

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

    if 'account_id' in parameters and parameters['account_id']:
        parameters['account_id'] = int(parameters['account_id'])

    print(f"Tag: {tag}")
    print(f"Parameters: {parameters}")
    
    match tag:
      case 'create account':
        parameters |= create_account(db, parameters)
      case 'get account by name':
        parameters |= get_account_by_name(db, parameters)
      case 'get account by id':
        parameters |= get_account_by_id(db, parameters)
      case 'add phone number':
        parameters |= add_phone_number(db, parameters)
      case 'delete speaker IDs':
        parameters |= delete_speaker_ids(db, parameters)
        
    session_info = {'parameters': parameters}
    response = {'sessionInfo': session_info}
    response_json = json.dumps(response)
    print(f"Response JSON: {response_json}")
    
    return response_json