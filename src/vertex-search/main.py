from flask import Flask, jsonify, request
import google.auth
import google.auth.transport.requests
from firebase_admin import db, initialize_app
from firebase_functions import https_fn
from google.cloud import discoveryengine_v1beta

initialize_app()
app = Flask(__name__)

creds, project = google.auth.default()

auth_req = google.auth.transport.requests.Request()


datastore_id = "google-fi-basic-search_1697467372085"
project_id = "hospitality-demo-361210"
location = "global"
collection_id = "default_collection"
serving_config_id = "default_serving_config"
base_url = "https://discoveryengine.googleapis.com/v1beta"
serving_config = f"projects/{project_id}/locations/{location}/collections/{collection_id}/dataStores/{datastore_id}/servingConfigs/{serving_config_id}"
endpoint = f"{base_url}/{serving_config}:search"


@app.post("/search")
def search():
  data = request.get_json()
  print(data)
  query = data.get("query")
  num_results = data.get("num_results")

  client = discoveryengine_v1beta.SearchServiceClient()

  req = discoveryengine_v1beta.SearchRequest(
      serving_config=serving_config,
      query=query,
      page_size=num_results,
  )

  res = client.search(req)
  results = []
  for result in res.results:
    doc = result.document
    doc_dict = {}
    doc_dict['name'] = doc.name
    doc_dict['title'] = doc.derived_struct_data['title']
    doc_dict['link'] = doc.derived_struct_data['link']
    doc_dict['snippet'] = doc.derived_struct_data['snippets'][0]['snippet']
    results.append(doc_dict)

  data = {"results": results}

  return jsonify(data)

@https_fn.on_request()
def main(req: https_fn.Request) -> https_fn.Response:
  creds.refresh(auth_req)
  with app.request_context(req.environ):
    return app.full_dispatch_request()
