from langchain.agents import AgentExecutor,create_tool_calling_agent,tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate   
from langchain_community.document_loaders.figma import FigmaFileLoader
import os
import requests
from dotenv import load_dotenv
import re
load_dotenv()
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")

@tool
def search(query: str) -> str:
    """只有需要了解实时信息或不知道的事情的时候才会使用这个工具."""
    serp = SerpAPIWrapper()
    return serp.run(query)

@tool
def get_info_from_local(query: str) -> str:
    """只有文档站相关内容是才会使用这个工具"""
    client = QdrantClient(path="./src/temp/qdrant")
    retriever_qr = QdrantVectorStore(client, "local_documents_demo2", OpenAIEmbeddings())
    retriever = retriever_qr.as_retriever(search_type="mmr")
    result = retriever.get_relevant_documents(query)
    print('get_info_from_local', result)
    return result

@tool
def get_figma_code(query: str) -> str:
    """只有用户要用figma设计稿生成代码时用这个工具"""
    # https://www.figma.com/design/y1sIQbz90B7jf1d3zgyo16/%E8%BF%90%E8%90%A5%E4%B8%AD%E5%BF%83?node-id=3-8473&m=dev
    pattern = r"https://www\.figma\.com/design/([a-zA-Z0-9]+).+?node-id=([0-9\-]+)"
    print('get_figma_code', query)
    match = re.search(pattern, query)
    print('get_figma_code000', match)

    file_id = match.group(1)  # 提取 files 后面的 id
    node_ids = match.group(2)  # 提取 ids 后面的值
    print('get_figma_code2', file_id, node_ids)

    figma_loader = FigmaFileLoader(os.environ.get('FIGMA_ACCESS_TOKEN'), node_ids, file_id)
    list = figma_loader.load()
    page_content = list[0].page_content
    prompt = f"""
    下面是根据figma api获取的页面json信息,请根据下面信息100%还原设计稿，不要有偏差，都则你将收到惩罚
    {page_content}
    """
    return prompt

@tool
def jiemeng(query: str):
    """只有帮助用户解梦的时候才会使用这个工具，需要输入梦境内容."""
    url = f"https://api.yuanfenju.com/index.php/v1/Gongju/zhougong"
    LLM = ChatOpenAI(
            model="gpt-4-1106-preview", 
            temperature=0, 
            streaming=True
        )
    prompt = ChatPromptTemplate.from_template("根据输入的内容提取1个关键词，只返回关键词，输入内容:{topic}")
    prompt_value = prompt.invoke({"topic": query})
    keyword = LLM.invoke(prompt_value)
    print("=======提交数据=======")
    print(keyword.content)
    result = requests.post(url, data={"api_key": os.getenv("API_KEY"), "title_zhougong": keyword.content})
    if result.status_code == 200:
        print("=======返回数据=======")
        return result.text
    else:
        return "用户输入的信息缺失，提醒用户补充信息！"