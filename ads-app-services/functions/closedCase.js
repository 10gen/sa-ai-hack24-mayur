exports = async function(changeEvent) {
  
  const { updateDescription, fullDocument } = changeEvent;
  console.log (changeEvent)
  var serviceName = "mongodb-atlas";
  var dbName = "curated_data";
  var collName = "knowledgebase";
  var collection = context.services.get(serviceName).db(dbName).collection(collName);
  console.log(fullDocument);
  const description = changeEvent.fullDocument.description;
   var input = description;
   console.log("this description");
   console.log(input);
 if (Array.isArray(fullDocument.comments) && fullDocument.comments.length > 0) {
    console.log("comments array exists")
    fullDocument.comments.forEach(comment => {
      input += comment.comment + " " + comment.commentor + "\n";
    });
 }else{
   return;
 }
console.log("final form for input")
console.log(input);

  var body = {
    "input": {
      "kbInput": input 
    }
  }
  var payload = JSON.stringify(body);
  console.log("this is payload")
  console.log(payload);
  return context.http.post({
    "url": 'https://support-app.jollywave-3d0d89dd.westus2.azurecontainerapps.io/kb-summary/invoke',
    "body": payload,
    "headers": {
      'Content-Type': ['application/json']
      }
    })
    .then(response => {
      //const data = EJSON.parse(response.body.text());
      const data = response.body.text();
      console.log("this is the data");
      console.log(data);
      //console.log(JSON.stringify(data, null, 2));
      // Update these to reflect your db/collection
    
    let output = JSON.parse(data);
    let parsedOuput= output.output;
    console.log("this is output");
    console.log(parsedOuput);
    let cleanedString = parsedOuput.replace(/^{|}$/g, "").trim();
    console.log(cleanedString);
    // Format as valid JSON by quoting the keys
    cleanedString = cleanedString.replace(/(\w+):/g, '"$1":');
    
    // Parse the cleaned string as JSO
    const parsedData = JSON.parse(cleanedString);

    // console.log("this is parsed output");
    // console.log(parsed);
    // if (parsed.output && typeof parsed.output === 'string') {
    //   parsed = JSON.parse(parsed.output);
    //   console.log ("this is parsed 1.5");
    //   console.log(parsed);
    // }
    console.log("this is parsed Q");
    let question = parsedData.question;
    console.log(question);
        // Second parse for the 'question' and 'solution' properties
    let solution = parsedData.solution;
    console.log("this is parsed solution");
    console.log(solution)
    var doc = {
      "question": question,
      "answer": solution,
      "source": "support"
    }
    const findResult = async () => {
    await collection.insertOne(doc);
    }
    findResult();
    return;
    });
  };