import json
from turtle import right
import streamlit as st
from tasty_api import searchapi # <-- Add this import to bring in the searchapi function
import pandas as pd
import plotly.express as px

# Set view state
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'create_user_profile'

# Step 1: User Profile Creation and BMI/BMR calculation 
def create_user_profile(): 
    st.header("User Profile")
    first_name = st.text_input("Enter your first name")
    last_name = st.text_input("Enter your last name") 
    gender = st.selectbox("Select your gender", ["Male", "Female"])
    age = st.number_input ("Enter you age", min_value = 1, step=1)
    weight = st.number_input ("Enter your weight in kg", min_value = 0.1, step= 0.1) # Set min_value > 0.1 
    height = st.number_input ("Enter your height in cm", min_value = 0.1, step= 0.1) # Set min_value > 0.1

    if st.button("Save Profile"): # Calculate BMI and BMR in the background to display it after the User Profile was saved instead of doing it partly 
        
        bmi = weight / ((height / 100) ** 2)

        def calculate_bmr(gender, weight, height, age):
            if gender.lower() == "male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:  # Assumes gender is "female"
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            return bmr
        
        bmr = calculate_bmr(gender, weight, height, age)

        user_data = { 
            "name" : f"{first_name} {last_name}",
            "age" : age, 
            "gender" : gender, 
            "BMI" : bmi, 
            "BMR" : bmr
        }

        # Display user profile 
        st.write (f"Profile is saved!")
        st.write (f"Your BMI is **{bmi:.2f}** and your BMR is **{bmr:.2f}**")

        #Calculate normal BMI range for gender
        if gender == 'Male':
            df = pd.DataFrame({ 
                "BMI": [20, 4.9, 5, 5, 5, 10],
            })
        elif gender == 'Female':
            df = pd.DataFrame({ 
                "BMI": [19, 4.9, 6, 5, 5, 10],
            })
        else:
            raise ValueError

        df['single_bar'] = 'BMI'

        #Create a bar chart with the BMI range and user-specific BMI
        fig = px.bar(
            df,
            x='BMI',
            y='single_bar',
            color=["Underweight", "Normal weight", "Overweight", "Serverly Overweight (Obesity Grade I)", "Obesity Grade II", "Obesity Grade III"],
            color_discrete_map=
            {
                'Underweight': '#89CFF0',
                'Normal weight': '#3FAD51',
                'Overweight': '#F3E85A',
                'Serverly Overweight (Obesity Grade I)': '#FFC000',
                'Obesity Grade II': '#FF8400',
                'Obesity Grade III': '#AA0000'
            },
            orientation='h',
            height=300
        )

        #Adjustments to the layout of the chart
        fig.update_yaxes(visible=False, showticklabels=False)
        fig.add_vline(x=bmi)
        fig.add_annotation(x=bmi -2.75, y=.3, text="Your BMI", showarrow=False)
        fig.update_layout(hovermode=False)
        fig.update_traces(width=.25)
        fig.update_layout(xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
        )
        fig.update_layout({
            'plot_bgcolor': '#FFFFFF',
            'paper_bgcolor': '#FFFFFF',
        })
        fig.update_layout(legend_title_text='BMI Level')

        #Display the chart in streamlit
        st.plotly_chart(fig)

        # Save user profile in json file
        with open ("user_profile.json", "w") as f:
            json.dump (user_data, f)
        st.session_state['mode'] = 'set_fitness_goal'
        set_fitness_goal(weight=weight)


# Step 2: Fitness Goal and Calorie Adjustment based on PAL, Exercise and Calorie Goal  
def set_fitness_goal(weight: int):
    st.header("Set Your Fitness Goal")

    # Step 2.1: Select fitness goal out of 3 options and target 
    fitness_goal = st.selectbox ("Choose your fitness goal", ["Lose weight", "Maintain weight", "Gain weight"])
    
    if fitness_goal in ["Lose weight", "Gain weight "]:
        target_amount = st.number_input ("Enter your target weight change in kg", step=0.1) # Should only appear if lose or gain weight was chosen
        time_period = st.number_input ("Enter your target time period in weeks", step=1)
    else: # Handle the "Maintain weight" case
        st.write("You have selected to maintain your current weight, so no weight change target is needed.")
        target_amount = 0  # Set default value for target amount if maintaining weight
        time_period = 0    # Set default value for time period if maintaining weight

    # Step 2.2: Calculate the calorie change factor based on fitness goal 
    if fitness_goal == "Lose weight":
            calorie_adjustment = -500 if target_amount > 2 else -200 
    elif fitness_goal == "Gain weight": 
            calorie_adjustment = 500 if target_amount > 2 else 200
    else: 
            calorie_adjustment = 0 #No adjustment for weight maintain
    
     # Step 2.3: Select Physical Activity Level (PAL)
    st.header("Physical Activity Level (PAL)")
    activity_level = st.selectbox ("Select your activity level", [
        "Sedentary (e.g., elderly) – PAL: 1.2",
        "Mostly sedentary (e.g., office job) – PAL: 1.4",
        "Moderate movement (e.g., students) – PAL: 1.6",
        "Standing work (e.g., professors) – PAL: 1.8",
        "Physically demanding work (e.g., manual labor) – PAL: 2.2"
    ])
    
    # Step 2.5: Weekly Exercise Adjustment
    st.header("Weekly Exercise")
    hours_of_sport = st.number_input("Enter hours of exercise per week", min_value=0.0, step=0.5)
    
    if st.button("Save Fitness Goal"): 
        # Step 2.4: Assign PAL value based on selection
        pal_dict = {
            "Sedentary (e.g., elderly) – PAL: 1.2": 1.2,
            "Mostly sedentary (e.g., office job) – PAL: 1.4": 1.4,
            "Moderate movement (e.g., students) – PAL: 1.6": 1.6,
            "Standing work (e.g., professors) – PAL: 1.8": 1.8,
            "Physically demanding work (e.g., manual labor) – PAL: 2.2": 2.2
        }
        pal = pal_dict[activity_level]     

        exercise_adjustment = pal * 0.05 * hours_of_sport

        # Step 2.6: Total Daily Expenditure and Caloric Goal Calculation
        energy_expenditure = 2000 # Placeholder for a base energy expenditure, adjust as needed
        total_daily_expenditure = energy_expenditure + exercise_adjustment
        goal_calories = total_daily_expenditure + calorie_adjustment

        # Step 2.7: Display results
        st.write(f"With your activity level and exercise, your daily caloric expenditure is: {total_daily_expenditure:.2f} calories.")
        st.write(f"To reach your fitness goal, your daily calorie target should be: {goal_calories:.2f} calories.")

        #Calculate daily protein, fat and carbs intake in grams based on the goal calories
        protein = round(1.5 * weight)
        protein_kcals = protein * 5.1
        fat = round(0.7 * weight)
        fat_kcals = fat * 9
        carbs_kcals =  goal_calories - protein_kcals - fat_kcals
        carbs = round(carbs_kcals / 5.1)

        #Create a dataframe to be used in the pie chart
        df = pd.DataFrame({
            "Type": ["Protein", "Carbs", "Fat"],
            "Calories": [protein, carbs, fat]
        })

        #Create a pie chart that displays the daily intake of protein, fat and carbs
        fig = px.pie(
            df, 
            values='Calories', 
            names='Type',
            title=f'Grams of Protein, Fat and Carbs for a {goal_calories} Calorie Diet',
            category_orders={"Type": df["Type"].tolist()},
            width=650,
            height=400
        )

        #Adjustments to the layout of the chart
        fig.update_layout(hovermode=False)
        fig.update_traces(
            textinfo='value',
            texttemplate='%{value}g (%{percent})',  # Adds "g" to the data labels
            marker=dict(colors=['#A52019', '#3E5982', '#E1A100']),
            sort=False
        ) 

        #Display the chart in streamlit
        st.plotly_chart(fig)

        # Step 2.8: Save fitness goal and calorie adjustment in json file
        fitness_data = {
            "fitness_goal": fitness_goal, 
            "target_amount": target_amount, 
            "time_period": time_period, 
            "activity_level": activity_level, 
            "pal": pal, 
            "hours_of_sport": hours_of_sport, 
            "exercise_adjustment": exercise_adjustment,
            "total_daily_expenditure": total_daily_expenditure, 
            "goal_calories": goal_calories
        }

        # save in json
        with open("fitness_goal.json", "w") as f:
             json.dump(fitness_data, f)
        st.write("Your fitness goal details have been saved.")
        st.session_state['mode'] = 'define_calories'
        define_calories()
    
            
# Step 3: Set up digital fridge
digital_fridge = {
    "Meat & Fish": ["Beef", "Chicken", "Pork", "Lamb", "Trout", "Cod", "Salmon", "Tuna"],
    "Meat Alternatives & Tofu": ["Tofu", "Tempeh", "Seitan", "Jackfruit", "Soy Protein", "Chickpea Patties"],
    "Spices, Herbs & Sauces": {
        "Spices": ["Salt", "Pepper", "Paprika", "Cumin", "Curry Powder", "Chili Flakes"],
        "Herbs": ["Basil", "Parsley", "Thyme", "Rosemary", "Oregano", "Dill"],
        "Sauces": ["Soy Sauce", "Tomato Sauce", "Barbecue Sauce", "Mustard", "Mayonnaise"]
    },
    "Convenience & Canned Foods": ["Canned Beans", "Canned Tomatoes", "Canned Corn", "Canned Tuna", "Soup", "Baked Beans"],
    "Frozen Foods": ["Frozen Peas", "Frozen Spinach", "Mixed Veggies", "Frozen Berries", "Frozen Mango", "Frozen Pizza", "French Fries"],
    "Milk & Milk Alternatives": ["Cow’s Milk", "Almond Milk", "Oat Milk", "Coconut Milk", "Soy Milk", "Goat Milk"],
    "Dairy Products, Cheese & Eggs": {
        "Dairy": ["Milk", "Yogurt", "Pudding", "Sour Cream"],
        "Cheese": ["Gruyère", "Mozzarella", "Camembert", "Cheddar", "Feta"],
        "Eggs": ["Chicken Eggs", "Quail Eggs"]
    },
    "Grain Products & Potato Products": ["Rice", "Corn", "Potatoes", "Oats", "Pasta", "Bread", "Quinoa", "Couscous"],
    "Legumes": ["Dried Beans", "Lentils", "Chickpeas", "Split Peas", "Black Beans"],
    "Fats & Oils": ["Olive Oil", "Butter", "Coconut Oil", "Vegetable Oil", "Bacon", "Avocado", "Peanut Butter"],
    "Cereals, Snacks & Nuts": {
        "Cereals": ["Cornflakes", "Oatmeal", "Muesli"],
        "Snacks": ["Crackers", "Rice Cakes", "Popcorn"],
        "Nuts": ["Walnuts", "Peanuts", "Almonds", "Cashews", "Pistachios"]
    },
    "Fruits": ["Apples", "Grapes", "Bananas", "Oranges", "Berries", "Mango", "Pineapple"],
    "Vegetables": ["Lettuce", "Carrots", "Broccoli", "Tomatoes", "Cucumbers", "Peppers", "Spinach"],
    "Sweets": ["Sugar", "Candy", "Jam", "Chocolate", "Honey", "Cookies"],
    "Beverages": ["Water", "Tea", "Herbal Tea", "Mineral Water", "Coffee", "Juice", "Sports Drinks"]
}

user_fridge = []

#Function to Add Items to Fridge
def add_to_fridge():
    st.header("Digital Fridge Setup")
    category = st.selectbox("Select a category", list(digital_fridge.keys()))
    
    #Check if the selected category has subcategories
    if isinstance(digital_fridge[category], dict):
        subcategory = st.selectbox("Select a subcategory", list(digital_fridge[category].keys()))
        item = st.selectbox("Select an item", digital_fridge[category][subcategory])
    else:
        item = st.selectbox("Select an item", digital_fridge[category])
    
    if st.button("Add Item to Fridge"):
        user_fridge.append(item)
        st.write(f"{item} added to your fridge!")

    #Display current fridge contents
    if user_fridge:
        st.write("Your current fridge contents:")
        for fridge_item in user_fridge:
            st.write(f"- {fridge_item}")

def suggest_recipes(food):
    # Use searchapi function to get recipes from the Tasty API
    recipes = searchapi(food)  # <-- Update: Call the searchapi function to get recipes
    return recipes  # <-- Update: Return the recipes list

def define_calories():
    st.header("Track Your Daily Calories")
    ## TODO
    calories = st.number_input("Enter your daily calorie intake", min_value=0, step=1)
    food = st.text_input("What kind of dished would you like? (comma seperated)", placeholder="chicken,beans")

    if st.button("Suggest Recipes"):
        recipes = suggest_recipes(food)  # <-- Update: Call suggest_recipes to get recipe list
        recipes = [recipe for recipe in recipes if recipe['nutrition'].get('calories', -1) < calories and recipe['nutrition'].get('calories', -1) > 0]

        st.write("Here are some recipe suggestions for you:")

        for i, recipe in enumerate(recipes):
            with st.expander(recipe["name"]):
                st.image(recipe["thumbnail_url"], caption=recipe["name"])
                st.markdown(f"**Description:** {recipe['description']}")
                st.markdown(f"**Prep Time:** {recipe['prep_time_minutes']} minutes")
                st.markdown(f"**Total Time:** {recipe['total_time_minutes']} minutes")
                st.markdown(f"**Servings:** {recipe['num_servings']}")
                st.markdown(f"**Calories:** {recipe['nutrition']['calories']} kcal")
                st.markdown(f"**Fat:** {recipe['nutrition']['fat']} gramms")
                st.markdown("**Instructions:**")
                st.write("\n".join([f"{step["display_text"]}" for step in recipe["instructions"]]))
        add_to_fridge()
     

# Frontend
if st.session_state['mode'] == "create_user_profile":
    create_user_profile()
elif st.session_state['mode'] == "set_fitness_goal":
     set_fitness_goal(weight=80) #Take from JSON file instead of hardcoded value
elif st.session_state['mode'] == "define_calories":
     define_calories()