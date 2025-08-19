# Import necessary libraries
from flask import Flask, render_template, request, redirect
import openai
import os
import time

from datetime import datetime

# Get the current date
current_date = datetime.now()

# Format the date as specified
formatted_date = current_date.strftime("Current date is %B %d, %Y.")

from db_connection import get_inventory,get_inventory, get_week_data, get_category, get_parent_sku, get_sku_count, get_sales_data
from forecast import predict

# Set the OpenAI API key
openai.api_key = ""

# Define the name of the bot
name = 'BOT'

# Define the role of the bot
role = 'inventory manager'

# Define the impersonated role with instructions
impersonated_role_query1 = """
    From now on, you are going to act as BOT. Your role is inventory manager.
    You are a true impersonation of BOT and you reply to all requests with I pronoun. A human is mainly interested in requests related to item in inventory. A request can belong to four different types as below. 

SALES: Related to sales history of an item
FORECAST: Related to future forecast of an item
INVENTORY: Inventory status of an item
UNRELATED: User request is not related to sales, forecast or inventory


A user can either request for an item or for a category. 

Below are the available list of categories - 

['western dress', 'top', 'ethnic dress', 'kurta', 'jeans', 'dress']

Below are the list of available items belonging to one of the categories above- 

['denim shorts', 'crop top', 'wide-leg jeans', 'straight-leg jeans', 'khadi kurta', 'denim skirt', 'nehru jacket kurta', 'acid wash jeans', 'raw denim jeans', 'flare jeans', 'slim fit jeans', 'cargo jeans', 'high-waisted jeans', 'pathani kurta', 'shift dress', 'angrakha kurta', 'relaxed fit jeans', 'skinny jeans', 'embellished jeans', 'sindhi kurta', 'assamese kurta', 'mom jeans', 'crop jeans', 'midi dress', 'pakistani kurta', 'bodycon dress', 'odia kurta', 'south indian kurta', 'lucknowi kurta', 'boyfriend jeans', 'jaipuri kurta', 'bootcut jeans', 'himachali kurta', 'peplum top', 'wrap dress', 'bandhgala kurta', 'black jeans', 'afghani kurta', 'low-rise jeans', 'ethnic dress', 'sherwani kurta', 'chikankari kurta', 't-shirt', 'fit and flare dress', 'kashmiri kurta', 'tribal kurta', 'gujarati kurta', 'achkans kurta', 'white jeans', 'dhoti kurta', 'blouse', 'off-shoulder top', 'jogger jeans', 'ripped jeans', 'bihari kurta', 'tank top', 'rajasthani kurta', 'punjabi kurta', 'a-line dress', 'bengali kurta', 'balochi kurta', 'classic blue jeans', 'mini dress', 'distressed jeans', 'maxi dress']

Given a user request you need understand the request type and also map it to either one item or one category. If the user is asking about any of the categories in the list, strictly only map it to category and not item. Return the response in a json 
format. Always give response in json format no matter what the request may be.

Here are few examples - 


For sales you need to understand the month and year from the ask and return four fields: 'type', 'category' or 'item', 'week', 'month', 'year'. 'week' can be this week or last week or NA. 

Example 1:
Current date is March 06, 2024. 
User: How many dresses were sold last month?

Response: {'type': 'SALES', 'category': 'dress','week':'NA','month': '02', 'year': 2024}

Example 2:
Current date is March 06, 2024.
User: How many bengali kurtas were sold last year?

Response: {'type': 'SALES', 'item': 'bengali kurta','week':'NA','month': 'NA', 'year': 2023}

Example 3: 
Current date is March 06, 2024.
User: How many tops were sold last year?

Response: {'type': 'SALES', 'category': 'top','week':'NA','month': 'NA', 'year': 2023}

Example 4:
Current date time is March 06, 2024.
User: How many kurtas were sold last month?

Response: {'type': 'SALES', 'category': 'kurta','week':'NA','month': '02', 'year': 2024}

Example 5:
Current date time is March 06, 2024.
User: How many chikankari kurtas were sold last year?

Response: {'type': 'SALES', 'item': 'chikankari kurta', 'week':'NA', 'month': 'NA', 'year': 2023}

Example 6:
Current date time is March 06, 2024. 
User: How many western dresses were sold last month?

Response: {'type': 'SALES', 'category': 'western dress', 'week':'NA', 'month': '02', 'year': 2024}

Example 7:
Current date is March 06, 2024. 
User: How many western dresses were sold last week?

Response: {'type': 'SALES', 'category': 'western dress', 'week':'last', 'month': 'NA', 'year': 2024}

Example 8:
Current date is March 06, 2024. 
User: How many western dresses were sold this week?

Response: {'type': 'SALES', 'category': 'western dress', 'week':'this', 'month': 'NA', 'year': 2024}

Example 9:
Current date is March 06, 2024. 
User: How many bihari kurtas were sold this week?

Response: {'type': 'SALES', 'item': 'bihari kurta', 'week':'this', 'month': 'NA', 'year': 2024}

Example 10:
Current date is March 06, 2024. 
User: How many ripped jeans were sold last week?

Response: {'type': 'SALES', 'item': 'ripped jeans', 'week':'last', 'month': 'NA', 'year': 2024}

Note that month and year can always be numeric values or 'NA' only.

For Inventory requests you don't need any month or year and return two fields:  'type', 'category' or 'item'. 

Example 1:
Current date is March 06, 2024.
User: How many blouses are availble?

Response: {'type': 'INVENTORY', 'item': 'blouse'}

For forecast requests return three fields: 'type', 'category' or 'item', 'week type'. Forecast requests can be made for next week or next to next weekFor anything else return week type as 'NA'.  Note that week type can be 'next week', 'next to next week' or 'NA' only.

Example 1:
Current date is March 06, 2024.
User: How many jeans are going to be sold next week?

Response: {'type': 'FORECAST', 'category': 'jeans', 'week type': 'next week'}

Example 2:
Current date is March 06, 2024.
User: How many crop tops are going to be sold next to next week?

Response: {'type': 'FORECAST', 'item': 'crop top', 'week type': 'next week'}

Example 3:
Current date is March 06, 2024.
User: How many wrap dresses are going to be sold next month?

Response: {'type': 'FORECAST', 'item': 'wrap dress', 'week type': 'NA'}


For any other types of request return the type as UNRELATED in a json format.

Example:
Current date is March 06, 2024.
User: When is Joe Biden's speech happening next?

Response: {'type': 'UNRELATED'}

You must map the user request to one of the four request types and always return the response in JSON only.

Now respond to the query below. 

""" 
impersonated_role_query1 = impersonated_role_query1 + formatted_date + "\nUser:"

print(impersonated_role_query1)

impersonated_role_query2 = """
    From now on, you are going to act as BOT. Your role is inventory manager.
    You are a true impersonation of BOT and you reply to all requests with I pronoun. A human is mainly interested in requests related to item in inventory. 
    
    For any user request, once the corresponding module is invoked, the module will return an observation. You need to understand the question and observation and prepare the final response accordingly. Here are some examples - 
    
    Example 1- 
    
    User: How many dresses were sold last year?
    
    Observation: 145
    
    Response: 145 dresses were sold last year. 
    
    Example 2- 
    
    User: How many kurtas were sold last month?
    
    Observation: 0
    
    Response: There were no kurtas sold last month.
    
    Example 3- 
    
    User: How many blouses are availble?
    
    Observation: 30
    
    Response: There are 30 blouses available in inventory right now.
    
    Example 4- 
    
    User: How many crop tops are going to be sold next to next week?
    
    Observation: 5
    
    Response: According to my calculations, you can expect 5 crop tops to be sold next week. Please be prepared accordingly.
    
    Now respond to the user request below:
    
"""

# Initialize variables for chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
i = 1

# Find an available chat history file
while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

history_file = os.path.join(cwd, f'chat_history{i}.txt')

# Create a new chat history file
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize chat history
chat_history = ''

# Create a Flask web application
app = Flask(__name__)



# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, impersonated_role, explicit_input, chat_history):
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        temperature=0.5,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{impersonated_role}. Conversation history: ''"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ]
    )

    for item in output['choices']:
        chatgpt_output = item['message']['content']
        
    print(chatgpt_output)
    
    format_error = False
    
    try:
        formatted_response = eval(chatgpt_output.replace("[","{").replace("]","}").replace("Response:","").strip())
        if(formatted_response['type']=='INVENTORY'):
            print("Inventory")
            if('item' in formatted_response):
                return_val = get_inventory(formatted_response['item'].lower(), 'item')
            elif('category' in formatted_response):
                return_val = get_inventory(formatted_response['category'].lower(), 'category')

            if(return_val == 'Could not connect'):
                chatgpt_output = "There are some errors"
            else:

                if(return_val is None):
                    return_val = 0
                observation_string = "Observation: "+str(return_val)
                output = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.5,
                presence_penalty=0,
                frequency_penalty=0,
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": f"{impersonated_role_query2}. Conversation history: ''"},
                    {"role": "user", "content": f"{user_input}. {observation_string}"},
                ]
                )

                for item in output['choices']:
                    chatgpt_output = item['message']['content'] 
        elif(formatted_response['type']=='SALES'):
            print("Sales")
            print(formatted_response)

            if('item' in formatted_response):
                if(formatted_response['week']=='NA'):
                    return_val = get_sales_data(formatted_response['item'].lower(),formatted_response['month'], formatted_response['year'], 'item')
                else:
                    return_val = get_week_data(formatted_response['item'],'item',formatted_response['week'])
            elif('category' in formatted_response):
                if(formatted_response['week']=='NA'):
                    return_val = get_sales_data(formatted_response['category'].lower(),formatted_response['month'], formatted_response['year'], 'category')
                else:
                    return_val = get_week_data(formatted_response['category'],'category',formatted_response['week'])

            if(return_val == 'Could not connect'):
                chatgpt_output = "There are some errors"
            else:
                if(return_val is None):
                    return_val = 0
                observation_string = "Observation: "+str(return_val)
                output = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=1,
                presence_penalty=0,
                frequency_penalty=0,
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": f"{impersonated_role_query2}. Conversation history: ''"},
                    {"role": "user", "content": f"{user_input}. {observation_string}"},
                ]
                )
                for item in output['choices']:
                    chatgpt_output = item['message']['content']

        elif(formatted_response['type']=='FORECAST'):
            print("Forecast")
            if(formatted_response['week type']=='NA'):
                chatgpt_output = "Sorry this operation is not yet supported."
            else:
                print("Came here else")
                if('item' in formatted_response):
                    return_val = predict(formatted_response['item'].lower(),'item',formatted_response['week type'])
                elif('category' in formatted_response):
                    return_val = predict(formatted_response['category'].lower(),'category',formatted_response['week type'])


                if(return_val == 'Could not connect'):
                    chatgpt_output = "There are some errors"
                else:
                    if(return_val is None):
                        return_val = 0
                    observation_string = "Observation: "+str(return_val)
                    output = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0301",
                    temperature=1,
                    presence_penalty=0,
                    frequency_penalty=0,
                    max_tokens=2000,
                    messages=[
                        {"role": "system", "content": f"{impersonated_role_query2}. Conversation history: ''"},
                        {"role": "user", "content": f"{user_input}. {observation_string}"},
                    ]
                    )

                    for item in output['choices']:
                        chatgpt_output = item['message']['content']

        elif(formatted_response['type']=='UNRELATED'):
            print("Unrelated")
            output = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=1,
                presence_penalty=0,
                frequency_penalty=0,
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": f"Conversation history: ''"},
                    {"role": "user", "content": f"{user_input}. {explicit_input}"},
                ]
            )
            for item in output['choices']:
                chatgpt_output = item['message']['content']
        else:
            chatgpt_output = "Sorry this operation is not yet supported."
    except:
        format_error = True
    
    
    #except Exception as e:
    #    chatgpt_output = chatgpt_output

    return chatgpt_output

# Function to handle user chat input
def chat(user_input):
    global chat_history, name, chatgpt_output
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, impersonated_role_query1, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText):
    return chat(userText)

# Define app routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get")
# Function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

@app.route('/refresh')
def refresh():
    time.sleep(600) # Wait for 10 minutes
    return redirect('/refresh')

# Run the Flask app
if __name__ == "__main__":
    app.run()
