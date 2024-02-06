# chatbot

## RUSH-B: The BoardSpace chatbot
Rush-B is a chatbot designed to answer support and ticketing questions for the BoardSpace condo management platform. It features a simple user interface where users can ask the chatbot questions. It is powered by a custom chatbot created using Python's LangChain library and utilizing OpenAI's GPT-3.5-Turbo LLM.

RUSH-B is trained on a knowledge base consisting of more than 100 BoardSpace support documents from this [link](https://boardspace.freshdesk.com/support/solutions). The documents are merged into a single PDF file, and that file is then broken down into chunks of up to 2000 characters, ensuring that the splits always occur on paragraph breaks to preserve semantic meaning. These chunks are then vectorized via OpenAI's ada-v2 embedding model, and then loaded into a vector database, which supports similarity matching between questions that users provide and the chunks stored in the database.

When a user asks a question, the similarity matching retrieves sections of the support documentation that have the highest similarity score with the question to provide as additional context. This context is then fed into the GPT-3.5 LLM to generate a clear and concise response to the user.

## How to use:
1. Open a new terminal and run the following command: `python assistantsv2.py`
2. Go to the URL that is displayed on the terminal (typically it will be `localhost:5000` or `127.0.0.1:5000`)
3. You will see a user interface. Type the query you wish to ask into the chat box, and when you are finished typing click the send button.
4. Wait for the response from the LLM. It can take a few seconds. If there are any errors, the chatbot's response will state the error that occurred.
   



