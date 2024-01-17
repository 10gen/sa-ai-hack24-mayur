#!pip install "langserve[all]"
#!pip install langchain-cli
#!pip install langchain-openai

import os
#from bson import json_util
#import json

#rom dotenv import load_dotenv
#load_dotenv()
#from langchain_openai import AzureOpenAI

from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
)
from pymongo import MongoClient


from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes


from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)






app = FastAPI()

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_API_TYPE = os.environ["OPENAI_API_TYPE"]
MONGO_URI = os.environ["MONGO_URI"]
AZURE_OPENAI_ENDPOINT= os.environ["AZURE_OPENAI_ENDPOINT"]
CHAT_API_VERSION= os.environ["CHAT_API_VERSION"]
CHAT_DEPLOYMENT= os.environ["CHAT_DEPLOYMENT"]
CHAT_END_POINT= os.environ["CHAT_END_POINT"]

examples = [
     {
     "input": "In Production EU, we recently updated the MongoDB operator to the latest version 1.22 and configured the newly released log rotation features. Before the upgrade, the Config pods were in a running state, but the container state was 0/1. After successfully completing the upgrade playbook, the ops-manager-db and ops-manager pods rolled out and came up successfully. However, the config pod restart did not happen; it was stuck. I attempted to manually restart the config-2 pod, but after doing so, the config pod is not coming up. I have attached the logs for your reference. Could someone please investigate this on priority? ",
     "output": "case_score: 1"
     },
     {
     "input": "case_score: 4, We acknowledge your need for this case to be used during the upcoming event. If any issues arise that need our assistance, please open another case with full details, severity level 1-4, and attach all logs and diagnostics for the time period just before and after the event frame. Let us know if you need our assistance.", 
     "output": "case_score: 5, comment_score: 5"
     },
     {
     "input": """case_score: 6, Thank you for letting me know that that worked. To answer your question: Also do I need to update the content type ever few months to make sure the date is correct? If you're not planning to use any new features released in a later version of the API, then no, you should not have to change the content version. This versioning is supposed to make it so that things won't break as we continue to make changes to the API to add features, as we would add them to a later-dated version of the API. The documentation for this endpoint says the current version of the API was released with the 2023-01-01 version of the API and hasn't been touched in subsequent versions.I think the actual change that made the request work was to add the Accept header in addition to the Content-Type header. I would bet that if you sent this as headers, it would also work:  
           { \"Content-Type\": \"application/vnd.atlas.2023-01-01+json\", \"Accept\": \"application/vnd.atlas.2023-01-01+json\" } Please let me know if you have any questions about this information.""", 
     "output":"case_score: 7, comment_score: 8"
     },
     {
    "input":"""case_score: 4, This is an automated reminder that this ticket is awaiting your response. Please respond to this ticket so that we can continue working on this issue with you, or let us know if the ticket can be resolved.""", 
     "output": "case_score: 5, comment_score: 5"
     },
     {
     "input":"""case_score: 2, This is an automated reminder that this ticket is awaiting your response. Please respond to this ticket so that we can continue working on this issue with you, or let us know if the ticket can be resolved.""", 
     "output": "case_score: 2, comment_score: 4"
     },
     {
     "input":"""case_score: 3, Thank you for the patience.
                From the case description I understand that you have modified the oplog size of your rollups-3 cluster from 375000 MB to 300000 MB.
                But the oplog size was automatically scaled to 51200 MB the same time when you submitted the disk size downgrade.
                And you would like to understand what triggered this automated downscaling of oplog size here.
                Currently the disk size on 00 secondary nodes on all the shards are being downgraded and this is happening in a rolling fashion.
                Please bear with me while I am investigating on this further. Meanwhile your patience here is much appreciated!       """, 
     "output": "case_score: 4, comment_score: 4"
     },
]


systemMessage = """
                 You are a Technical Analyst who can look at a statement and infer the sentiment and give it a score. The score can range from 0 to 10. Where 0 represents most negative, 5 is neutral and 10 is the most positive sentiment. \
                 The imput statements are related to a technical support ticket raised by a customer on a support portal. 
                 The following rules are to be used: 
                 1. case_score is the overall sentiment score for the ticket 
                 2. comment_score is the overall sentiment of the comment on that ticket. 
                 3. Your job is to determine the case_score if the input doesnt include any case_score.
                 4. If the input contains a case_score, use this case_score along with the given input to generate the overall case_score and the comment_score.
                 5. If the input contains the case_score, it will always be the first part of the input text followed by comma and the comment for e.g. \"case_score: 7, input comment\". here case_score of 7 represents the overall case score and comment is the new comment being added \
                 6. If case_score is not given, then the comment is the description of a new case and so only case_score needs to be given based on the given description \
                 7. If case_score is given, then use that to determine the sentiment score for the comment as the customer may feel differently if they are already happy or frustrated with the overall case. \
                 8. You can then increase or decrease the case_score by 1 or keep it the same based on the sentiment of the new comment being added \
                 9. the output should be two variables with integer value substituting \"value\" and should be of format \"case_score: value\" if no overall case score is given and of format \"case_score: new_value, comment_score: value\" when overall case score is given and new_value is the new calculated case sentiment score after the new comment was added"""

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",systemMessage),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)

model = AzureChatOpenAI(
            azure_deployment=CHAT_DEPLOYMENT,
            openai_api_version=CHAT_API_VERSION,
            azure_endpoint=CHAT_END_POINT
            )

chain1 = final_prompt | model | StrOutputParser() 

systemMessageSummary= """ Summarize {input} and the optional {summary} provided to generate a new summary in less than 100 words"""
summary_prompt = ChatPromptTemplate.from_template(systemMessageSummary)

chain2 = summary_prompt | model |  StrOutputParser() 

#chain = RunnableParallel(sentiment=chain1, summary=chain2)

saSummaryPrompt = """
        You are an AI support tool for Solution Architects wanting a quick look at the support cases for their customers. 
        The input will be the optional Account Summary, optional Account sentiment Score {{{{account_score}}}}, optional case Sentiment score {{{{case_score}}}} and finally the new comment being added. 
        Combine all the data, including {{{{input}}}}, {{{{summary}}}} and optional {{{{saSummaryInput}}}}, to generate the following insights - 
        The output should have two categories: 
        Account Summary which tells us based on present case if there are any account based risks and any upsell opportunities. 
        The second part will be what next steps solution architect can take to minimize the risks identified or to better the upsell opportunities. 

        Here is a list of MongoDB products and services that can be sold to the customer:
        1. Atlas: A multi-cloud database that simplifies application development and data management for a variety of use cases, offering global scaling and price/performance optimization as data needs evolve.
        If a customer is running their databases on-prem and have operational issues, you can recommend Atlas.

        2. Atlas Search: Delivers engaging search experiences by providing a Lucene based search index on top of the data stored in an Atlas Database.
        Recommend Atlas Search for any full text search scenario or where better customer engagement is needed from the UI perspective. 

        3. Vector Search: Enables the design of intelligent apps with Generative AI by allowing semantic search on data stored in Atlas using vector index.
        Vector Searches can help with Retrieval Augmented Generation (RAG) based use cases. 

        4. Stream Processing (Preview): Unifies data in motion and data at rest by allowing streaming query capability.
        You may recommend Streams Processing if customer has to analyze streaming data. 

        5. Atlas Online Archive: Allows you to use low cost Cloud Object storage to archive data out of a hot Atlas database while allowing query capabilities into the archived and hot data.
        You may recommend this when the database size is too large and cost savings is needed.

        6. Atlas Data Federation: Allows you to bring data stored in your Cloud Object Storage and query it using Mongo Query Language as a virtual Mongo Database.
        This can be recommended when customer has analytical use cases or trying to integrate mongodb with data residing on cloud object stores or when data integration across heterogenous sources is needed. 

        7. Atlas Triggers: Allows you to create scheduled or database evets based triggers where a CRUD operation on Database can invoke a serverless function. Triggers can respond to events or use pre-defined schedules.
        You can recommend triggers when customer is trying to build a envent driven architecture on MongoDB Atlas.

        8. Atlas Serverless Functions: An Atlas Serverless Function is a piece of server-side JavaScript code that you write to define your app's behavior. You can call your app's functions directly from a client app or define services 
        that integrate and call functions automatically.
        You can recommend serverless functions when trying to create short lived lambda applications or any other serverless environment.

        9. Atlas Data API: The Data API is a managed service that lets you securely work with data stored in Atlas using standard HTTPS requests. The Data API is not a direct connection to your database. Instead, the API is a fully-managed middleware service that sits between your cluster and the clients that send requests.
        You can recommend Atlas Data Api is the customer needs a quick way to access the data in mongodb ATlas environment.

        10. Atlas GraphQL: The Atlas GraphQL API allows client applications to access data stored in a linked MongoDB Atlas cluster using any standard GraphQL client. Atlas App Services automatically creates GraphQL types for every linked collection that has a defined schema and evaluates role-based permissions for all GraphQL requests.
        You may recommend Atlas graphQL is customer is using or planning to use GraphQL for data access.

        11.Atlas Edge Server: Edge Server runs on-premises and handles sync between local devices, and bi-directional sync between the Edge Server and Atlas.
        You may recommend Atlas Edge Server if the customer is developing a distributed application with some components on-prem and some running in Atlas and he needs data synchronization 
        
        12. Professional Services: MongoDB provides paid consulting engagements to help customers adopt MongoDB best practices for a given project. You may sell MongoDB Consulting Services for a MongoDB project consulting, if the customer shows lack of knowledge for mongodb best practices or is looking for education on MongoDB services.
        
        You can recommend multiple services at a time.
        
        """

saSummaryexamples = [
     {
     "saSummaryInput": """ Account Summary: New client, showing significant potential for growth and expansion, with 6 deployments/instances over 1 years.Present Annual revenue on Atlas is $1,000,000.
        Account Sentiment Score: 6
        Case Sentiment Score: 5
        Comment: 
        Hi,  
        
        We need to archive data from one of our cluster  
        Cluster details:  
        
        Name : info-5  
        Database : enlighten_production  
        Collection : email_logs  
        Size of collection : 2TB  
        
        The size of this cluster is very high and because of this we are seeing performance issues in our applications. Deleting large amount of data from the cluster will overload the cluster and this will exhaust the write tickets.  
        
        Please let us know which is the best approach to re-size this cluster.  
        
        Thanks,  
        Nandhini D.  
        
        
        Comments  4  
        
        Internal Notes  
        
        Case History  
        
        All Comments  
        
        Show: All  
        1 - 4 / 4    
        case-comment-avatar  
        Nandhini Dhinakaran  
        12/12/2023 2:10 AM PST | User Time 12/12/2023 3:40 PM IST  
        
        NEUTRAL  
        EVERYONE  
        We would like to understand which will be the best approach for both deletion and archival of data.  
        
        Thanks.  
        
        View Markdown  
        Open in SFSC  
        Copy Link  
        case-comment-avatar  
        Benjamin Castillo  
        12/12/2023 4:11 AM PST | User Time 12/12/2023 7:11 AM EST  
        
        POSITIVE  
        EVERYONE  
        Hello Nandhini  
        
        Thank you for contacting MongoDB Support. My name is Ben, and I am happy to assist you with your inquiry.  
        
        We would like to understand which will be the best approach for both deletion and archival of data.  
        
        Below are the recommendations for deletion and archival of data. This is further detailed in document link.  
        
        Delete documents in batches. Start with small batches and increase gradually to ensure acceptable performance impact.  
        Add a pause between each batch to allow the delete commands to replicate to the other members of the replica set.  
        Use write-concern majority to help alleviate possible lag issues.  
        Please contact us if you have additional questions.  
        
        Regards,  
        
        Ben  
        
        View Markdown  
        Open in SFSC  
        Copy Link  
        Support AI  
        
        SUMMARY  
        Comments from 12/12/2023 2:10 AM PST - 12/12/2023 4:11 AM PST  
        The customer is seeking advice on the best approach for both deletion and archival of data. Ben from MongoDB Support recommends deleting documents in batches, starting with small batches and increasing gradually to ensure acceptable performance impact. He also suggests adding a pause between each batch to allow the delete commands to replicate to the other members of the replica set and using write-concern majority to help alleviate possible lag issues. Ben provides a link to a document with further details on these recommendations and invites the customer to contact them if they have additional questions.  
        
        case-comment-avatar  
        MongoDB Support  
        12/16/2023 4:15 AM PST | User Time 12/16/2023 7:15 AM EST  
        
        NEUTRAL  
        EVERYONE  
        Hello,  
        
        This is an automated reminder that this ticket is awaiting your response. Please respond to this ticket so that we can continue working on this issue with you, or let us know if the ticket can be resolved.  
        
        Thanks,  
        MongoDB Support  
        
        View Markdown  
        Open in SFSC  
        Copy Link  
        case-comment-avatar  
        MongoDB Support  
        12/16/2023 4:15 AM PST | User Time 12/16/2023 7:15 AM EST  
        
        NEUTRAL  
        INTERNAL  
        AutoCloseSF1 state performed, the following actions were taken:  
        
        First customer notification sent """,
            
    "saSummaryOutput": """ Account Summary:
        Sentiment Score: 6
        Upsell Opportunity: The account is showing significant potential for growth and expansion, with 6 deployments/instances over 1 year and an annual revenue of $1,000,000 on Atlas.
        Risks:
        The customer is experiencing performance issues in their applications due to the large size of their cluster, and they are concerned about overloading the cluster and exhausting write tickets while attempting to delete a large amount of data.
        Upsell Opportunities:
        Given the significant potential for growth and the revenue generated on Atlas, there is an upsell opportunity for various features that can enhance the customer's MongoDB deployment.
        Next Steps:
        The Solution Architect could consider the following next steps to address the risks and leverage the upsell opportunity:

        Upsell Features: Engage with the customer to discuss potential upsell opportunities, such as "Atlas Online Archive" to address the performance issues caused by the large cluster size and provide a scalable solution for managing data.
        Performance Optimization: Provide guidance on resizing the cluster and optimizing performance, leveraging MongoDB's best practices and potentially considering additional features or services that align with the customer's growth trajectory.
        Engagement Strategy: Develop an engagement strategy to understand the customer's future needs and how MongoDB's products and services can support their expansion plans, potentially exploring features like "Atlas Data Federation" or "Atlas Triggers" to align with their growth and expansion goals.

        By aligning the upsell opportunities with the customer's growth potential and addressing the performance issues, the Solution Architect can add value to the customer's MongoDB deployment and position MongoDB as a strategic partner for their future expansion."""
    },
    {
     "saSummaryInput": """ Comment: We need to update the records in a nested document. We need to update the datatype from int to long. (int32 to int64).

        Sample document :
        { _id: 'xxxxxx:20231225',
        battery_channels: {
        '12xxxxxx233_1': {
        '1703xxxx93': { enj: 0, d: 360, mgh: 7200 , nav: 100 } },
        '170xxxx637': { enj: 0, d: 344, mgh: 7200, nav: 100 } }
        }}}

        We need to update the datatype of enj field from int to long.

        Please help us with this query. Our production sites are affected due to this datatype change. Kindly help us in priority. """,
    "saSummaryOutput": """ It seems like the customer is facing a critical issue with updating the data type of a field in a nested document and it's impacting their production sites. The urgency of the request indicates a high level of concern and potential risk to their operations.

        The Solution Architect should take the following steps to address this urgent request:

        Immediate Support: Engage with the customer promptly to understand the specific requirements for updating the datatype of the "enj" field from int to long and provide them with a query that can address their critical issue.
        Best Practices: Offer guidance on best practices for updating data types in MongoDB, ensuring that the proposed solution aligns with the customer's production environment and minimizes any potential impact on their operations.
        Post-Resolution Support: Follow up with the customer after providing the query to ensure that the issue has been resolved and the impact on their production sites has been mitigated.

        By providing immediate support and a robust query to address the datatype change issue, the Solution Architect can help the customer minimize the impact on their production sites and demonstrate MongoDB's commitment to addressing critical issues promptly."""
    },
]

saSummaryexample_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{saSummaryInput}"),
        ("ai", "{saSummaryOutput}"),
    ]
)

few_shot_prompt_sa_summary = FewShotChatMessagePromptTemplate(
    
    example_prompt=saSummaryexample_prompt,
    examples=saSummaryexamples
    
)

final_prompt_sa_summary = ChatPromptTemplate.from_messages(
    [
        ("system",saSummaryPrompt),
        few_shot_prompt,
        ("human", "{saSummaryInput}"),
    ]
)

chain3 = final_prompt_sa_summary | model |  StrOutputParser() 

chain = RunnableParallel(sentiment=chain1, summary=chain2, saSummary=chain3)



add_routes(
    app,
    chain,
    path="/sentiment-summary",
)

kbPrompt = """ You are an AI assistant that helps with the creation of knowledge base based on a database support issue. 
            You will be provided with the conversation between mongoDB support and the customer as a single input {kbInput}. This includes the support case description and the 
            subsequent interaction between the support team and the customer till the ticket was resolved.  
            
            carefully analyze the ticket and infer what was the problem statement and what was the solution provided by the support team.

            The output you provide will be in JSON format with two fields question and solution, like this: 
            "{{{{question: summary of the issue, solution: summary of the solution proivided}}}}" where {{{question}}} is a good summarization of 
            what was the question was being asked by the customer and the {{{solution}}} will be a good summarization of the 
            solution that was provided by the support team that led to the ticket resolution. If the support case did not have a good solution or was closed 
            for non responsiveness then provide empty responses in the form of "{{{{question: , solution:  }}}}" """

kbExamples = [
     {
        "kbInput": """ Hi  
            
            We are seeing timeout errors in most of the applications.  
            
            Error message:  
            
            Mongo::Error::SocketTimeoutError: Errno::ETIMEDOUT: Operation timed out - Took more than 90 seconds to receive data (select call timed out) (for 192.168.240.226:27017 (preprod-info-1-shard-00-00.bxbxc.mongodb.net:27017, TLS)) (on preprod-info-1-shard-00-00.bxbxc.mongodb.net:27017, connection 1:4, modern retry, attempt 2).  
            
            Please help us understand the issue. This is causing high error rate in most of our applications and affecting the alpha users.  
            
            Thanks,  
            Nandhini D.  
            
            
            Comments  9  
            
            Internal Notes  
            
            Case History  
            
            All Comments  
            
            Show: All  
            1 - 9 / 9    
            File(s) uploaded:  
            
            Query targeting metrics.png  
            Uploaded by Alejo Gonez at 12/21/2023 2:37 AM PST  
            
            Query targeting metrics.png  
            case-comment-avatar  
            Alejo Gonez  
            12/21/2023 3:07 AM PST | User Time 12/21/2023 12:07 PM CET  
            
            NEUTRAL  
            EVERYONE  
            Hello Nandhini,  
            
            Thanks for contacting MongoDB support. I would be happy to assist you on this.  
            
            It's my understanding you are encountering errors when connecting to the preprod-info-1 but you still able to connect. Please let me know if this is not the case.  
            
            Mongo::Error::SocketTimeoutError: Errno::ETIMEDOUT: Operation timed out - Took more than 90 seconds to receive data (select call timed out) (for 192.168.240.226:27017 (preprod-info-1-shard-00-00.bxbxc.mongodb.net:27017, TLS)) (on preprod-info-1-shard-00-00.bxbxc.mongodb.net:27017, connection 1:4, modern retry, attempt 2).  
            
            Based on the error message shared, it seems your application is unable to retrieve data from node 00-02 and it's timing out. Upon reviewing the Atlas cluster metrics, I'm seeing high memory pressure in node 00-00 causing an increase in page faults and swapping activity. This seems to be leading to high kernel CPU pressure in the node. As a result, it's expected for you to encounter some issues on retrieving data from this node.  
            
            With that being said, I'm seeing multiple query targeting alerts in the cluster which can be correlated with the high Query Targeting and Query Executor metrics:  
            
            https://sfsc-case-attachments.s3-accelerate.amazonaws.com/01240182%2FQuery+targeting+metrics.png  
            
            Please note the default Query Targeting alert is triggered when the average number of documents being examined exceeds the average number of documents being returned by a ratio of 1000:1, across all operations during a sampling period, server-wide. It's often a result of inefficient ops in need of improved indexing, but there are potentially other causes. It's also worth noting that only operations that take longer than the slowms threshold are actually logged, such that the responsible operations may not actually be logged.  
            
            The Atlas Query Profiler is directly populated with the logged operations in the mongodb.log file(s). Therefore, if the operation(s) that triggered the Query Targeting alert aren't logged, they will not be displayed in the Atlas Query Profiler.  
            
            To understand how the Query Targeting alert is generated, we recommend reviewing the Alert Resolutions > Query Targeting documentation.  
            
            One resource for investigating remedies for these alerts would be to navigate to the cluster's Performance Advisor panel to determine possible indexes that could help query performance. Operations that take more than the threshold to complete are logged in the cluster's mongod logs, which is used by the Performance Advisor to suggest new indexes to improve query performance. I'm currently seeing 12 index suggestions in the Performance Advisor for this cluster.  
            
            Next Steps  
            As a short relief and in order to allow the cluster to recover a healthy status, you can either:  
            
            Reduce the workload.  
            Scale your cluster up to allocate more resources.  
            For a long term solution, you would need to implement the necessary indexes to improve your queries. You can start applying the 12 index recommendations from the Performance advisor and then reviewing the Atlas profiler to spot more potential slow queries.  
            
            From a preliminary analysis of your Atlas profiler, I'm seeing the most affected namespace is enlighten_preprod.email_logs. I'm seeing the Performance Advisor is recommending to create the following index for that particular namespace: {recipient: 1, time_sent: -1}. You may want to start creating that index and see if your performance improve and your cluster resources can handle the active workload.  
            
            Let me know if this clarifies things out or if you have further questions or concerns.  
            
            Best,  
            Alejo.  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            Aditya Nutulapati  
            12/22/2023 9:48 AM PST | User Time 12/22/2023 11:18 PM IST  
            
            NEUTRAL  
            EVERYONE  
            Hi Alejo,  
            Thanks for the insights. We got some information and we'll work on them. I would like to bring to your notice that, we were receiving another alert along with the one we mentioned earlier, please have a look.  
            
            Mongo::Error::OperationFailure: [292:QueryExceededMemoryLimitNoDiskUseAllowed]: Exceeded memory limit for $group, but didn't allow external sort. Pass allowDiskUse:true to opt in. (on preprod-info-1-shard-00-00.bxbxc.mongodb.net:27017, modern retry, attempt 1)  
            
            Please help us understand this issue  
            
            Thanks,  
            Aditya  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            Anastasia Kravtsov  
            12/24/2023 8:17 AM PST | User Time 12/24/2023 6:17 PM IST  
            
            NEUTRAL  
            EVERYONE  
            Hi Aditya,  
            
            Thank you for getting back to us. My name is Anastasia and I'm assisting my colleague Alejo with this case while he's unavailable.  
            
            I am reviewing the case history and will provide more details in a follow-up comment. Meanwhile, if you have any other questions or concerns, please let us know.  
            
            Best Regards,  
            Anastasia  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            Anastasia Kravtsov  
            12/24/2023 9:33 AM PST | User Time 12/24/2023 7:33 PM IST  
            
            NEUTRAL  
            EVERYONE  
            Hi Aditya,  
            
            I'm following up on this case.  
            
            we were receiving another alert along with the one we mentioned earlier, please have a look.  
            Mongo::Error::OperationFailure: [292:QueryExceededMemoryLimitNoDiskUseAllowed]: Exceeded memory limit for $group, but didn't allow external sort. Pass allowDiskUse:true to opt in. (on preprod-info-1-shard-00-00.bxbxc.mongodb.net:27017, modern retry, attempt 1)  
            
            The above Exceeded memory limit for $group error implies that you encountered the 100 megabytes limit of RAM for the $group stage, as documented here. For the respective $group stage you can allow pipeline processing to take up more space by using the allowDiskUse option to enable the ability for the aggregation to write data to temporary files.  
            
            However, please keep in mind that the allowDiskUse option is only supported for non-shared atlas clusters.  
            
            Please let us know if you have any additional questions or concerns regarding the details above.  
            
            Best Regards,  
            Anastasia  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            Anastasia Kravtsov  
            12/24/2023 9:35 AM PST | User Time 12/24/2023 7:35 PM IST  
            
            NEGATIVE  
            INTERNAL  
            INTERNAL  
            Exceeded memory limit for $group, but didn't allow external sort. Pass allowDiskUse:true to opt in  
            https://support.mongodb.com/case/01046542?c__ccId=CC-3356998  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            MongoDB Support  
            12/28/2023 10:16 AM PST | User Time 12/28/2023 1:16 PM EST  
            
            NEUTRAL  
            EVERYONE  
            Hello,  
            
            This is an automated reminder that this ticket is awaiting your response. Please respond to this ticket so that we can continue working on this issue with you, or let us know if the ticket can be resolved.  
            
            Thanks,  
            MongoDB Support  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            MongoDB Support  
            12/28/2023 10:16 AM PST | User Time 12/28/2023 1:16 PM EST  
            
            NEUTRAL  
            INTERNAL  
            AutoCloseSF1 state performed, the following actions were taken:  
            
            First customer notification sent  
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            Anastasia Kravtsov  
            12/28/2023 11:27 AM PST | User Time 12/28/2023 9:27 PM IST  
            
            NEUTRAL  
            EVERYONE  
            Hi Aditya,  
            
            Hope you're doing well.  
            
            Since I haven't heard back from you for a while, I wanted to check in on the state of this case.  
            
            Please let me know whether you've any additional questions or whether I can proceed to mark this case as closed.  
            
            I look forward to hearing from you soon.  
            
            Best Regards,  
            Anastasia  
            
            View Markdown  
            Open in SFSC  
            Copy Link  
            case-comment-avatar  
            Anastasia Kravtsov  
            12/31/2023 5:59 AM PST | User Time 12/31/2023 3:59 PM IST  
            
            NEUTRAL  
            EVERYONE  
            Hi Aditya,  
            
            Hope you're doing well.  
            
            Since we have not heard back from you with any additional questions, we will go ahead and close this case.  
            
            Please don't hesitate to open a new case via the Support Portal in the future should you need any further assistance.  
            
            Thanks for using MongoDB Atlas Support! """,
    "kbOutput": """ { 
                "question": "The customer is experiencing timeout errors in their applications, specifically related to MongoDB operations. They are seeking assistance to understand and resolve the issue, which is causing a high error rate and affecting alpha users.",  
                "solution": "The support team identified that the timeout errors were due to high memory pressure in node 00-00, leading to increased page faults and swapping activity. They also mentioned alerts related to query targeting and memory limit for $group stage. Recommendations were provided to reduce workload, scale up the cluster, and implement necessary indexes to improve query performance. Additionally, the customer was advised to use the allowDiskUse option for the $group stage to enable writing data to temporary files, but this option is only supported for non-shared Atlas clusters. The case was closed after the customer did not respond to the last follow-up."  
                 } 
            """
     }
]

kbExamplePrompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{kbInput}"),
        ("ai", "{kbOutput}"),
    ]
)

few_shot_prompt_kbSummary = FewShotChatMessagePromptTemplate(  
    example_prompt=kbExamplePrompt,
    examples=kbExamples
    
)

final_prompt_kb_summary = ChatPromptTemplate.from_messages(
    [
        ("system",kbPrompt),
        few_shot_prompt_kbSummary,
        ("human", "{kbInput}"),
    ]
)

kbchain = final_prompt_kb_summary | model |  StrOutputParser() 




add_routes(
    app,
    kbchain,
    path="/kb-summary",
)



MONGO_URI = os.environ["MONGO_URI"]

# Note that if you change this, you also need to change it in `rag_mongo/chain.py`
DB_NAME = "curated_data"
COLLECTION_NAME = "knowledgebase"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
MONGODB_COLLECTION = db[COLLECTION_NAME]

CHAT_API_VERSION = os.environ["CHAT_API_VERSION"]
CHAT_END_POINT = os.environ["CHAT_END_POINT"]
CHAT_DEPLOYMENT = os.environ["CHAT_DEPLOYMENT"]


#vector_search = MongoDBAtlasVectorSearch.from_connection_string(
#    MONGO_URI,
#    DB_NAME + "." + COLLECTION_NAME,
#    AzureOpenAIEmbeddings(disallowed_special=()),
#    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
#)

embeddings = AzureOpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
# Initialize the Vector Store
vector_search = MongoDBAtlasVectorSearch(collection = MONGODB_COLLECTION, embedding = embeddings,
                                       text_key = 'question',
                                       embedding_key = 'embedding', 
                                       index_name= ATLAS_VECTOR_SEARCH_INDEX_NAME)

# def parse_json(data):
#    return json.loads(json_util.dumps(data))


def retrieve(query: str):
    
    results = vector_search.similarity_search(
        query,
        k=4,
        post_filter_pipeline=[
            {"$project": {"_id": 0}}]
    )
    return results


# RAG prompt
mongotemplate = """Answer the question as a Database technical engineer based only on the following context:
{context}
Question: {question}
"""
mongoprompt = ChatPromptTemplate.from_template(mongotemplate)


model = AzureChatOpenAI(
            azure_deployment=CHAT_DEPLOYMENT,
            openai_api_version=CHAT_API_VERSION,
            azure_endpoint=CHAT_END_POINT
            )



mongochain = (
    RunnableParallel({"context": retrieve, "question": RunnablePassthrough()})
    | mongoprompt
    | model
    | StrOutputParser()
)


# Add typing for input
class Question(BaseModel):
    __root__: str


rag_mongo_chain = mongochain.with_types(input_type=Question)



#from rag_mongo import chain as rag_mongo_chain
add_routes(app, rag_mongo_chain, path="/rag-mongo")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
