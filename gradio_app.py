import gradio as gr
import openai
import json
import pandas as pd
import math
from datetime import datetime
import os

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get current date
current_date = datetime.now()
formatted_date = current_date.strftime("Current date is %B %d, %Y.")

# Mock data for demo purposes
INVENTORY_DATA = {
    'western dress': 45, 'top': 120, 'ethnic dress': 30, 'kurta': 85, 'jeans': 200, 'dress': 75,
    'denim shorts': 25, 'crop top': 40, 'wide-leg jeans': 15, 'straight-leg jeans': 35,
    'khadi kurta': 20, 'denim skirt': 18, 'nehru jacket kurta': 12, 'acid wash jeans': 8,
    'raw denim jeans': 22, 'flare jeans': 30, 'slim fit jeans': 45, 'cargo jeans': 28,
    'high-waisted jeans': 55, 'pathani kurta': 15, 'shift dress': 25, 'angrakha kurta': 18,
    'relaxed fit jeans': 32, 'skinny jeans': 65, 'embellished jeans': 12, 'sindhi kurta': 8,
    'assamese kurta': 10, 'mom jeans': 38, 'crop jeans': 20, 'midi dress': 35,
    'pakistani kurta': 14, 'bodycon dress': 28, 'odia kurta': 9, 'south indian kurta': 16,
    'lucknowi kurta': 22, 'boyfriend jeans': 42, 'jaipuri kurta': 18, 'bootcut jeans': 25,
    'himachali kurta': 7, 'peplum top': 30, 'wrap dress': 20, 'bandhgala kurta': 15,
    'black jeans': 50, 'afghani kurta': 11, 'low-rise jeans': 18, 'ethnic dress': 30,
    'sherwani kurta': 8, 'chikankari kurta': 25, 't-shirt': 80, 'fit and flare dress': 22,
    'kashmiri kurta': 12, 'tribal kurta': 9, 'gujarati kurta': 16, 'achkans kurta': 6,
    'white jeans': 35, 'dhoti kurta': 14, 'blouse': 45, 'off-shoulder top': 28,
    'jogger jeans': 20, 'ripped jeans': 40, 'bihari kurta': 10, 'tank top': 55,
    'rajasthani kurta': 18, 'punjabi kurta': 24, 'a-line dress': 32, 'bengali kurta': 15,
    'balochi kurta': 8, 'classic blue jeans': 60, 'mini dress': 25, 'distressed jeans': 30,
    'maxi dress': 28
}

SALES_DATA = {
    'western dress': {'last_month': 120, 'last_week': 28, 'this_week': 15},
    'top': {'last_month': 200, 'last_week': 45, 'this_week': 22},
    'ethnic dress': {'last_month': 85, 'last_week': 18, 'this_week': 12},
    'kurta': {'last_month': 150, 'last_week': 35, 'this_week': 18},
    'jeans': {'last_month': 180, 'last_week': 42, 'this_week': 25},
    'dress': {'last_month': 95, 'last_week': 22, 'this_week': 14},
    'crop top': {'last_month': 65, 'last_week': 15, 'this_week': 8},
    'skinny jeans': {'last_month': 75, 'last_week': 18, 'this_week': 10},
    'chikankari kurta': {'last_month': 45, 'last_week': 12, 'this_week': 6},
    'maxi dress': {'last_month': 55, 'last_week': 14, 'this_week': 7}
}

# Categories and items lists
CATEGORIES = ['western dress', 'top', 'ethnic dress', 'kurta', 'jeans', 'dress']
ITEMS = list(INVENTORY_DATA.keys())

def get_mock_inventory(item_name, search_type):
    """Mock function to replace database inventory lookup"""
    if search_type == 'item':
        return INVENTORY_DATA.get(item_name.lower(), 0)
    elif search_type == 'category':
        # Sum all items in category
        category_items = [k for k in INVENTORY_DATA.keys() if item_name.lower() in k.lower()]
        return sum(INVENTORY_DATA.get(item, 0) for item in category_items)
    return 0

def get_mock_sales_data(item_name, time_period):
    """Mock function to replace database sales lookup"""
    item_data = SALES_DATA.get(item_name.lower(), {'last_month': 0, 'last_week': 0, 'this_week': 0})
    return item_data.get(time_period, 0)

def mock_predict(item_name, search_type, week_type):
    """Mock prediction function"""
    base_sales = get_mock_sales_data(item_name, 'this_week')
    # Simple prediction: current week sales + 10-30% growth
    if base_sales == 0:
        return 5  # Default prediction
    growth_factor = 1.2 if week_type == 'next week' else 1.15
    return math.ceil(base_sales * growth_factor)
# Defi
ne the role and instructions for the chatbot
impersonated_role_query1 = f"""
From now on, you are going to act as BOT. Your role is inventory manager.
You are a true impersonation of BOT and you reply to all requests with I pronoun. A human is mainly interested in requests related to item in inventory. A request can belong to four different types as below. 

SALES: Related to sales history of an item
FORECAST: Related to future forecast of an item
INVENTORY: Inventory status of an item
UNRELATED: User request is not related to sales, forecast or inventory

A user can either request for an item or for a category. 

Below are the available list of categories - 
{CATEGORIES}

Below are the list of available items belonging to one of the categories above- 
{ITEMS[:20]}  # Showing first 20 items for brevity

Given a user request you need understand the request type and also map it to either one item or one category. If the user is asking about any of the categories in the list, strictly only map it to category and not item. Return the response in a json format. Always give response in json format no matter what the request may be.

For sales you need to understand the time period from the ask and return fields: 'type', 'category' or 'item', 'time_period'. 

Example 1:
{formatted_date}
User: How many dresses were sold last month?
Response: {{"type": "SALES", "category": "dress", "time_period": "last_month"}}

For Inventory requests return two fields: 'type', 'category' or 'item'. 

Example 1:
{formatted_date}
User: How many blouses are available?
Response: {{"type": "INVENTORY", "item": "blouse"}}

For forecast requests return three fields: 'type', 'category' or 'item', 'week_type'. 

Example 1:
{formatted_date}
User: How many jeans are going to be sold next week?
Response: {{"type": "FORECAST", "category": "jeans", "week_type": "next week"}}

For any other types of request return the type as UNRELATED.

You must map the user request to one of the four request types and always return the response in JSON only.

Now respond to the query below.
{formatted_date}
User:"""

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
User: How many blouses are available?
Observation: 30
Response: There are 30 blouses available in inventory right now.

Example 4- 
User: How many crop tops are going to be sold next week?
Observation: 5
Response: According to my calculations, you can expect 5 crop tops to be sold next week. Please be prepared accordingly.

Now respond to the user request below:
"""

def chatbot_response(message, history):
    """Main chatbot function for Gradio"""
    if not openai.api_key:
        return "⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    
    try:
        # First, classify the user query
        classification_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=500,
            messages=[
                {"role": "system", "content": impersonated_role_query1},
                {"role": "user", "content": message}
            ]
        )
        
        classification_text = classification_response['choices'][0]['message']['content']
        print(f"Classification: {classification_text}")
        
        # Parse the JSON response
        try:
            # Clean up the response and parse JSON
            clean_response = classification_text.replace("Response:", "").strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response.replace("```json", "").replace("```", "").strip()
            
            parsed_response = json.loads(clean_response)
        except json.JSONDecodeError:
            return "I'm having trouble understanding your request. Could you please rephrase it?"
        
        # Handle different request types
        if parsed_response['type'] == 'INVENTORY':
            if 'item' in parsed_response:
                result = get_mock_inventory(parsed_response['item'], 'item')
            elif 'category' in parsed_response:
                result = get_mock_inventory(parsed_response['category'], 'category')
            else:
                return "I couldn't identify the item or category you're asking about."
                
        elif parsed_response['type'] == 'SALES':
            item_key = parsed_response.get('item') or parsed_response.get('category')
            time_period = parsed_response.get('time_period', 'last_month')
            result = get_mock_sales_data(item_key, time_period)
                
        elif parsed_response['type'] == 'FORECAST':
            item_key = parsed_response.get('item') or parsed_response.get('category')
            search_type = 'item' if 'item' in parsed_response else 'category'
            week_type = parsed_response.get('week_type', 'next week')
            result = mock_predict(item_key, search_type, week_type)
                
        elif parsed_response['type'] == 'UNRELATED':
            return "I'm an inventory management assistant. I can help you with sales data, inventory levels, and forecasts. Please ask me about our products!"
        
        else:
            return "I'm not sure how to handle that request. Please ask about sales, inventory, or forecasts."
        
        # Generate final response using the observation
        observation_string = f"Observation: {result}"
        
        final_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500,
            messages=[
                {"role": "system", "content": impersonated_role_query2},
                {"role": "user", "content": f"{message}. {observation_string}"}
            ]
        )
        
        return final_response['choices'][0]['message']['content']
        
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again."

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Inventory Management Chatbot", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🏪 Inventory Management Chatbot
            
            I'm your AI inventory assistant! I can help you with:
            - 📊 **Sales Data**: "How many jeans were sold last month?"
            - 📦 **Inventory Levels**: "How many crop tops are available?"
            - 📈 **Sales Forecasts**: "How many dresses will be sold next week?"
            
            **Available Categories**: Western Dress, Top, Ethnic Dress, Kurta, Jeans, Dress
            """
        )
        
        chatbot = gr.ChatInterface(
            fn=chatbot_response,
            title="",
            description="Ask me about sales, inventory, or forecasts!",
            examples=[
                "How many jeans were sold last month?",
                "What's the current inventory for crop tops?",
                "Forecast sales for dresses next week",
                "How many kurtas are available?",
                "Sales data for western dress last week"
            ],
            retry_btn=None,
            undo_btn=None,
            clear_btn="Clear Chat"
        )
        
        gr.Markdown(
            """
            ---
            **Note**: This is a demo version using mock data. In production, this would connect to a real inventory database.
            
            **Tech Stack**: Python, OpenAI GPT-3.5, Gradio, Machine Learning
            """
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
