from sklearn.linear_model import LinearRegression
import joblib
from db_connection import get_category, get_week_data, get_parent_sku, get_sku_count 
import pandas as pd
import math

loaded_model_item = joblib.load('linear_regression_model.pkl')
loaded_model_category = joblib.load('linear_regression_model_category.pkl')

# Assuming 'new_data' is a DataFrame containing the same columns as the training data
# Make predictions with the loaded model

def predict(text, type_of_search, type_of_week):
    if(type_of_search == 'category'):
        category = get_category(text)
        weekly_count = get_week_data(category, type_of_search, type_of_week)
        
        if(weekly_count is None):
            weekly_count = 0
        else:
            weekly_count = int(weekly_count)
            
        new_record = pd.DataFrame([{'Category':category,'wk_m_1':weekly_count}])

        predicted_value = loaded_model_category.predict(new_record)[0]
              
        return math.ceil(predicted_value)
    
    else:
        sku_parent = get_parent_sku(text)
        sku_count = get_sku_count(text)
        
        weekly_count = get_week_data(text, type_of_search, type_of_week)
        
        new_record = pd.DataFrame([{'SKU_Parent':sku_parent,'wk_m_1':weekly_count*int(sku_count)}])
        
        predicted_value = loaded_model_item.predict(new_record)[0]
        
        return math.ceil(predicted_value)