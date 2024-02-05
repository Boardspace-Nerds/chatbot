from flask import Flask, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
from langchain_community.document_loaders import PDFMinerLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.vectorstores import VectorStoreRetriever
from sqlalchemy import UUID

app = Flask(__name__)

CORS(app)
load_dotenv()

loader = PDFMinerLoader("static/knowledge.pdf")
document = loader.load()

# splits documents into smaller "chunks", preserving semantic meaning of the text based on paragraphs
text_splitter = CharacterTextSplitter(
    separator="\\n\\n",
    chunk_size=2000,
    chunk_overlap=300,
    length_function=len,
    is_separator_regex=False,
)
doc_chunks = []
chunks = text_splitter.create_documents([str(document)])
for chunk in chunks:
    doc_chunks.append(chunk)

print(len(doc_chunks))

#embed and store into vector database
db = FAISS.from_documents(doc_chunks, OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY')))

#defines the llm and sets it up with our database retriever
llm = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0,
    max_tokens=512,
    api_key=os.getenv('OPENAI_API_KEY')
)

instructions = """RUSH-B is a support chatbot for BoardSpace, a condo board management platform. RUSH-B will respond to questions using the provided knowledge base, rather than searching Bing for answers. Upon receiving a question, RUSH-B should examine relevant parts of the documentation to construct a meaningful response that can help the customer, rather than simply instructing them to consult the documentation. RUSH-B maintains a friendly, professional demeanor, offering straightforward answers without humor. RUSH-B should provide clear and concise answers without sacrificing any important details, preferably in under 200 words.

{context}

Question: {question}
"""

prompt = PromptTemplate(template=instructions, input_variables=['context', 'question'])

retriever = MultiQueryRetriever.from_llm(retriever=db.as_retriever(), llm=llm)

assistant = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
)

#main route for queries
@app.route('/message')
def message():
    content = request.args.get('content')
    return(assistant.run(content))

#test route to get document similarity between chunks and user prompts
@app.route('/similarity')
def getSimilarity():
    text = request.args.get('text')
    docs = db.similarity_search(text)
    return(docs[0].page_content)

#test route to view the contents of a particular chunk
@app.route('/chunk')
def getChunk():
    chunk = request.args.get('chunk')
    if (int(chunk) < len(doc_chunks)):
        return str(doc_chunks[int(chunk)])
    else:
        return "no matches found for chunk " + chunk

@app.route('/')
def hello():
    return render_template("ui.html", greetingMessage="Hello, I am RUSH-B, the BoardSpace chatbot. How can I help you today?", botReply="cyka blyat")

if __name__ == '__main__':
    app.run()