# Virtual Assistant

## General

Virtual Assistant (VA), created as a part of \"Model-Based Execution Platform for Space Applications\" project (contract 4000146882/24/NL/KK) financed by the European Space Agency.

VA is meant to support the requirement engineering process, using ECSS, and any other provided knowledge. It can be used in a both standalone mode, and integrated within SpaceCreator (see ESA's TASTE toolset)

## Warning

Software uses Large Language Models to serve the user queries and so it is susceptible to LLM hallucinations and various other errors. The provided answers, even if looking plausible or convincing, may be incorrect. Therefore the software should be used only as a non-binding linter to facilitate work, not replace it. Each answer needs to be interpreted by the human operator as a suggestion, and verified before taking any action.

## Installation

### vareq
Virtual Assistant (vareq) can be installed using one of 3 methods, as indicated in the makefile:
- make install-pipx - installs vareq using pipx (default target for make)
- make install-native - installs vareq natively using pip
- make install-venv - installs vareq in a Python virtual environment

The above options allow vareq to be installed both on Windows and Linux, supporting various system configurations.

### Ollama

In order to function, vareq requires Ollama. For installation instructions, please refer to https://ollama.com/
Ollama needs to be installed and started separately. Ollama is a host for the used Large Language Models (LLMs). The models need to be installed separately. The default configuration requires the following models to run:
- qwen3:0.6b - for text generation
- nomic-embed-text - for embeddings

Qwen3:0.6b is selected as the default to enable execution "out-of-the-box", even on legacy hardware. Virtual Assistant is intended to be deployed alongside Mistral:7b or a better LLM.

## Configuration

Configuration is supplied via JSON provided either as a command line argument or a file. It's schema is as follows:

```json
{
 "$schema": "http://json-schema.org/draft-04/schema#",
 "type": "object",
 "properties": {
 "augmented_chat_config": {
 "type": "object",
 "properties": {
 "max_knowledge_items": { # Maximum number document items provided for chat as context
 "type": "integer"
 },
 "max_knowledge_size": { # Maximum combined size of document items provided for chat as context
 "type": "integer"
 },
 "use_documents": { # Use text documents from the document directories as chat context
 "type": "boolean"
 },
 "use_requirements": { # Use requirements as chat context
 "type": "boolean"
 }
 },
 "required": [
 "max_knowledge_items",
 "max_knowledge_size",
 "use_documents",
 "use_requirements"
 ]
 },
 "batch_query_context_size": { # Maximum number of requirements processed together in a batch query
 "type": "integer"
 },
 "chat_config": {
 "type": "object",
 "properties": {
 "history_summarization_template": { # Template for chat history summarization
 "type": "string"
 },
 "query_template": { # Chat query template
 "type": "string"
 },
 "remove_thinking": { # Remove the thinking part of the LLM reply, if present
 "type": "boolean"
 }
 },
 "required": [
 "history_summarization_template",
 "query_template",
 "remove_thinking"
 ]
 },
 "document_directories": { # List of directories to search for the document items
 "type": "array",
 "items": {}
 },
 "lib_config": {
 "type": "object",
 "properties": {
 "chunk_overlap": { # Size of the overlap in chunks that the document items are divided into
 "type": "integer"
 },
 "chunk_size": { # Maximum size of a document item chunk
 "type": "integer"
 },
 "persistent_storage_path": { # Path to Vector DB storage
 "type": "string"
 },
 "requirement_document_mappings": {
 "type": "object",
 "properties": {
 "description": { # Column name containing requirement descriptions
 "type": "string"
 },
 "first_row_number": { # First row with requirements
 "type": "integer"
 },
 "id": { # Column name containing requirement IDs
 "type": "string"
 },
 "justification": { # Column name containing requirement justifications
 "type": "string"
 },
 "note": { # Column name containing requirement notes
 "type": "string"
 },
 "trace_separator": { # Symbol used to separate individual traces
 "type": "string"
 },
 "traces": { # Column name containing requirement traces
 "type": "string"
 },
 "type": { # Column name containing requirement types
 "type": "string"
 },
 "validation_type": { # Column name containing requirement validation types
 "type": "string"
 },
 "worksheet_name": { # Name of the worksheet containing the requirements
 "type": "string"
 }
 },
 "required": [
 "description",
 "first_row_number",
 "id",
 "justification",
 "note",
 "trace_separator",
 "traces",
 "type",
 "validation_type",
 "worksheet_name"
 ]
 }
 },
 "required": [
 "chunk_overlap",
 "chunk_size",
 "persistent_storage_path",
 "requirement_document_mappings"
 ]
 },
 "llm_config": {
 "type": "object",
 "properties": {
 "chat_model_name": { # LLM model to use for chat
 "type": "string"
 },
 "embeddings_model_name": { # LLM model to use for embeddings
 "type": "string"
 },
 "temperature": { # LLM model temperature
 "type": "number"
 },
 "url": { # URL of remote Ollama server (if used)
 "type": "string" or “null”
 }
 },
 "required": [
 "chat_model_name",
 "embeddings_model_name",
 "temperature",
 "url"
 ]
  },
 },
 "required": [
 "augmented_chat_config",
 "batch_query_context_size",
 "chat_config",
 "document_directories",
 "lib_config",
 "llm_config",
 ]
}
```

Example configuration is provided in the data folder.

## Running

### Command Line Interface (CLI)
Once installed, vareq command should be available. The command line interface is documented in the built-in help:
```
  -h, --help            show this help message and exit
  --mode {chat,query,serve,reset-db,dump-config}
                        Operating mode
  --requirements REQUIREMENTS
                        Path to the requirements file (overrides config)
  --document-directories DOCUMENT_DIRECTORIES
                        Comma separated list of directories (overrides config)
  --model MODEL         LLM model name to use (overrides config)
  --query-definitions-base-directory QUERY_DEFINITIONS_BASE_DIRECTORY
                        Base directory to resolve references within query definitions
  --query-definitions-path QUERY_DEFINITIONS_PATH
                        Path to query definitions
  --config-path CONFIG_PATH
                        Path to config file
  --config-json CONFIG_JSON
                        Config JSON string
  --server-config-json SERVER_CONFIG_JSON
                        Server config JSON string
  --query-id QUERY_ID   Query ID for query mode
  --requirement-id REQUIREMENT_ID
                        Requirement ID for query mode
  --setup-instructions  Print installation instructions
  --verbosity {info,debug,warning,error}
                        Logging verbosity
```

### REST API

In order to support possible integrations, Virtual Assistant exposes its functionality via REST API. In such case, vareq needs to be started in **serve** mode, and additional server configuration needs to be provided via "--server-config-json" argument:
```json
{
 "$schema": "http://json-schema.org/draft-04/schema#",
 "type": "object",
 "properties": {
 "host": { # Host to bind the server to
 "type": "string"
 },
 "port": { # Port to bind the server to
 "type": "integer"
 },
 "debug": { # Provide debug information
 "type": "boolean"
 }
 },
 "required": [
 "host",
 "port",
 "debug"
 ]
}

```

The available endpoints, served via Flask, are as follows:
- GET /areyoualive/ - performs simple health check
- GET /query/<<string:query_id>>/ - performs a query on all requirements
- GET /query/<<string:query_id>>/<<string:requirement_id>>/  - performs a query on a specific requirement
- GET /reload/ - reloads configuration (including queries and requirements)
- GET /chat/<string:query>/ - sends a chat message

All arguments need to be URL encoded, so e.g., chat query "List all functional requirements" shall be provided as /chat/List%20all%20functional%20requirements (note spaces replaced with %20 and lack of ""). All queries respond with JSON.

#### -Are you alive-
/areyoualive/ (GET) 

Purpose: Health check endpoint to verify server availability. 

Response JSON Structure: 
```
{ 
  "status": "ok" 
} 
```

Field Descriptions: 
- status (string): Always returns "ok" when server is responsive 

#### -Reload-
/reload/ (GET) 

Purpose: Reloads the server context, reinitializing the engine and reloading requirements.

Success Response JSON Structure: 
```
{ 
  "status": "ok" 
} 
```

Error Response JSON Structure: 
```
{ 
  "status": "failed", 
  "error": "Error message describing what went wrong" 
} 
```

Field Descriptions: 
- status (string): Either "ok" for success or "failed" for errors 
- error (string, optional): Present only on failure, contains the error message 

#### -Chat-

/chat/<<string:query>>/ (GET) 

Purpose: Answers a free standing query using automatically retrieved context.

Success Response JSON Structure: 
```
{ 
  "query": "user's query string", 
  "reply": "AI assistant's response", 
  "references": ["reference text 1", "reference text 2", ...], 
  "reference_names": ["reference name 1", "reference name 2", ...], 
  "status": "ok" 
} 
```

Error Response JSON Structure: 
```
{ 
  "query": "user's query string", 
  "status": "failed", 
  "error": "error message" 
} 
```

Field Descriptions: 
- query (string): The decoded user query from the URL path 
- reply (string): The assistant's response text (only present on success) 
- references (array of strings): Full text of relevant documents/requirements used as context 
- reference_names (array of strings): Names/titles of the referenced documents 
- status (string): Either "ok" or "failed" 
- error (string, optional): Error message when status is "failed" 

#### -Unary query-
/query/<<string:query_id>>/<<string:requirement_id>> (GET)

Purpose: Execute a predefined query against a specific requirement. The list of available queries is provided in the configuration.

Success Response JSON Structure: 
```
{ 
  "query_id": "query identifier", 
  "requirement_id": "requirement identifier", 
  "status": "ok", 
  "reply": "analysis result or response text", 
  "error": null 
}
```

Error Response JSON Structure: 
```
{ 
  "query_id": "query identifier", 
  "requirement_id": "requirement identifier", 
  "status": "failed", 
  "reply": null, 
  "error": "Requirement not found" // or "Query not found" or "Processing failed" 
} 
```

Field Descriptions for Unary Query: 
- query_id (string): The identifier of the predefined query 
- requirement_id (string): The ID of the specific requirement being analyzed 
- status (string): Either "ok"" or "failed"` 
- reply (string, nullable): The analysis result or LLM response text 
- error (string, nullable): Error message describing the failure 

#### -N-ary Query-

/query/<<string:query_id>>/ (GET)

Purpose: Execute a predefined query against all loaded requirements (batch processing).

Presentation of the response, including filtering and field visibility, is to TBD by the software integration. The following recommendations may be followed:
- Each response element which has a non-empty applied requirements list shall be presented to the user.
- Response elements with an empty list of applied requiements shall be hidden from the user.
- If the same pair of requirements is present twice in the response (as the "main" and "applied" requirement, and the other way round), it is possible to show only one.
- ID of each shown requirement (main or applied) shall be shown.
- Description of each shown requirement (main or applied) should be shown. 
- Presentation of context requirements should be optional, as the feature is intended as a debugging facility, however, it still may provide insight to the user.
- Embeddings should not be presented, as the feature is intended as a debugging facility, which is not human readable in case of a practical deployment.
- Other fields (e.g., justification, traces) may be available in additional controls hidden by default (e.g., floating hint, collapsed panel, additional window, etc).

Success Response JSON Structure: 
```
{ 
  "query_id": "query identifier", 
  "status": "ok", 
  "reply": [ 
    { 
      "requirement": { 
        "id": "requirement identifier", 
        "type": "requirement type", 
        "validation_type": "validation type", 
        "description": "requirement description", 
        "note": "additional notes", 
        "justification": "requirement justification", 
        "traces": ["parent requirement identifier 1", "parent requirement identifier 2"] 
      }, 
      "embedding": [0.1, 0.2, 0.3, ...], 
      "applied_requirements": [ 
        { 
          "id": "requirement identifier", 
          "type": "requirement type", 
          "validation_type": "validation type", 
          "description": "requirement description", 
          "note": "additional notes", 
          "justification": "requirement justification", 
          "traces": ["parent requirement identifier 1"] 
        } 
      ], 
      "message": "analysis result or detection message", 
      "context_requirements": [ 
        { 
          "id": "requirement identifier", 
          "type": "requirement type", 
          "validation_type": "validation type", 
          "description": "requirement description", 
          "note": "additional notes", 
          "justification": "requirement justification", 
          "traces": ["parent requirement identifier 1"] 
        } 
      ] 
    } 
  ], 
  "error": null 
} 
```

Error Response JSON Structure: 
```
{ 
  "query_id": "query identifier", 
  "status": "failed", 
  "reply": null, 
  "error": "Query not found" // or "Processing failed" 
} 
```

Field Descriptions for N-ary Query: 
- query_id (string): The identifier of the predefined query 
- status (string): Either "ok" or "failed" 
- reply (array of objects, nullable): Array of BatchResponseElement objects converted to dictionaries 
- error (string, nullable): Error message when processing fails 

BatchResponseElement Structure (each item in reply array): 
- requirement (object): The primary requirement being analyzed 
- id (string): Unique requirement identifier 
- type (string, nullable): Requirement type (e.g., "functional") 
- validation_type (string, nullable): Validation method (e.g., "T" for test) 
- description (string): Main requirement description 
- note (string, nullable): Additional notes 
- justification (string, nullable): Rationale for the requirement 
- traces (array of strings): List of parent requirement identifiers 
- embedding (array of floats): Vector embedding of the requirement description 
- applied_requirements (array of objects): Requirements that matched/triggered for this analysis; Each object has the same structure as requirement above 
- message (string, nullable): Detection message
- context_requirements (array of objects): Similar requirements used as context for analysis; Each object has the same structure as requirement above 
 

## Frequently Asked Questions (FAQ)

None

## Troubleshooting

In case of any issues, please follow this step-by-step guide as a starting point of troubleshooting:
- Set verbosity to error - are any issues reported?
- Check whether Ollama is installed and running.
- Check whether the desired LLMs (both for text generation and embedding) are deployed to Ollama.
- Check whether the desired LLMs execute on Ollama (deployed LLMs may not execute properly when they run out of memory).
- Check whether the provided configuration is read properly using --mode dump-config option.
- Check for any typos in the provided queries, paths and arguments.

When submitting an issue, please include vareq output produced with verbosity set to debug.