from llama_index.tools import QueryEngineTool, ToolMetadata
import chainlit as cl
from chainlit.input_widget import Select, TextInput
import openai
from llama_index.agent import ReActAgent
from llama_index.llms import OpenAI
from llama_index.callbacks.base import CallbackManager
from index_wikipages import create_index
from utils import get_apikey

# define the data model in pydantic
class WikiPageList(BaseModel):
    "Data model for WikiPageList"
    pages: list


def wikipage_list(query):
    openai.api_key = get_apikey()

    prompt_template = prompt_template_str = """
    Given the input {query}, 
    extract the Wikipedia pages mentioned after 
    "please index:" and return them as a list.
    If only one page is mentioned, return a single
    element list.
    """
    program = OpenAIPydanticProgram.from_defaults(output_cls=WikiPageList, prompt_template_str=prompt_template, verbose=True)
    wikipage_requests = program(query=query)

    return wikipage_requests


def create_wikidocs(wikipage_requests):
    WikipediaReader = download_loader("WikipediaReader")
    loader = WikipediaReader()
    documents = loader.load_data(pages=wikipage_requests)
    return documents


def create_index(query):
    global index
    wikipage_requests = wikipage_list(query)
    documents = create_wikidocs(wikipage_requests)
    text_splits = get_default_text_splitter(chunk_size=150, chunk_overlap=45)
    parser = SimpleNodeParser.from_defaults(text_splitter=text_splits)
    service_context = ServiceContext.from_defaults(node_parser=parser)
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    return index


if __name__ == "__main__":
    query = "/get wikipages: paris, lagos, lao"
    index = create_index(query)
    print("INDEX CREATED", index)
