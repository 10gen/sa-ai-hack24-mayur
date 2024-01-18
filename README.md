# support-app
## Description

Our team has built an Intelligent Next Gen Support Platform, that can uplift overall Customer and Internal  support Experience. 
This tool can be incorporated into either the internal Support Portal used by our internal customers like MongoDB Support Team, MongoDB Sales/Account Teams or can be demoed to external MongoDB’s customers to enhance their existing support infrastructure. With the use of GenAI models, we are able to offer intelligent sentiment analysis, role based summarization and Image and multimodal contexts to make the support data integrate with other data sources and provide very rich and business specific insights. 

## Installation

The demo primarily uses Atlas Data Platform to host the datasets in the database, host the react frontend, serverless functions and database triggers in the Atlas App Services, Atlas Search and Vector Search to provide full text and semantic search capabilities, Atlas CHarts to provide visualizations for Dashboards, Langchain and LangServe for genAI middleware and finally connectivity to Azure OpenAI and Google Gemini based LLM Models. For Installation please follow these steps:

1. Upload the collections datasets provided in the "Datasets" folder using mongoimport using the same namespaces as the filenames.
2. Create the Atlas Search and Vector Search indexes for "support" and "curated_data" databases.
3. Import the Charts Dashboards provided in the "Charts" folder.
4. Import the App Services Application that is provided in "ads-app-services" folder
5. Create the OpenAI gpt3.5+ model deployment and ada002 embedding model deployment in your Azure subscription
6. Create a new Google Gemini Vision model in your GCP Vertex AI subscription/project.
7. Create your LangServe container on Azure / GCP as follows: 

Install the LangChain CLI if you haven't yet

```bash
pip install -U langchain-cli
```

## Adding packages

```bash
# adding packages from 
# https://github.com/langchain-ai/langchain/tree/master/templates
langchain app add $PROJECT_NAME

# adding custom GitHub repo packages
langchain app add --repo $OWNER/$REPO
# or with whole git string (supports other git providers):
# langchain app add git+https://github.com/hwchase17/chain-of-verification

# with a custom api mount point (defaults to `/{package_name}`)
langchain app add $PROJECT_NAME --api_path=/my/custom/path/rag
```

Note: you remove packages by their api path

```bash
langchain app remove my/custom/path/rag
```

## Setup LangSmith (Optional)
LangSmith will help us trace, monitor and debug LangChain applications. 
LangSmith is currently in private beta, you can sign up [here](https://smith.langchain.com/). 
If you don't have access, you can skip this section


```shell
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your-api-key>
export LANGCHAIN_PROJECT=<your-project>  # if not specified, defaults to "default"
```

## Launch LangServe

```bash
langchain serve
```

## Running in Docker

This project folder includes a Dockerfile that allows you to easily build and host your LangServe app.

### Building the Image

To build the image, you simply:

```shell
docker build . -t my-langserve-app
```

If you tag your image with something other than `my-langserve-app`,
note it for use in the next step.

### Running the Image Locally

To run the image, you'll need to include any environment variables
necessary for your application.

In the below example, we inject the `OPENAI_API_KEY` environment
variable with the value set in my local environment
(`$OPENAI_API_KEY`)

We also expose port 8080 with the `-p 8080:8080` option.

```shell
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8080:8080 my-langserve-app
```
