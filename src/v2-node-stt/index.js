/*****************************************************************************/
// DEFINITION SECTION
/*****************************************************************************/
const PROJECTID = "hospitality-demo-361210";
const speech = require('@google-cloud/speech');
//const {PubSub} = require('@google-cloud/pubsub');
//const pubsub = new PubSub();
const {Storage} = require('@google-cloud/storage')
var createHTML = require('create-html')

// Declare your endpoint
const endPoint = 'speech.googleapis.com';

// Creates a client
const client = new speech.SpeechClient({apiEndpoint: endPoint});

function replaceAll(string, search, replace) {
  return string.split(search).join(replace);
}

/*****************************************************************************/
// MAIN SECTION
/*****************************************************************************/
exports.index = (req, res) => {

  // Log some parameters
  console.log(`Function version: ${process.env.K_REVISION}`);
  console.log(`Body Log: ${JSON.stringify(req.body)}`)

  

  //let test = process.env.ddd;


  if (
    !(req.body.hasOwnProperty("model") &&
    req.body.hasOwnProperty("gcsUri") &&
    req.body.hasOwnProperty("encoding") &&
    req.body.hasOwnProperty("sampleRateHertz") &&
    req.body.hasOwnProperty("languageCode"))
    
    ) {
      console.log('Missing Parameter')
      return res.status(400).send({
        sessionInfo: {
          message: {
            status: "Fail",
            description: "Missing Parameter"
          },
        },
      });
  }
  let model = req.body.model;
  let gcsUri = req.body.gcsUri;
  let encoding = req.body.encoding;
  let sampleRateHertz = req.body.sampleRateHertz;
  let languageCode = req.body.languageCode;

  if (
    (req.body.hasOwnProperty("confidenceThreshold") &&
    req.body.hasOwnProperty("enableWordLevelConfidence")&&(enableWordLevelConfidence==true))
    
    ) {
      console.log('Word Confidence Translation Enabled')
      
      msg = asyncRecognizeGCSWords(
        model,
        gcsUri,
        encoding,
        sampleRateHertz,
        languageCode,
      )

    } else {
      console.log('Word Confidence Translation Disabled' )
      msg = asyncRecognize(
        model,
        gcsUri,
        encoding,
        sampleRateHertz,
        languageCode
      )

    }
    /*
  asyncRecognizeGCSWords

  
  msg = asyncRecognize(
    model,
    gcsUri,
    encoding,
    sampleRateHertz,
    languageCode
  )
  */
  
  
  return res.status(200).send({
    sessionInfo: {
      message: {
        status: "Success",
        description: "The Transcription has started. This can take some minutes."
      },
    },
  });
  

};

/*****************************************************************************/
// FUNCTIONS SECTION
/*****************************************************************************/



// Function asyncRecognize Init

async function asyncRecognize(
  model,
  gcsUri,
  encoding,
  sampleRateHertz,
  languageCode
) {

  console.log('Starting long runing from GCS audio file custom')
  //const speech = require('@google-cloud/speech');
  //const client = new speech.SpeechClient();

  const diarizationConfig = {
    enableSpeakerDiarization: true,
    maxSpeakerCount: 2,
  };
  const phraseSets = {
    phraseSets: [
        {
            name: "projects/878087147798/locations/global/phraseSets/pukps"
        }
    ]
  };

  const config = {
    model: model,
    encoding: encoding,
    sampleRateHertz: sampleRateHertz,
    languageCode: languageCode
  };

  const audio = {
    uri: gcsUri,
  };

  const request = {
    config: config,
    audio: audio,
  };


  const [operation] = await client.longRunningRecognize(request);
  const [response] = await operation.promise();
  console.log(`The length of results in response is ${response.results.length}`)

  const transcription2 = response.results
    .map((result, index) => ('<br>' + index + '--> ' +result.alternatives[0].transcript + '<br>' ))
    .join('\n\n')
    //console.log(`Transcription: ${transcription2}`);
    console.log(`Transcription for model: ${config.model} confidence is: ${response.results[0].alternatives[0].confidence}`)
  
  const msg = {
    sessionInfo: {
      message: {
        status: "Success",
        description: transcription2
      },
    },
  }
  const sourceFile = gcsUri.split('/').pop().split('.')[0]
  const fileNameToWrite = `${sourceFile}-${model}-${encoding}-${sampleRateHertz}-${languageCode}-`
  
  uploadFromMemory(transcription2, fileNameToWrite).catch(console.error);  
  //asyncPubTranscription(req, msg) 
}

async function asyncRecognizeGCSWords(
  model,
  gcsUri,
  encoding,
  sampleRateHertz,
  languageCode
  
) {
  const speech = require('@google-cloud/speech');

  // Creates a client
  const client = new speech.SpeechClient();

  const config = {
    enableWordTimeOffsets: true,
    encoding: encoding,
    sampleRateHertz: sampleRateHertz,
    languageCode: languageCode,
    enableWordConfidence: true
  };

  const audio = {
    uri: gcsUri,
  };
  

  const request = {
    config: config,
    audio: audio,
  };

  const [operation] = await client.longRunningRecognize(request);

  // Get a Promise representation of the final result of the job
  const [response] = await operation.promise()
  let fullText = ''
  response.results.forEach(result => {
    fullText = "<br>" + fullText + "<br>" 
    //console.log(`Transcription: ${result.alternatives[0].transcript}`);

    result.alternatives[0].words.forEach(wordInfo => {
      const startSecs =
        `${wordInfo.startTime.seconds}` +
        '.' +
        wordInfo.startTime.nanos / 100000000;
      const endSecs =
        `${wordInfo.endTime.seconds}` +
        '.' +
        wordInfo.endTime.nanos / 100000000;
      const wordConfidence = 
        `${wordInfo.confidence}`
      
              fullText = fullText + `<span style="color:${wordInfo.confidence > 0.8? 'green' : 'red'}" title="${wordInfo.confidence}">${wordInfo.word} </span>`
      
      
    });
    //const sourceFile = gcsUri.split('/').pop().split('.')[0]
    //const fileNameToWrite = `${sourceFile}-${model}-${encoding}-${sampleRateHertz}-${languageCode}-`
  
      //uploadFromMemory(fullText, fileNameToWrite).catch(console.error);  
    //console.log (fullText)
  });
  const sourceFile = gcsUri.split('/').pop().split('.')[0]
  const fileNameToWrite = `${sourceFile}-${model}-${encoding}-${sampleRateHertz}-${languageCode}-`
  console.log('now outside of the loop')
  console.log(`outside transcription ${fullText}`)
  uploadFromMemory(fullText, fileNameToWrite).catch(console.error); 
  // [END speech_transcribe_async_word_time_offsets_gcs]
}

async function uploadFromMemory(text, fileNameToWrite) {
  console.log('uploading to a file...')
  const options = {
    resumable: false,
    timeout:300
    //contentType: 'application/json'
  };

  const storage = new Storage();
  const bucketName = 'stt-demos'
  const destFileName = `transcripts/from-cloud-function/${fileNameToWrite}${Date.now()}.html`;
  var html = createHTML({
    title: 'Transcription Results',
    head: '<meta name="description" content="Transcription Results">',
    body: `<p><b>${text}</b></p>`,

  })
  await storage.bucket(bucketName).file(destFileName).createWriteStream(html, options);
  //await storage.bucket(bucketName).file(destFileName).save(html, options);
  console.log('uploading after await createWriteStream')
  await storage.bucket(bucketName).file(destFileName).save(html, options);
  console.log('uploading after await save')

  console.log(
    `${destFileName} with contents ${html} uploaded to ${bucketName}.`
  );
}
