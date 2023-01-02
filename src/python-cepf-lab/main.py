from flask import Flask
from flask import Response, request
import requests
import json
import os
import sqlalchemy
import time

### Global Variables
db_name = "retail"
db_user = "postgres"
#db_password = "Al0h0m0ra!"
db_password = "1sh7harGat3!"
connection_name = "hospitality-demo-361210:us-central1:dfcxlabs"
driver_name = 'postgresql+pg8000'
query_string = dict({"unix_sock": "/cloudsql/{}/.s.PGSQL.5432".format(connection_name)})
#---------------#

def main(initial_request):
        
    request_json = initial_request.get_json()
    tag = request_json['fulfillmentInfo']['tag']
    ver = os.environ.get('K_REVISION')
    print(f"Python Function version: {ver}")
    print("main - print: {}".format(request_json))
    
    # Evaluate webhook tag
    print(f'Tag called: {tag}')
    if tag == 'validate-pin':
        msg, params = db_validate_pin(initial_request)
    elif tag == 'update-order':    
        msg, params = update_orders(initial_request)
    elif tag == 'empty-orders-table':
        msg, params = empty_orders_table()
    else:
        msg = "Unknown tag"
        params = {}
        
    # Setup and send Response back to Dialogflow CX   
    WebhookResponse=answer_webhook(msg, params)
    return WebhookResponse

#---------------#
def answer_webhook(msg, params):

    print (f'Params length is : {len(params)}')
    message =  {
        "session_info": {
            "parameters" : {
                "wh_execution_time":time.time()
            }    
        },
        "fulfillment_response": {
            "messages": [
                {   
                    "text": {
                        "text": [msg]
                    }
                }
            ]
        }
    }
    if (len(params) > 0):
        for k, v in params.items():
            message["session_info"]["parameters"][k]=v            
    return Response(json.dumps(message), 200)

#---------------#
def db_validate_pin(req):
    
    request_json = req.get_json()
    if not (request_json.get("sessionInfo").get("parameters").get("pin_number")):
        params = {}
        return "no pin provided", params
    typed_pin_param = request_json['sessionInfo']['parameters']['pin_number']
    # The param is received like a list. Let's extract the value
    typed_pin = typed_pin_param[0]
    table_name = "customers"
    stmt1 = sqlalchemy.text(f'select customerPIN from {table_name}')
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            query=query_string,
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800
    )
    try:
        with db.connect() as conn:
            params = {}
            result = conn.execute(stmt1).fetchone()
            stored_pin = result[0]
            
            if (str(stored_pin) == str(typed_pin)):
                params = {
                    "pin_match":True
                }
                msg = "Your pin match with our records"
            else:
                params = {
                    "pin_match":False
                }
                msg = "Your pin does not match with our records"
            #return (f'Validating PIN ...', params)
            return (msg, params)
            
    except Exception as e:
        return 'Error: {}'.format(str(e))
    
def update_orders(req):
    print ('Updating shoping cart...')
    request_json = req.get_json()
    if not (request_json.get("sessionInfo").get("parameters").get("cart")):
        params = {}
        return "no pin provided", params
    table_name = "orders"
    cart_param = request_json['sessionInfo']['parameters']['cart']
    # The param is received like a list. Let's extract the value
    productName = cart_param[0]
    print (f'product {productName}')
    print (f'cart {cart_param}')
    customerPhone = "+1555", 
    quantity = 1
    stmt1 = sqlalchemy.text(f'insert into {table_name} (productName, customerPhone, quantity) values (\'{cart_param }\', \'+1-555-555-555\', {quantity})')

    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            query=query_string,
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800
    )
    try:
        with db.connect() as conn:
            params = {}
            print('before update')
            print(stmt1)
            conn.execute(stmt1)
            params = {"db_instert":"ok"}
            return "updated", params
            
    except Exception as e:
        return 'Error: {}'.format(str(e))

def empty_orders_table():
    table_name = "orders"

    stmt1 = sqlalchemy.text('delete from {}'.format(table_name))
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            query=query_string,
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800
    )
    try:
        with db.connect() as conn:
            params = {}
            print('before delete')
            print(stmt1)
            results = conn.execute(stmt1)
            for result in results:
                print(result)
            print('after execute')
            params = {"table_empty":"true"}
            return "deleted", params
            
    except Exception as e:
        return 'Error: {}'.format(str(e))

    