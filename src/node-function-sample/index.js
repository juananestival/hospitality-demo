/*****************************************************************************/
// DEFINITION SECTION
/*****************************************************************************/
const COLLECTION_NAME = "customers";
const PROJECTID = "hospitality-demo-361210";
const Firestore = require("@google-cloud/firestore");
const firestore = new Firestore({
  projectId: PROJECTID,
  timestampsInSnapshots: true,
});

/*****************************************************************************/
// MAIN SECTION
/*****************************************************************************/
exports.hospitalityMainWH = (req, res) => {
  // Log some parameters
  console.log(`Function version: ${process.env.K_REVISION}`);
  console.log("Dialogflow Request body: " + JSON.stringify(req.body));
  let tag = req.body.fulfillmentInfo.tag;
  console.log("Tag: " + tag);
  console.log(
    "Session Info Parameters: " +
      JSON.stringify(req.body.sessionInfo.parameters)
  );

  // Checking Tags
  if (tag === "channel-type") {
    console.log("Evaluating type of channel...1");
    channelEvaluation(req, res);
  }
  if (tag === "validate-customer") {
    validateCustomer(req, res);
  }

  if (tag === "check-ani") {
    checkANI(req, res);
  }

  if (tag === "ani-lookup") {
    aniLookup(req, res);
  }

  if (tag === "get-reservations") {
    getReservations(req, res);
  }

  // If enabled the function is stopped before getting fs answer
  //res.end()
};

/*****************************************************************************/
// FUNCTIONS SECTION
/*****************************************************************************/
function channelEvaluation(req, res) {
  console.log("Evaluating type of channel...2");
  if (req.body.hasOwnProperty("payload")) {
    let phoneNumber = req.body.payload.telephony.caller_id;
    console.log("CHANNEL-TYPE: VOICE");
    return res.status(200).send({
      sessionInfo: {
        parameters: {
          channel: "voice",
          ani: phoneNumber,
        },
      },
    });
  } else {
    console.log("CHANNEL-TYPE: TEXT");
    return res.status(200).send({
      sessionInfo: {
        parameters: {
          channel: "chat"
        },
      },
    });
  }
}
/*****************************************************************************/
/*****************************************************************************/

function validateCustomer(req, res) {
  let channel = req.body.sessionInfo.parameters.channel;
  let documentId;

  if (channel === "voice") {
    if (req.body.hasOwnProperty("payload")) {
      documentId = req.body.payload.telephony.caller_id;
    }
  } else {
    documentId = req.body.sessionInfo.parameters.customerid;
  }
  console.log("READY FOR QUERY");
  // Query Firehose
  return firestore
    .collection(COLLECTION_NAME)
    .doc(documentId)
    .get()
    .then((doc) => {
      //NOT FOUND
      if (!(doc && doc.exists)) {
        res.status(200).send({
          sessionInfo: {
            parameters: {
              customerverified: false,
            },
          },
        });
      } else {
        //FOUND
        const data = doc.data();
        console.log(JSON.stringify(data));
        const lastName = JSON.stringify(doc.data().lastName);
        const firstName = JSON.stringify(doc.data().firstName);
        const pinNumber = JSON.stringify(doc.data().pinNumber);

        

        // Wrong Pin
        if (!(pinNumber === req.body.sessionInfo.parameters.customerpin)) {
          res.status(200).send({
            sessionInfo: {
              parameters: {
                customerverified: false,
              },
            },
          });
        } else {
          //PIN OK
          res.status(200).send({
            sessionInfo: {
              parameters: {
                customerverified: true,
                last_name: lastName,
                first_name:firstName
              },
            },
          });
        }
      }
    })
    .then()
    .catch();

  // End query
}

/*****************************************************************************/
/*****************************************************************************/

function checkANI(req, res) {
  let phoneNumber = req.body.payload.telephony.caller_id;
  // Document id is the phone number.

  const id = phoneNumber;
  console.log("Id: " + id);

  // Query Firehose
  return firestore
    .collection(COLLECTION_NAME)
    .doc(id)
    .get()
    .then((doc) => {
      if (!(doc && doc.exists)) {
      
        res.status(200).send({
          sessionInfo: {
            parameters: {
              ani_lookup: "not-found",
            },
          },
        });
      }

      const data = doc.data();
      console.log(JSON.stringify(data));
      const lastName = JSON.stringify(doc.data().lastName);
      const firstName = JSON.stringify(doc.data().firstName);
      const pinNumber = JSON.stringify(doc.data().pinNumber);

      var answer = "Welcome";
      console.log(answer);
      res.status(200).send({
        sessionInfo: {
          parameters: {
            ani: phoneNumber,
            customerid: phoneNumber,
            lastName: lastName,
            firstName: firstName,
            dbPinNumber: pinNumber,
          },
        },
        
        fulfillmentResponse: {
          messages: [
            {
              text: {
                text: [answer],
              },
            },
          ],
        },
      });
    })
    .catch((err) => {
      console.error(err);
      return res.status(404).send({ error: "Unable to retrieve the document" });
    });

  // End query
}

/*****************************************************************************/
/*****************************************************************************/

function aniLookup(req, res) {
  let phoneNumber = req.body.payload.telephony.caller_id;
  const id = phoneNumber;
  console.log("Id: " + id);

  // Query Firehose
  return firestore
    .collection(COLLECTION_NAME)
    .doc(id)
    .get()
    .then((doc) => {
      if (!(doc && doc.exists)) {
        console.log("ANI Not in Database")
        res.status(200).send({
          sessionInfo: {
            parameters: {
              ani_lookup: "not-found",
            },
          },
        });
      } else { 
      const data = doc.data();
      console.log(JSON.stringify(data));
      const lastName = JSON.stringify(doc.data().lastName);
      const firstName = JSON.stringify(doc.data().firstName);
      const loyaltyPoints = JSON.stringify(doc.data().loyaltyPoints);
      
      res.status(200).send({
        sessionInfo: {
          parameters: {
            last_name: lastName,
            first_name: firstName,
            loyalty_points: loyaltyPoints,
            ani_lookup: "found"         
          },
        },
      });
    }})
    
    .catch((err) => {
      console.error(err);
      return res.status(404).send({ error: "Unable to retrieve the document" });
    });

  // End query
}

/*****************************************************************************/
/*****************************************************************************/
function getReservations (req, res) {
  let channel = req.body.sessionInfo.parameters.channel;
  let documentId;

  if (channel === "voice") {
    if (req.body.hasOwnProperty("payload")) {
      documentId = req.body.payload.telephony.caller_id;
    }
  } else {
    documentId = req.body.sessionInfo.parameters.customerid;
  }
  console.log("READY FOR QUERY");
  // Query Firehose
  return firestore

  
  
    .collection(COLLECTION_NAME)
    .doc(documentId)
    .collection('reservations')
    .get()
    .then((querySnapshot)=>{
      console.log(`Currently there are: ${querySnapshot.size} reservations`)
      if ((querySnapshot.size > 3)) {
        res.status(200).send({
          sessionInfo: {
            parameters: {
              reservations_list: querySnapshot.size,  
              // message 'you have more than 3 reservations. Transfer?'      
            },
          },
          fulfillmentResponse: {
            messages: [
              {
                text: {
                  text: [`You have ${querySnapshot.size}. You will be better serve by an agent.`],
                },
              },
            ],
          },
        });
      
      } else {
        let answer = `Currently you have ${querySnapshot.size} reservations. The registered reservations are: `
        querySnapshot.forEach((doc) => {
          console.log(doc.id, " => ", doc.data());
          answer = answer + `Hotel ${JSON.stringify(doc.data().hotel)} for ${JSON.stringify(doc.data().nights)} nights.` 
        })
        res.status(200).send({
          sessionInfo: {
            parameters: {
              reservations_list: querySnapshot.size,  
              // message 'you have more than 3 reservations. Transfer?'      
            },
          },
          fulfillmentResponse: {
            messages: [
              {
                text: {
                  text: [answer],
                },
              },
            ],
          },
        });
        

      }
      

    })
    .catch();

  // End query

}