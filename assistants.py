from flask import Flask, request
from flask_cors import CORS
from markupsafe import escape
from dotenv import load_dotenv
import os
from openai import OpenAI
from flask import Response
from uuid import uuid4
import datetime

app = Flask(__name__)

CORS(app)
load_dotenv()
client = OpenAI()

#initial setup for assistants api
assistant = client.beta.assistants.create(
    name="RUSH B",
    instructions="RUSH-B, specifically designed as an assistant for BoardSpace, now exclusively uses data from https://boardspace.freshdesk.com/support/solutions and its related links to answer user queries. It conducts internal searches within this domain, avoiding external search engines like Bing, to ensure information is directly relevant to BoardSpace's context. RUSH-B thoroughly explores these resources before concluding that information related to a query is unavailable. This focused approach guarantees the most comprehensive and relevant answers, prioritizing reliability and accuracy. RUSH-B maintains a friendly, professional demeanor, offering straightforward answers without humor. Its profile picture, featuring a stylized 'B' on a blackboard with a condo floorplan background, symbolizes its dedication to efficient condo board management through BoardSpace.",
    model="gpt-4-1106-preview"
)

#initiates conversation when api loads
thread = client.beta.threads.create()

@app.route('/message')
def message(content):
    message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=content
    )

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)




@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'

