
import pymongo
from urllib.parse import quote_plus
import pandas as pd
import json
import glob

uri = "mongodb+srv://" + quote_plus("mongoadmin") + ":" + quote_plus("h@ckath0n24") + "@supportdb.ob4zr.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(uri)
testembeddingsdb = client["testembeddingsdb"]
testembeddingscol = testembeddingsdb['testembeddingscol']
# testdoc = { "name": "Gautam", "address": "Highway 37" }
# x = testembeddingscol.insert_one(testdoc)

# df = pd.read_csv("dataset_with_qa_embeddings.csv")
all_files = glob.glob('dataset_with_qa_embeddings_openai-*.csv')



for filename in all_files:
    df = pd.read_csv(filename)
    for index, row in df.iterrows():
        ticket = row.to_json()
        ticket_dict = json.loads(ticket)
        del ticket_dict["Unnamed: 0"]
        ticket_dict['embedding_combined'] = eval(ticket_dict['embedding_combined'])
        ticket_dict['embedding_question'] = eval(ticket_dict['embedding_question'])
        ticket_dict['embedding_answer'] = eval(ticket_dict['embedding_answer'])

        print (ticket_dict)
        x = testembeddingscol.insert_one(ticket_dict)
        break
    
        

# for i in df.index:
#     # row = df.loc[i].to_json("row{}.json".format(i))
#     row = df.loc[i].to_json("row{}.json".format(i), orient='records')
#     print (row)
#     # ticket = json.loads(row)
#     # ticket_str = json.dumps(ticket)
#     # print (ticket)
#     # print (ticket_str)
#     # print (json.loads(row[0]))
#     break

# df['json'] = df.apply(lambda x: x.to_json(), axis=1)

    


# %%



