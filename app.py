from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load your dataset
df = pd.read_csv('food_data_final.csv')

vitamin_columns = ['Vitamin C', 'Vitamin A', 'Vitamin E', 'Vitamin K']
mineral_columns = ['Potassium', 'Magnesium', 'Phosphorus', 'Calcium', 'Iron', 'Zinc']

# Create new columns for total vitamins and total minerals
df['Total_Vitamins'] = df[vitamin_columns].sum(axis=1)
df['Total_Minerals'] = df[mineral_columns].sum(axis=1)
df_new=df[['food items','Category']].copy()
gluten_free_categories = ['Gluten-Free','NIL']
df_new['Gluten_Free'] = df['gluten'].apply(lambda x: 1 if any(category in x for category in gluten_free_categories) else 0)
vegetarian_categories = ['Vegetables', 'Fruits', 'Grains','Nuts & Seeds','Dairy','Protien']
df_new['Vegetarian'] = df['Category'].apply(lambda x: 1 if any(category in x for category in vegetarian_categories) else 0)
vegan_categories = ['Vegetables', 'Fruits', 'Grains','Nuts & Seeds','Protien']
df_new['Vegan'] = df['Category'].apply(lambda x: 1 if any(category in x for category in vegan_categories) else 0)
nut_free_category=['Vegetables', 'Fruits', 'Grains','Meat','Non-veg Protien','Protien','Dairy']
df_new['Dairy_Free'] = df['Category'].apply(lambda x: 1 if 'Dairy' not in x else 0)
df_new['Dairy'] = df['Category'].apply(lambda x: 1 if 'Dairy' in x else 0)
df_new['Nut Free'] = df['Category'].apply(lambda x: 1 if 'Nuts & Seeds' not in x else 0)
Non_veg=['Meat','Non-veg Protien']
df_new['Non-Vegetarian'] = df['Category'].apply(lambda x: 1 if any(category in x for category in Non_veg) else 0)
sodium_std = df['Sodium'].std()

# Set a threshold as mean minus one standard deviation
low_sodium_threshold = df['Sodium'].mean() - sodium_std
df_new['Low_Sodium'] = df['Sodium'].apply(lambda x: 1 if x < low_sodium_threshold else 0)
df_new['Low_Carb'] = (df['Carbs'] <= df['Carbs'].mean()).astype(int)
df_new['Vitamin_Rich'] = (df['Total_Vitamins'] >= df['Total_Vitamins'].mean()).astype(int)
df_new['Mineral_Rich'] = (df['Total_Minerals'] >= df['Total_Minerals'].mean()).astype(int)
df_new['Low_Cholesterol'] = (df['Cholesterol'] <= df['Cholesterol'].mean()).astype(int)
df_new['High_Fiber'] = (df['Fiber'] >= df["Fiber"].mean()).astype(int)
df_new['Low_Sugar'] = (df['Sugar'] <= df['Sugar'].mean()).astype(int)
df_new['High_Protein'] = (df['Protein']>=df['Protein'].mean()).astype(int)
preference_mapping = {
    'Low_Sodium': 'Sodium',
    'Low_Carb': 'Carbs',
    'High_Protein': 'Protein',
    'High_Fiber': 'Fiber',
    'Low_Sugar': 'Sugar',
    'Low_Cholesterol': 'Cholesterol',
    'Vitamin_Rich': 'Total_Vitamins',
    'Mineral_Rich': 'Total_Minerals'
}
sorting_rules = {
    'rich': 'descend',  # Sort in descending order for "rich" nutrients
    'high': 'descend',  # Sort in descending order for "high" nutrients
    'low': 'ascend'     # Sort in ascending order for "low" nutrients
}

@app.route('/')
def index():
    return render_template('buttons_page.html')

@app.route('/analyze')
def manual_preferences():
    return render_template('preferences_form.html')
@app.route('/analyze', methods=['POST'])
def submit_preferences():
    user_input_dietary = {
        'Gluten_Free': int(request.form.get('gluten_free', 0)),
        'Vegetarian': int(request.form.get('vegetarian', 0)),
        'Vegan': int(request.form.get('vegan', 0)),
        'Dairy_Free': int(request.form.get('dairy_free', 0)),
        'Dairy':int(request.form.get('dairy', 0)),
        'Nut Free': int(request.form.get('nut_free', 0)),
        'Non-Vegetarian': int(request.form.get('non_vegetarian', 0))
    }
    
    user_series_dietary = pd.Series(user_input_dietary)
    
    # Filter DataFrame based on dietary preferences
    filtered_df = df_new[(df_new[list(user_series_dietary[user_series_dietary == 1].index)] == 1).all(axis=1)]
    
    # Extract nutrient preferences from the form
    user_input_nutrient = {
        'Low_Sodium': int(request.form.get('low_sodium', 0)),
        'Low_Carb': int(request.form.get('low_carb', 0)),
        'High_Protein': int(request.form.get('high_protein', 0)),
        'High_Fiber': int(request.form.get('high_fiber', 0)),
        'Low_Sugar': int(request.form.get('low_sugar', 0)),
        'Low_Cholesterol': int(request.form.get('low_cholesterol', 0)),
        'Vitamin_Rich': int(request.form.get('vitamin_rich', 0)),
        'Mineral_Rich': int(request.form.get('mineral_rich', 0))
    }
    
    user_series_nutrient = pd.Series(user_input_nutrient)
    
    # Filter DataFrame based on nutrient preferences
    filtered_df = filtered_df[(filtered_df[list(user_series_nutrient[user_series_nutrient == 1].index)] == 1).all(axis=1)]
    
    # Extract indexes of filtered rows
    filtered_indexes = filtered_df.index.tolist()

    # Display the corresponding rows from the original DataFrame
    original_filtered_df = df.loc[filtered_indexes]
    
    # Select columns to display based on selected nutrient preferences
    selected_columns = [col for col, value in user_input_nutrient.items() if value == 1]
    corresponding_columns = [preference_mapping[col] for col in selected_columns]

    # Display selected columns along with 'food items' and 'Calories'
    result_df = original_filtered_df[['food items','Calories'] + corresponding_columns]
    sorted_datasets = []
    for nutrient, value in user_input_nutrient.items():
        if value == 1:
            # Extract the corresponding column from preference_mapping
            column = preference_mapping[nutrient]
            
            # Extract the keyword from the nutrient name
            keyword = ''
            for kw, order in sorting_rules.items():
                if kw in nutrient.lower():
                    keyword = kw
                    sorting_order = order
                    break
            
            # Sort the DataFrame accordingly
            sorted_df = result_df.sort_values(by=column, ascending=(sorting_order == 'ascend'))
            
            sorted_datasets.append((column, sorting_order, sorted_df[['food items','Calories',column]][:5]))
            for column, order, dataset in sorted_datasets:
                print(f"Sorted Dataset by '{column}' in {order}ing order:")
                print(dataset)
                print()

    
    return render_template('filtered_results.html', sorted_datasets=sorted_datasets)




if __name__ == '__main__':
    app.run(debug=True)
