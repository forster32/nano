from qdrant_client import QdrantClient

import autogen
from autogen.agentchat.contrib.qdrant_retrieve_user_proxy_agent import QdrantRetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent

# Accepted file formats for that can be stored in
# a vector database instance
from autogen.retrieve_utils import TEXT_FORMATS

config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")

assert len(config_list) > 0
print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])

print("Accepted file formats for `docs_path`:")
print(TEXT_FORMATS)


# 1. create an RetrieveAssistantAgent instance named "assistant"
assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    },
)

# 2. create the QdrantRetrieveUserProxyAgent instance named "ragproxyagent"
# By default, the human_input_mode is "ALWAYS", which means the agent will ask for human input at every step. We set it to "NEVER" here.
# `docs_path` is the path to the docs directory. It can also be the path to a single file, or the url to a single file. By default,
# it is set to None, which works only if the collection is already created.
#
# Here we generated the documentations from FLAML's docstrings. Not needed if you just want to try this notebook but not to reproduce the
# outputs. Clone the FLAML (https://github.com/microsoft/FLAML) repo and navigate to its website folder. Pip install and run `pydoc-markdown`
# and it will generate folder `reference` under `website/docs`.
#
# `task` indicates the kind of task we're working on. In this example, it's a `code` task.
# `chunk_token_size` is the chunk token size for the retrieve chat. By default, it is set to `max_tokens * 0.6`, here we set it to 2000.
# We use an in-memory QdrantClient instance here. Not recommended for production.
# Get the installation instructions here: https://qdrant.tech/documentation/guides/installation/
ragproxyagent = QdrantRetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    retrieve_config={
        "task": "code",
        "docs_path": [
            "https://raw.githubusercontent.com/microsoft/flaml/main/README.md",
            "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Research.md",
        ],  # change this to your own path, such as https://raw.githubusercontent.com/microsoft/autogen/main/README.md
        "chunk_token_size": 2000,
        "model": config_list[0]["model"],
        "client": QdrantClient(":memory:"),
        "embedding_model": "BAAI/bge-small-en-v1.5",
    },
    code_execution_config=False,
)

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

qa_problem = "Is there a function called tune_automl?"
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=qa_problem)