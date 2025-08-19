import mysql.connector
import datetime

def create_connection():
    cnx = mysql.connector.connect(user='root', password='12345678',
                              host='127.0.0.1',
                              database='sales data')
    return cnx

def close_connection(cnx):
    cnx.close()
    
def execute_query(query, cnx):
    print(query)
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:

            result = cursor.execute(query)

            rows = cursor.fetchall()

            for row in rows:
                return str(row[0])

    else:
        return "Could not connect"
    
def get_inventory(text, type_of_filter):
    if('type_of_filter' == 'category'):  
        query = "SELECT sum(Available_Qty) from item where category like '%{}%'".format(text)
    else:
        item_phrase = '%{}%'.format("%").join(text.split())
        query = "SELECT sum(Available_Qty) from item where product_name like '%{}%' or category like '%{}%'".format(item_phrase, item_phrase)
        
    cnx = create_connection()
    value = execute_query(query,cnx)
    close_connection(cnx)
    return value

def get_sales_data(text, month, year, type_of_filter):
    if('type_of_filter' == 'category'):
        if(month != 'NA'):
            query = "SELECT sum(qty) FROM combined WHERE EXTRACT(YEAR FROM date_ending) = '{}' AND EXTRACT(MONTH FROM date_ending) = '{}' AND category like '%{}%'".format(year, month, category)
        else:
            query = "SELECT sum(qty) FROM combined WHERE EXTRACT(YEAR FROM date_ending) = '{}' AND category like '%{}%'".format(year, category)
    else:
        item_phrase = '%{}%'.format("%").join(text.split())
        if(month != 'NA'):
            query = "SELECT sum(qty) FROM combined WHERE EXTRACT(YEAR FROM date_ending) = '{}' AND EXTRACT(MONTH FROM date_ending) = '{}' AND (product_name like '%{}%' or category like '%{}%')".format(year, month, item_phrase, item_phrase)
        else:
            query = "SELECT sum(qty) FROM combined WHERE EXTRACT(YEAR FROM date_ending) = '{}' AND (product_name like '%{}%' or category like '%{}%') ".format(year, item_phrase, item_phrase)
    
    print(query)
    cnx = create_connection()
    value = execute_query(query,cnx)
    close_connection(cnx)
    return value

def get_parent_sku(item):
    item_phrase = '%{}%'.format("%").join(item.split())
    query = "SELECT sku_parent FROM item WHERE product_name like '%{}%'".format(item_phrase)                                  
    cnx = create_connection()
    value = execute_query(query,cnx)
    close_connection(cnx)
    return value

def get_category(category):
    query = "SELECT distinct category FROM item WHERE category like '%{}%' limit 1".format(category)                                  
    cnx = create_connection()
    value = execute_query(query,cnx)
    close_connection(cnx)
    return value
                                
def get_sku_count(item):
    item_phrase = '%{}%'.format("%").join(item.split())
    query = "SELECT count(1) FROM item WHERE product_name like '%{}%'".format(item_phrase)
    
    cnx = create_connection()
    value = execute_query(query,cnx)
    close_connection(cnx)
    return value
                                     
def get_week_data(text, type_of_filter, week_type='next week'):
    date_req = datetime.date.today()
    if(week_type=='last'):
        date_req = date_req - datetime.timedelta(days=7)
                                     
    days_passed = date_req.weekday() + 2  # Adding 1 to shift Sunday from 6 to 0
    saturday = date_req + datetime.timedelta(days=(5 - date_req.weekday()))
    saturday_formatted = saturday.strftime("%Y/%m/%d")
    
    if('type_of_filter' == 'category'):                         
        query = "SELECT sum(qty) FROM combined WHERE date_ending = '{}' AND category like '%{}%'".format(saturday_formatted, category)
    else:
        item_phrase = '%{}%'.format("%").join(text.split())
        query = "SELECT sum(qty) FROM combined WHERE date_ending = '{}' AND category like '%{}%'".format(saturday_formatted, item_phrase)
    
    cnx = create_connection()
    value = execute_query(query,cnx)
    close_connection(cnx)
    return value