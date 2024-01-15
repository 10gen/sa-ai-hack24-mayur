#! /usr/bin/env python3 

import json
import os
import re
import tiktoken
from num2words import num2words
from io import BytesIO
from database import getCollection
from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") 
client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_KEY"),  
  api_version = "2023-05-15",
  azure_endpoint =os.getenv("AZURE_OPENAI_ENDPOINT") 
)

def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()
    return s

tokenizer = tiktoken.get_encoding("cl100k_base")
def enrich():

    coll = getCollection()
    filter = { "text_embedding" : { "$exists": False} }
    for doc in coll.find(filter):
        input = doc["question"]+doc["answer"]
        normalized = normalize_text(input)
        n_tokens = len(tokenizer.encode(normalized))
        #print(doc["question"])
        if n_tokens < 8182:
            print("Enriching={}".format(doc["_id"]))
            print("tokens: {}".format( n_tokens ))
            response = client.embeddings.create(
              input = normalized,
              model = deployment
            )
            jsonout = json.loads( response.model_dump_json(indent=1) )
            embedding = jsonout['data'][0]['embedding']
            coll.update_one({"_id" : doc["_id"]}, {"$set" : { "text_embedding": embedding }})
        else:
            print("Skipping={}".format(doc["_id"]))
    
    print("Enrichment completed successfully!!!")

if __name__ == "__main__":
    enrich()
    print("Press ctrl-c to exit.")

