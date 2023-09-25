import json
import sqlalchemy
from google.cloud import secretmanager
import os

def verify_pin(request):
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
    pin = int(request_json.get('pageInfo',{}).get('formInfo',{}).get('parameterInfo',[{}])[0].get('value',-1))
    session_parameters = request_json.get('sessionInfo',{}).get('parameters',{})
    #account_id = next((session_parameters[parameter] for parameter in session_parameters.keys() if parameter == 'account_id'),-1)
    account_id = None
    #print(f'the session account_id is  is {account_id}')
    should_enroll_speaker_id = True
    print(f'the pin gathered is  is {pin}')


    #if not account_id and phone_number:
    if not account_id:
        with db.connect() as conn:
            account_ids = conn.execute(
                "SELECT account_id FROM phone WHERE phone_number = '{}'".format(phone_number)).fetchall()

        account_id = None
        print(f'the list of accounts {account_ids}')

        for row in account_ids:
            account_id = row[0]
            print(f'the  account {account_id}')
        should_enroll_speaker_id = True

    if not account_id:
        raise ValueError(f"No account found for phone number {phone_number}")

    with db.connect() as conn:
        pins = conn.execute(
            'SELECT pin from account where id = {}'.format(account_id)).fetchall()

    expected_pin = None
    for row in pins:
      expected_pin = row[0]
      print(f'the expected_pin  {expected_pin} the pin gathered is  is {pin}' )

    response_json = json.dumps({
        'sessionInfo': {
            'parameters': {
                'userAuthenticated': pin == expected_pin,
                'shouldEnrollSpeakerId': should_enroll_speaker_id
            }
        }
    })
    return response_json