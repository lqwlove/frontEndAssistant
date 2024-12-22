from langchain_community.document_loaders import TextLoader
import asyncio
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
import re

async def add_md_file(path):
        mdLoador = TextLoader(
            path
        )
        docs = await mdLoador.aload()
        return docs


async def start():
       docs = await add_md_file('./src/doc/readme.md')

       client = QdrantClient(path='./src/temp/qdrant')
       collection_name = "local_documents_demo"
       client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
       
       qdrant = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=OpenAIEmbeddings(),
        )
       qdrant.add_documents([docs[0]])
    #    print(docs[0].page_content) 

def test():
    # 示例 HTML 字符串
    html_content = """
    123234
    <!DOCTYPE html>
    <html>
    <head><title>Sample Page</title></head>
    <body>
    <h1>Welcome to My Website</h1>
    <p>This is a sample HTML document.</p>
    </body>
    </html>
    45645
    """

    # 正则表达式匹配从 <!DOCTYPE html> 到 </html>
    pattern = r"<!DOCTYPE html>.*?</html>"

    # 使用 re.search 查找匹配项
    match = re.search(pattern, html_content, re.DOTALL)

    if match:
        print("Matched content:")
        print(match.group(0))
    else:
        print("No match found.")

test()
# asyncio.run(start())