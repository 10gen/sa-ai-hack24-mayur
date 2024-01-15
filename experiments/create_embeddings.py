#run the below commands before running this script.
# OPENAI_API_KEY must be present in the env
#pip3 install langchain pymongo bs4 openai tiktoken gradio requests lxml argparse unstructured
#pip3 install -U langchain-openai
#pip3 install -U langchain-community
import pandas as pd
from openai import OpenAI, AzureOpenAI
import openai
from bs4 import BeautifulSoup
import os

#os.environ['OPENAI_API_KEY'] = ''


client = OpenAI()
# client = AzureOpenAI(api_key = os.getenv("OPENAI_API_KEY"),  
#                      api_version = "2023-07-01-preview",
#                      azure_endpoint ="https://sawestaisandbox.openai.azure.com/" )
embeddings_calls = 0

def get_embedding(text, model="text-embedding-ada-002"):
    
    global embeddings_calls
    text = text.replace("\n", " ")
    print (text)
    t = BeautifulSoup(text).get_text()
    embedding = client.embeddings.create(input=[t], model=model).data[0].embedding
    print('The embedding is: ' + str(embedding))
    embeddings_calls =  embeddings_calls + 1
    print(f'Embeddings api called: {embeddings_calls}')
    return embedding

df = pd.read_csv("QueryResultsNew.csv")

df['combined'] = "Embed Field: " + df['embedfield'].str.strip() + "; Answer: " + df['answer'].str.strip()

chunk_size = 25
list_df = [df[i:i+chunk_size] for i in range(0,len(df),chunk_size)]
print (f'Number of chunks {len(list_df)}')


import time
chunk_id = 0
for chunk in list_df:
    try:
        chunk_id = chunk_id + 1
        print (f'Processing chunk {chunk_id}')
        # Get embeddings and save them for future reuse
        chunk["embedding_combined"] = chunk["combined"].apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))
        chunk["embedding_question"] = chunk["embedfield"].apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))
        chunk["embedding_answer"] = chunk["answer"].apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))

        chunk.to_csv("dataset_with_qa_embeddings_openai-" + str(chunk_id) + ".csv")
        time.sleep(5)
        print (f'Processing the next chunk {chunk_id}')
    except Exception as e:
        try:
            print (f"Exception {e}")
        except Exception as ee:
            print ("Nested exception")
    except:
        print ('There was an error')


