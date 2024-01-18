exports = async function(changeEvent) {

  const serviceName = "mongodb-atlas";
  const databaseName = "curated_data";
  const collectionName = "mongodb";
  const collection = context.services.get(serviceName).db(databaseName).collection(changeEvent.ns.coll);
  // for test: const collection = context.services.get(serviceName).db(databaseName).collection(collectionName);

  const AZURE_OPENAI_KEY="9c5ec6797a8140229904eec37925a0d1";
  const AZURE_OPENAI_ENDPOINT="https://sawestaisandbox.openai.azure.com/";
  const AZURE_OPENAI_DEPLOYMENT="textembeddings";
  const myEmbedderURL = "https://sawestaisandbox.openai.azure.com/openai/deployments/textembeddings/embeddings?api-version=2023-05-15";

/* for test */
/*
  result = await getDoc();
  const docId = result._id;
  text = JSON.stringify(result.question+result.answer);
*/
  const docId = changeEvent.documentKey._id;
  const question = changeEvent.fullDocument.question;
  const answer = changeEvent.fullDocument.answer;
  text = JSON.stringify( question+answer );
  text = text.replace(/\\n+/g,'').trim();
  text = text.replace(/<p>+/g,'').trim();
  text = text.replace(/<\/p>+/g,'').trim();
  text = text.replace(/\s+/g,' ').trim();
  test = text.replace(/\s{2,}/g,' ').trim() 
  //console.log("text", docId, text);

  textInput='{"input"' + ":" + text + '}';
  //console.log("text1",textInput);
  var embedding = {};
  out = await context.http
    .post({
      "url": myEmbedderURL,
      "body": textInput,
      "headers": {
        'Content-Type': ['application/json'],
        'api-key': [AZURE_OPENAI_KEY],
        'encodeBodyAsJson': ["true"]
      }
    })
    .then(response => {
      const output = EJSON.parse(response.body.text());
      embedding = output.data[0].embedding;
    });
    
  var string = JSON.stringify(embedding, null, 2);
 //console.log("out",string);
  
// Update the document in MongoDB.
  try {
    var out = await collection.updateOne(
                { _id: docId },
                // The name of the new field you'd like to contain your embeddings.
                { $set: { "embedding": embedding }}
            );
    } catch(err) {
    console.log("error performing mongodb write: ", err.message);
    }
            
/*
  // Get the "FullDocument" present in the Insert/Replace/Update ChangeEvents
  try {

    // If this is an "insert" event, insert the document into the other collection
    if (changeEvent.operationType === "insert") {
      collection.insertOne(changeEvent.fullDocument);
    }

    // If this is an "update" or "replace" event, then replace the document in the other collection
    else if (changeEvent.operationType === "update" || changeEvent.operationType === "replace") {
      collection.replaceOne({"_id": docId}, changeEvent.fullDocument);
    }
  } catch(err) {
    console.log("error performing mongodb write: ", err.message);
  }
 */ 
};

async function getDoc() {
  
  const serviceName = "mongodb-atlas";
  const databaseName = "curated_data";
  const collectionName = "mongodb";
  const collection = context.services.get(serviceName).db(databaseName).collection(changeEvent.ns.coll);
  //const collection = context.services.get(serviceName).db(databaseName).collection(collectionName);

return collection.findOne({})
  .then(result => {
    if(result) {
      id=result._id
      console.log(`Successfully found document: ${id}.`);
    } else {
      console.log("No document matches the provided query.");
    }
    return result;
  })
  .catch(err => console.error(`Failed to find document: ${err}`));    
}
