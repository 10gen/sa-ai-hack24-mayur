exports = async function(arg){
  
  
  SCHEME = "https";
  // https://docs.atlas.mongodb.com/reference/api/vpc-get-connections-list/
  SENTIMENT_API_HOSTNAME_PATH = 'support-app.jollywave-3d0d89dd.westus2.azurecontainerapps.io/sentiment-summary/invoke';
  var serviceName = "mongodb-atlas";
  var dbName = "support";
  var collName = "triggerTest";
  var issuesColl = "issues";
  
  var body = {
    "input": {
             "input":"Need to fix the collections",
             "summary":""
              }
  }
  var payload = JSON.stringify(body);
  
  
  return context.http
    .post({
      "url": 'https://support-app.jollywave-3d0d89dd.westus2.azurecontainerapps.io/sentiment-summary/invoke',
     // "url": `${SCHEME}://${context.values.get("AtlasAPIKeyPublic")}:${context.values.get("AtlasAPIKeyPrivate")}@${ATLAS_API_HOSTNAME_PATH}`,
     // "digestAuth": true
     "body": payload,
      //encodeBodyAsJSON: true,
      "headers": {
        'Content-Type': ['application/json']
      }
    })
    .then(response => {
      const data = EJSON.parse(response.body.text());
      
     
      console.log(JSON.stringify(data, null, 2));
       // Update these to reflect your db/collection
     
  
    
    var collection = context.services.get(serviceName).db(dbName).collection(collName);
    const findResult = async () => {
     await collection.insertOne(data);
    }
    
    findResult();

  
      
  return;
  });
    
    /*
  // This default function will get a value and find a document in MongoDB
  // To see plenty more examples of what you can do with functions see: 
  // https://www.mongodb.com/docs/atlas/app-services/functions/

  // Find the name of the MongoDB service you want to use (see "Linked Data Sources" tab)
  var serviceName = "mongodb-atlas";

  // Update these to reflect your db/collection
  var dbName = "support";
  var collName = "issues";

  // Get a collection from the context
  var collection = context.services.get(serviceName).db(dbName).collection(collName);

  var findResult;
  try {
    // Get a value from the context (see "Values" tab)
    // Update this to reflect your value's name.
    //var valueName = "account";
   // var value = context.values.get(valueName);

    // Execute a FindOne in MongoDB 
    findResult = await collection.findOne(
      { "account": "ABC, Inc."},
    );

  } catch(err) {
    console.log("Error occurred while executing findOne:", err.message);

    return { error: err.message };
  }

  // To call other named functions:
  // var result = context.functions.execute("function_name", arg1, arg2);
  */

  return { "result": "findResult" };
};