const https = require('https');
/*****************************************************************************/
// DEFINITION SECTION
/*****************************************************************************/

function replaceAll(string, search, replace) {
  return string.split(search).join(replace);
}

/*****************************************************************************/
// MAIN SECTION
/*****************************************************************************/
exports.index = (req, res) => {
 

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
  if (tag === "consulta-pokemon") {
    console.log("Consultando Pokemon");
    respuesta = consultaPokemon(req, res);
	//console.log(`desde tag ${respuesta.id}`)

  }

};

/*****************************************************************************/
// FUNCTIONS SECTION
/*****************************************************************************/
async function consultaPokemon(req, res) {
  console.log("Consulta Pokemon Iniciado");
  //
  //console.log(`Sobre el pokemon ${req.body.sessionInfo.parameters.nombrepokemon.original}`)
  console.log(`Sobre el pokemon ${req.body.sessionInfo.parameters.nombrepokemon}`)
  //pokemon = req.body.sessionInfo.parameters.nombrepokemon.original
  pokemon = req.body.sessionInfo.parameters.nombrepokemon
  respuesta = await makeSynchronousRequest(pokemon)
  res.status(200).send({
	sessionInfo: {
	  parameters: {
		pokemon_id: replaceAll(JSON.stringify(respuesta.id), '"', ''),
		pokemon_image: replaceAll(JSON.stringify(respuesta.sprites.other.dream_world.front_default), '"', ''),
		pokemon_name: replaceAll(JSON.stringify(respuesta.name), '"', ''),
		pokemon_height: JSON.stringify(respuesta.height),
		pokemon_weight: JSON.stringify(respuesta.weight),
		pokemon_base_experience: JSON.stringify(respuesta.base_experience),
		pokemon_type: replaceAll(JSON.stringify(respuesta.types[0].type.name), '"', '')
	  },
	},
  });
  console.log(`respuesta ${respuesta}`)
  return respuesta

}
/*****************************************************************************/
/*****************************************************************************/


// function returns a Promise
function getPromise(request) {
	return new Promise((resolve, reject) => {
		https.get(`https://pokeapi.co/api/v2/pokemon/${request}`, (response) => {
			let chunks_of_data = [];

			response.on('data', (fragments) => {
				chunks_of_data.push(fragments);
			});

			response.on('end', () => {
				let response_body = Buffer.concat(chunks_of_data);
				resolve(response_body.toString());
			});

			response.on('error', (error) => {
				reject(error);
			});
		});
	});
}

// async function to make http request
async function makeSynchronousRequest(request) {
	try {
		let http_promise = getPromise(request);
		let response_body = await http_promise;

		// holds response from server that is passed when Promise is resolved
		//console.log(`Respuesta makeSynchronousRequest ${response_body}`);
		//console.log(`Typeof makeSynchronousRequest ${typeof(response_body)}`);
		pokeJson = JSON.parse(response_body)
		console.log(`Sample field id ${pokeJson.id}`);
		console.log(`Sample field stringfy id ${JSON.stringify(pokeJson.id)}`);
		console.log(`Sample field stringfy type ${JSON.stringify(pokeJson.types[0].type.name)}`);
		return pokeJson
	}
	catch(error) {
		// Promise rejected
		console.log(error);
	}
}

console.log(1);

// anonymous async function to execute some code synchronously after http request
(async function () {
	// wait to http request to finish
	await makeSynchronousRequest();
	
	// below code will be executed after http request is finished
	console.log(2);
})();

console.log(3);