# hospitality-demo

```sh
terraform apply -target=module.python_function_main --auto-approve
terraform apply -target=module.node_function_main --auto-approve
terraform apply -target=module.node_main_feature_testing --auto-approve
terraform apply -target=module.python-cepf-lab --auto-approve
terraform apply -target=module.v2-node-stt --auto-approve
```

Python env creation
```sh
python3 -m venv venv
```

Python env activation
```sh
source venv/bin/activate
```
Python env installation
```sh
pip install functions-framework
```

pip install -r requirements.txt


https://pypi.org/project/simple-salesforce/

Note if you copy past the number in Dialog Flow console then a unicode character si addad 202 for the copy paste and the query don'tm work

## Created localtesting to test the python functions before upload them
I'll create a branch called localtesting

## The functions are created in the project.
this means that it should be accesible from any agent. 
 to add a new node funciton
 ```tf
 module "node_function_main" {
  source               = "./modules/functions"
  project              = var.project
  function_name        = "a-name"
  function_entry_point = "the value of the exports.hospitalityMainWH = (req, res) => {"
  sourcefn             = "the directory"
  runtimefn              = "nodejs16"
}
```


```sh
curl -m 3010 -X POST https://v2-stt-recognize-czhewlm65q-uc.a.run.app \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
    "model": "latest_long",
    "gcsUri":"gs://stt-demos/audio-files/spanish-dataset/Spanish_Conversational_Speech_Corpus/WAV/A0001_S004_0_G0001_G0002.wav",
    "encoding":"WAV",
    "sampleRateHertz":16000,
    "languageCode":"es-ES",
    "topic":"projects/hospitality-demo-361210/topics/dfcxtopic",
    "message":"Future Pubsub Integration",
    "confidenceThreshold":"0.7",
    "enableWordLevelConfidence":true
}'
```

