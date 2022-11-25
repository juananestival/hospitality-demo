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
function replaceAll(string, search, replace) {
  return string.split(search).join(replace);
}

/*****************************************************************************/
// MAIN SECTION
/*****************************************************************************/
exports.main = (req, res) => {
 

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
  if (tag === "check-order") {
    getOrders(req, res);
  }

  if (tag === "get-loyalty-points") {
    getLoyaltyPoints(req, res);
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
        const loyaltyPoints = JSON.stringify(doc.data().loyaltyPoints);
        const insuranceType = JSON.stringify(doc.data().insuranceType);
        const insuranceLevel = JSON.stringify(doc.data().insuranceLevel);

        

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
                first_name:firstName,
                loyalty_points:loyaltyPoints,
                insurance_type:insuranceType,
                insurance_level:insuranceLevel
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
      const insuranceType = JSON.stringify(doc.data().insuranceType);
      const insuranceLevel = JSON.stringify(doc.data().insuranceLevel);
      
      res.status(200).send({
        sessionInfo: {
          parameters: {
            last_name: lastName,
            first_name: firstName,
            loyalty_points: loyaltyPoints,
            insurance_type:insuranceType,
            insurance_level:insuranceLevel,
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
        var answerbylang
        let lang = req.body.languageCode;
        if (lang === "ca") {
          answerbylang = `Actualment teniu reserves de ${querySnapshot.size}. Les reserves registrades són: `

        } else if (lang === "es") {
          answerbylang = `Actualmente tiene ${querySnapshot.size} reservas. Las reservas registradas son: `



        } else {
          answerbylang = `Currently you have ${querySnapshot.size} reservations. The registered reservations are: `
        }

        querySnapshot.forEach((doc) => {
          console.log(doc.id, " => ", doc.data());
          if (lang === "ca") {
            answerbylang = answerbylang + `Hotel ${JSON.stringify(doc.data().hotel)} per ${JSON.stringify(doc.data().nights)} nits.` 


          } else if (lang === "es") {
            answerbylang = answerbylang + `Hotel ${JSON.stringify(doc.data().hotel)} por ${JSON.stringify(doc.data().nights)} noches.` 


          } else {
            answerbylang = answerbylang + `Hotel ${JSON.stringify(doc.data().hotel)} for ${JSON.stringify(doc.data().nights)} nights.` 


          }
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
                  text: [answerbylang],
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
function getOrders (req, res) {
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
    .collection('orders')
    .get()
    .then((querySnapshot)=>{
      console.log(`Currently there are: ${querySnapshot.size} orders`)
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
        var answerbylang
        var estimated_delivery
        let lang = req.body.languageCode;
        if (lang === "ca") {
          answerbylang = `Actualment teniu  ${querySnapshot.size} comandes. Les comandes registrades són: `

        } else if (lang === "es" | lang === "es-es") {
          answerbylang = `Actualmente el número de pedidos que tenemos registrados es ${querySnapshot.size}.`



        } else {
          answerbylang = `Currently you have ${querySnapshot.size} orders. The registered orders are: `
        }

        querySnapshot.forEach((doc) => {
          console.log(doc.id, " => ", doc.data());
          if (lang === "ca") {
            answerbylang = answerbylang + `comande amb stat ${JSON.stringify(doc.data().status)} amb lliurament estimat  ${JSON.stringify(doc.data().estimated_delivery).replace(/""/g, '' )} .` 


          } else if  (lang === "es" | lang === "es-es") {
            answerbylang = answerbylang + `Pedido con estado ${JSON.stringify(doc.data().status)}.` 
            estimated_delivery_temp = JSON.stringify(doc.data().estimated_delivery)
            estimated_delivery = replaceAll(JSON.stringify(doc.data().estimated_delivery), '"', '');

          } else {
            answerbylang = answerbylang + `Order with status ${JSON.stringify(doc.data().status)} with estimated delivery ${JSON.stringify(doc.data().estimated_delivery).replace(/""/g, '' )} .` 


          }
        })
        res.status(200).send({
          sessionInfo: {
            parameters: {
              reservations_list: querySnapshot.size,  
              date:estimated_delivery
              // message 'you have more than 3 reservations. Transfer?'      
            },
          },
          fulfillmentResponse: {
            messages: [
              {
                text: {
                  text: [answerbylang],
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

/*****************************************************************************/
/*****************************************************************************/
function getLoyaltyPoints (req, res) {
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
        const loyaltyLevel = JSON.stringify(doc.data().loyaltyLevel);
        const loyaltyPoints = JSON.stringify(doc.data().loyaltyPoints);
        const sessionId = req.body.sessionInfo.session;

        res.status(200).send({
          sessionInfo: {
            parameters: {
              loyalty_level: loyaltyLevel,
              loyalty_points:loyaltyPoints,
              session:sessionId
            },
          },
        });

      }
    })
    .then()
    .catch();

  // End query

  // End query

}