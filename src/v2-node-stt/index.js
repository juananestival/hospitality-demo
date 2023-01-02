/*****************************************************************************/
// DEFINITION SECTION
/*****************************************************************************/
const PROJECTID = "hospitality-demo-361210";
const speech = require('@google-cloud/speech');
//const {PubSub} = require('@google-cloud/pubsub');
//const pubsub = new PubSub();
const {Storage} = require('@google-cloud/storage');
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

  let model = req.body.model;
  let gcsUri = req.body.gcsUri;
  let encoding = req.body.encoding;
  let sampleRateHertz = req.body.sampleRateHertz;
  let languageCode = req.body.languageCode;

  let test = process.env.ddd;


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
  /*
  if (!req.body.topic || !req.body.message) {
    res
      .status(400)
      .send(
        'Missing parameter(s); include "topic" and "message" properties in your request.'
      );
    return;
  }

  msg="test"
  asyncPubTranscription(req, msg) 


  console.log(`Recognition request received with ${model} ${gcsUri} ${encoding} ${sampleRateHertz} ${languageCode}`)
  */
  
  msg = asyncRecognize(
    model,
    gcsUri,
    encoding,
    sampleRateHertz,
    languageCode
  )
  
  
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
    console.log(`Transcription: ${transcription2}`);
    console.log(`Transcription for model: ${config.model} confidence is: ${response.results[0].alternatives[0].confidence}`)
  
  const msg = {
    sessionInfo: {
      message: {
        status: "Success",
        description: transcription2
      },
    },
  }
  uploadFromMemory(transcription2).catch(console.error);  
  //asyncPubTranscription(req, msg) 
}
async function uploadFromMemory(text) {
  const storage = new Storage();
  const bucketName = 'stt-demos'
  const destFileName = `transcripts/from-cloud-function/just-testing-2${Date.now()}.html`;
  var html = createHTML({
    title: 'example',
    head: '<meta name="description" content="example">',
    body: `<p><b>${text}</b></p>`,

  })
  await storage.bucket(bucketName).file(destFileName).save(html);

  console.log(
    `${destFileName} with contents ${html} uploaded to ${bucketName}.`
  );
}
// Function asyncRecognize End


// Function asyncPubTranscription Init
/*
async function asyncPubTranscription(req, msg) {

  // References an existing topic
  const topic = pubsub.topic(req.body.topic);

  const messageObject = {
    data: {
      message: req.body.message,
    },
  };

  const messageBuffer = Buffer.from(JSON.stringify(messageObject)+msg, 'utf8');
  // Publishes a message
  try {
    await topic.publish(messageBuffer);
    //res.status(200).send('Message published.');
  } catch (err) {
    console.error(err);
    //res.status(500).send(err);
    return Promise.reject(err);
  }


}
/*

// Function asyncPubTranscription End


// Function <name> Init

// Function <name> 


/*****************************************************************************/
// ENDFUNCTIONS SECTION
/*****************************************************************************/

