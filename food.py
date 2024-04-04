import streamlit as st
import pandas as pd

# Read the CSV file
df = pd.read_csv('food_data_final.csv')
vitamin_columns = ['Vitamin C', 'Vitamin A', 'Vitamin E', 'Vitamin K']
mineral_columns = ['Potassium', 'Magnesium', 'Phosphorus', 'Calcium', 'Iron', 'Zinc']

# Create new columns for total vitamins and total minerals
df['Total_Vitamins'] = df[vitamin_columns].sum(axis=1)
df['Total_Minerals'] = df[mineral_columns].sum(axis=1)
df_new=df[['food items','Category']].copy()
gluten_free_categories = ['Gluten-Free','NIL']
# Define gluten-free categories

# Apply the function only to items in the "Grains" category
df_new['Gluten_Free'] = df.apply(lambda row: 1 if 'Grains' in row['Category'] and any(category in row['gluten'] for category in gluten_free_categories) else 0, axis=1)

vegetarian_categories = ['Vegetables', 'Fruits', 'Grains','Nuts & Seeds','Dairy','Protien']
df_new['Vegetarian'] = df['Category'].apply(lambda x: 1 if any(category in x for category in vegetarian_categories) else 0)
vegan_categories = ['Vegetables', 'Fruits', 'Grains','Nuts & Seeds','Protien']
df_new['Vegan'] = df['Category'].apply(lambda x: 1 if any(category in x for category in vegan_categories) else 0)
nut_free_category=['Vegetables', 'Fruits', 'Grains','Meat','Non-veg Protien','Protien','Dairy']
df_new['Dairy_Free'] = df['Category'].apply(lambda x: 1 if 'Dairy' not in x else 0)
df_new['Dairy'] = df['Category'].apply(lambda x: 1 if 'Dairy' in x else 0)
df_new['Nut_Free'] = df['Category'].apply(lambda x: 1 if 'Nuts & Seeds' not in x else 0)
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

# Define nutrient preferences mapping and sorting rules
preference_mapping = {
    'Low_Sodium': 'Sodium',
    'Low_Carb': 'Carbs',
    'High_Protein': 'Protein',
    'High_Fiber': 'Fiber',
    'Low_Sugar': 'Sugar',
    'Low_Cholesterol': 'Cholesterol',
    'Vitamin_Rich': 'Total_Vitamins',
    'Mineral_Rich':'Total_Minerals' 
}

sorting_rules = {
    'rich': 'descend',  # Sort in descending order for "rich" nutrients
    'high': 'descend',  # Sort in descending order for "high" nutrients
    'low': 'ascend'     # Sort in ascending order for "low" nutrients
}

# Define Streamlit app
def main():
    st.title('Nutritional Preferences Analyzer')

    page = st.sidebar.radio("Select Method", ["Enter Preferences Manually", "Enter your Age"])

    if page == "Enter Preferences Manually":
        st.header("Enter Nutritional Preferences Manually")
        enter_preferences_manually()

    elif page == "Based on Age":
        st.header("Analyze Nutritional Preferences Based on Age")
        analyze_based_on_age()

def enter_preferences_manually():
    # Collect user dietary preferences
    st.subheader("Dietary Preferences")
    user_input_dietary = {}
    for preference in ['Gluten_Free', 'Vegetarian', 'Vegan', 'Dairy_Free', 'Dairy', 'Nut_Free', 'Non-Vegetarian']:
        user_input_dietary[preference] = st.checkbox(preference)
    
    user_series_dietary = pd.Series(user_input_dietary)
    # Filter DataFrame based on dietary preferences
    

    # Collect user nutrient preferences
    st.subheader("Nutrient Preferences")
    user_input_nutrient = {}
    for nutrient  in  [ 'Low_Sodium',
    'Low_Carb',
    'High_Protein',
    'High_Fiber',
    'Low_Sugar',
    'Low_Cholesterol',
    'Vitamin_Rich',
    'Mineral_Rich']:
           user_input_nutrient[nutrient] = st.checkbox(nutrient)

    user_series_nutrient = pd.Series(user_input_nutrient) 
    if st.button("Analyze"):
    # Filter DataFrame based on user preferences
        filtered_df = filter(user_series_dietary, user_series_nutrient,df_new)
        filtered_indexes = filtered_df.index.tolist()
        original_filtered_df = df.loc[filtered_indexes]
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
        
        # Append top matching results to sorted_datasets
    
    # Display results
        st.subheader("Top Matching Results")
        for dataset in sorted_datasets:
              st.write(f"Sorted by: {dataset[0]}, Order: {dataset[1]}")
              st.write(dataset[2])
              st.write("---") 

    # Filter DataFrame based on nutrient preferences
    
    
    # Display the corresponding rows from the original DataFrame
    
    

def analyze_based_on_age():
    s=st.slider("Select your age:", min_value=1, max_value=100, value=30, step=1)
    age=s
   
    # Logic to analyze nutritional preferences based on age
    # This can include specific recommendations based on age groups
def filter(user_series_dietary,user_series_nutrient,df_new):
     filtered_df = df_new[(df_new[list(user_series_dietary[user_series_dietary == 1].index)] == 1).all(axis=1)]
     filtered_df = filtered_df[(filtered_df[list(user_series_nutrient[user_series_nutrient == 1].index)] == 1).all(axis=1)]
     return filtered_df
         

if __name__ == "__main__":
    main()
