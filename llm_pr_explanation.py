"""
Module to create RAG app. for summarizing the input context,
and generating PR explanation.
"""
import os
import tiktoken
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.markdown import \
    UnstructuredMarkdownLoader
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain_ibm import WatsonxLLM


""" Load and Run LLM using Ollama """
# LLM = Ollama(model = "instructlab/granite-7b-lab")
# LLM = Ollama(model = "custom-granite-7b")
# LLM = Ollama(model = "mistral")
LLM = Ollama(model = "llama3.1:latest")

""" Load and Run LLM using WatsonLLM """
parameters = {
    "decoding_method": "greedy",  # Prompt Lab uses "greedy"
    "max_new_tokens": 200,
    "min_new_tokens": 1,
    "repetition_penalty": 1,
    "temperature": 1.0,
    "top_k": 50,
    "top_p": 1,
}

""" You can create your WatsonAI instance and run using your API key """
# WatsonXAI instance
# os.environ["WATSONX_APIKEY"] = "<API KEY>"
# LLM = WatsonxLLM(
#     # model_id="ibm/granite-7b-lab",
#     # model_id="granite-3b-code-instruct",
#     model_id="google/flan-ul2",
#     url="https://eu-de.ml.cloud.ibm.com",
#     project_id="<prodject-id>", # Replace with project id for sandbox project in your watsonx instance, e.g.
#     params=parameters,
# )

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    fn. to calculate token size for the given input
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def create_rag_chain(filename, path):
    """Creates a RAG chain for summarizing input based on the given context."""
    # Load and split the context
    loader = UnstructuredMarkdownLoader(
        os.path.join(path, filename),
        mode="elements",
        strategy="fast"
    )
    documents = loader.load()
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, overlap=0)
    # texts = text_splitter.split_text(documents[0].page_content)

    # Create embeddings and vector store
    embeddings=OllamaEmbeddings(model='nomic-embed-text')
    vectorstore = FAISS.from_documents(documents, embeddings)
    # Create LLM and RAG chain
    rag = RetrievalQA.from_llm(llm=LLM, retriever=vectorstore.as_retriever())

    return rag

def summarize_input(rag, context, user_input_text, standard_output, prompt_query, prompt_instructions):
    """Summarizes the input text based on the given context and query."""
    # embeddings=OllamaEmbeddings(model='nomic-embed-text')
    # Embed the input text
    # input_embedding = embeddings.embed(user_input_text)
    retriever = rag.retriever
    docs = retriever.invoke(prompt_query)
    # Combine context and input for LLM prompt
    prompt = f"""
    You are an Ansible Expert. Please read through the config rules
        context provided and suggest the summary of changes done by Ansible code bot,
        and how they improve the Ansible content.
    Context: {context}
    Input: {user_input_text}
    Question: {prompt_query}
    Relevant documents: {docs}
    Instructions: {prompt_instructions}

    Always, start the bulleted summary with statement: 'Ansible code bot has identified several rule violations in the repo playbooks. Here's a breakdown of the violations based on the relevant rules: ...
    """

    # prompt = f"""
    # You are an Ansible Expert. Please read through the config rules
    #     context provided and suggest the summary of changes done by Ansible code bot,
    #     and how they improve the Ansible content.
    # Context: {context}
    # Input: {user_input_text}
    # Question: {prompt_query}
    # Relevant documents: {docs}
    # Instructions: {prompt_instructions}
    # Use the following standard output format for reference,
    # and try to generate summary in similar format,
    # Standard Output reference: {standard_output}

    # You **should always**, start the summary with:
    # 'Ansible code bot has identified several rule violations in the repo playbooks. Here's a breakdown of the violations based on the relevant rules: ...
    # """

    # Generate summary using LLM
    print("** prompt_query_size ** ", num_tokens_from_string(input_query, "cl100k_base"))
    rag_summary = LLM(prompt)

    return rag_summary

PATH = "<PWD>"
# FILENAME = "config_data/lint-autofix-rules.md"
FILENAME = "config_data/ari-rules-context.md"
# FILENAME = "config_data/noexample-autofix-ari.md"

with open (os.path.join(PATH, FILENAME), 'r', encoding="utf-8") as f:
    input_context = f.read()
# with open (os.path.join(PATH, "config_data/git-diff-unified.txt"), 'r', encoding="utf-8") as f:
with open (os.path.join(PATH, "config_data/modified-ari.txt"), 'r', encoding="utf-8") as f:
    input_query = f.read()
with open (os.path.join(PATH, "config_data/ideal-summary-response.txt"), 'r', encoding="utf-8") as f:
    std_output = f.read()

input_text = input_query
INSTRUCTIONS = """
    1. You are an AI agent for the Ansible code bot. As the agent, you summarize briefly,\
    succinctly.
    2. You **should always** include the numbers of files from the input in the summary.
    3. You **should not** include the rule id in the summary, only the rule description.
    4. Summarize concisely, using bullet points. Avoid jargon.
    5. Don't include the config rule number itself, just the description of why the rules were\
    applied.
    6. You **should always** reference Bot config rules to come up with summary and results\
    based on relevant config rules.
    7. Your response should avoid being vague, controversial or off-topic.
    8. Your respinse **should not** include any code metadata.
"""
QUERY = """Please provide the summary of the input text based on the provided context."""

rag_chain = create_rag_chain(FILENAME, PATH)
summary = summarize_input(rag_chain, input_context, input_text, std_output, QUERY, INSTRUCTIONS)

# Output the final LLM response
print(summary)
