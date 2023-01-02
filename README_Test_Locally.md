on the node cf

1. install the dev framework
```sh
npm install --save-dev @google-cloud/functions-framework
```

2. Execute
```sh
npx functions-framework --target=index --port=4444 
```


3. local

```sh
curl -m 3010 -X POST http://localhost:4444 \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
    "model": "default",
    "gcsUri":"gs://stt-demos/audio-files/caixabank/A0001_S003_0_G0001_G0002.wav",
    "encoding":"WAV",
    "sampleRateHertz":16000,
    "languageCode":"es-ES",
    "topic":"projects/hospitality-demo-361210/topics/dfcxtopic",
    "message":"hey"
}'
```
4. REMOTE

```sh
curl -m 3010 -X POST https://v2-stt-recognize-czhewlm65q-uc.a.run.app \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
    "model": "default",
    "gcsUri":"gs://stt-demos/audio-files/caixabank/A0001_S003_0_G0001_G0002.wav",
    "encoding":"WAV",
    "sampleRateHertz":16000,
    "languageCode":"es-ES",
    "topic":"projects/hospitality-demo-361210/topics/dfcxtopic",
    "message":"hey"
}'
```