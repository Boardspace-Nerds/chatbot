from flask import Flask, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import time
from bs4 import BeautifulSoup

app = Flask(__name__)

CORS(app)
load_dotenv()
client = OpenAI()

# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("static/knowledge.pdf", "rb"),
  purpose='assistants'
)

#initial setup for assistants api
assistant = client.beta.assistants.create(
    name="RUSH B",
    instructions="RUSH-B is a support/customer service chatbot for BoardSpace, a condo board management platform. RUSH-B will use the knowledge base provided to best respond to user queries. RUSH-B thoroughly explores the files in the provided knowledge base before concluding that information related to a query is unavailable. RUSH-B should use the provided knowledge base to answer questions first, before searching other websites like Bing. It also should figure out and come up with a meaningful response to the user queries that summarizes the instructions in the documentation, rather than simply referring the users to the documentation page. This focused approach guarantees the most comprehensive and relevant answers, prioritizing reliability and accuracy. RUSH-B maintains a friendly, professional demeanor, offering straightforward answers without humor. Additionally, it should provide short and concise answers where possible, to ensure users can understand them, ideally in less than 150 words.",
    model="gpt-3.5-turbo-1106",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
)

#initiates conversation when api loads
thread = client.beta.threads.create()

@app.route('/message')
async def message():
    content = request.args.get('content')
    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=content
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while (run.status == 'queued' or run.status == 'in_progress'):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(run.status)
        time.sleep(0.1)
    
    if (run.status == 'completed'):
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
    elif (run.status == 'requires_action'):
        print("Action required")
    else:
        return "error sending message to chatbot!", 400

    return(str(messages.data[1].content[0].text.value) + '\n' + str(messages.data[0].content[0].text.value))

@app.route('/')
def hello():
    return render_template("ui.html", greetingMessage="Hello, I am RUSH-B, the BoardSpace chatbot. How can I help you today?", botReply="cyka blyat")

if __name__ == '__main__':
    app.run()