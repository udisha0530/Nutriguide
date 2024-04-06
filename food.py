import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans


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
low_sodium_threshold = df['Sodium'].mean() 
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

    page = st.sidebar.radio("Select Method", ["Enter Preferences Manually", "Enter your Information"])

    if page == "Enter Preferences Manually":
        st.header("Enter Nutritional Preferences Manually")
        enter_preferences_manually()

    elif page == "Enter your Information":
        st.header("Analyze Nutritional Preferences Based on User Information")
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
        result_df = original_filtered_df[['food items','Calories','Category'] + corresponding_columns]
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
            
            sorted_datasets.append((column, sorting_order, sorted_df[['food items','Calories','Category',column]][:5]))
        
        # Append top matching results to sorted_datasets
    
    # Display results
        st.subheader("Top Matching Results")
        for dataset in sorted_datasets:
              st.write(dataset[2])
              st.write("---") 

    # Filter DataFrame based on nutrient preferences
    
    
    # Display the corresponding rows from the original DataFrame
    
    

def analyze_based_on_age():
    # Collect user information
    st.subheader("User Information")
    # Collect user information
    
    age = st.number_input("Enter your age", min_value=1, max_value=120, value=30, step=1)
    weight = st.number_input("Enter your weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
    height = st.number_input("Enter your height (cm)", min_value=50.0, max_value=300.0, value=170.0, step=1.0)

    # Define user profile based on input
    user_profile = define_user_profile(age, weight, height)
    df_age = pd.read_csv('food_data_final.csv')

# Perform k-means clustering on the nutritional values
    X = df_age[['Calories', 'Protein', 'Carbs', 'Total Fat']]
    kmeans = KMeans(n_clusters=3)  # Adjust the number of clusters as needed
    kmeans.fit(X)
    df_age['cluster'] = kmeans.labels_

    # Perform recommendation based on user profile
    recommended_food = recommend_food(df_age, user_profile,kmeans)

    # Display recommendations
    if st.button("Analyze"):
       st.subheader("Recommended Food Items")
       st.write(recommended_food)
   
    # Logic to analyze nutritional preferences based on age
    # This can include specific recommendations based on age groups
def define_user_profile(age, weight, height):
    # Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation
    # BMR (kcal/day) = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (years) + S
    # S = +5 for males, -161 for females
    gender = st.selectbox("Select your gender", ["Male", "Female"])
    if gender == "Male":
        s = 5
    else:
        s = -161
    bmr = 10 * weight + 6.25 * height - 5 * age + s

    # Determine Total Daily Energy Expenditure (TDEE) based on activity level
    activity_level = st.selectbox("Select your activity level", ["Sedentary", "Lightly active", "Moderately active", "Very active", "Extremely active"])
    activity_factors = {"Sedentary": 1.2, "Lightly active": 1.375, "Moderately active": 1.55, "Very active": 1.725, "Extremely active": 1.9}
    tdee = bmr * activity_factors[activity_level]

    # Define macronutrient distribution based on user's goals
    goal = st.selectbox("Select your goal", ["Weight loss", "Maintenance", "Muscle gain"])
    if goal == "Weight loss":
        calories_percentage = 40
        protein_percentage = 30
        carbs_percentage = 30
        fat_percentage = 20
    elif goal == "Maintenance":
        calories_percentage = 50
        protein_percentage = 25
        carbs_percentage = 25
        fat_percentage = 25
    elif goal == "Muscle gain":
        calories_percentage = 45
        protein_percentage = 35
        carbs_percentage = 35
        fat_percentage = 20

    # Define user profile as a dictionary
    user_profile = {
        'Calories': tdee * (calories_percentage / 100),
        'Protein': tdee * (protein_percentage / 100) / 4,  # 1 gram of protein = 4 calories
        'Carbs': tdee * (carbs_percentage / 100) / 4,  # 1 gram of carbs = 4 calories
        'Total Fat': tdee * (fat_percentage / 100) / 9  # 1 gram of fat = 9 calories
    }

    return user_profile
def recommend_food(df_age, user_profile,kmeans):
    # Find cluster that matches user's nutritional needs
    user_profile_df = pd.DataFrame([user_profile])
    
    # Select relevant features for clustering (assuming they match the features used for training)
    features = ['Calories', 'Protein', 'Carbs', 'Total Fat']
    
    # Extract user profile features
    user_features = user_profile_df[features]
    
    # Print user_features for debugging
    # Predict the cluster for the user profile
    user_cluster = kmeans.predict(user_features)[0]
    
    # Filter food items belonging to the predicted cluster
    recommended_food = df_age[df_age['cluster'] == user_cluster]['food items']
    
    return recommended_food
def filter(user_series_dietary,user_series_nutrient,df_new):
     filtered_df = df_new[(df_new[list(user_series_dietary[user_series_dietary == 1].index)] == 1).all(axis=1)]
     filtered_df = filtered_df[(filtered_df[list(user_series_nutrient[user_series_nutrient == 1].index)] == 1).all(axis=1)]
     return filtered_df
         

if __name__ == "__main__":
    main()
