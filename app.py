import json
from turtle import right
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import base64
from openai import OpenAI
import os

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = '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'

# Set the title of the Streamlit app
st.title("CookCount: Your Personal Nutrition and Recipe Assistant")

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'create_user_profile'

# Function to search for recipes using the Tasty API
def searchapi(food, dietary_type):
    url = "https://tasty.p.rapidapi.com/recipes/list"
    querystring = {"from": "0", "size": "50", "tags": f"under_30_minutes,{dietary_type}", "q": food}

    headers = {
        "x-rapidapi-key": "ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586",
        "x-rapidapi-host": "tasty.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    common_emojis = {
        "vegetarian": "🥗",
        "vegan": "🌱",
        "pescatarian": "🐟",
        "keto": "🥩",
        "paleo": "🍖",
        "gluten-free": "🚫🍞",
        "dairy-free": "🚫🥛",
    }

    results = data.get("results", [])

    for result in results:
        if dietary_type != "":
            result["name"] = result.get("name", "") + " " + common_emojis[dietary_type]

    return results

# Step 1: User Profile Creation and BMI/BMR calculation
def create_user_profile():
    st.header("Create User Profile (Step 1/3)")
    first_name = st.text_input("Enter your first name")
    last_name = st.text_input("Enter your last name")
    gender = st.selectbox("Select your gender", ["Male", "Female"])
    age = st.number_input("Enter your age", min_value=1, step=1)
    weight = st.number_input("Enter your weight in kg", min_value=0.1, step=0.1)
    height = st.number_input("Enter your height in cm", min_value=0.1, step=0.1)

    if st.button("Save Profile"):
        bmi = weight / ((height / 100) ** 2)

        def calculate_bmr(gender, weight, height, age):
            if gender.lower() == "male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            return bmr

        bmr = calculate_bmr(gender, weight, height, age)

        user_data = {
            "name": f"{first_name} {last_name}",
            "age": age,
            "gender": gender,
            "BMI": bmi,
            "BMR": bmr
        }

        # Display user profile
        st.write("Profile is saved!")
        st.write(f"Your BMI is **{bmi:.2f}** and your BMR is **{bmr:.2f}**")

        # Calculate normal BMI range for gender
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

        # Create a bar chart with the BMI range and user-specific BMI
        fig = px.bar(
            df,
            x='BMI',
            y='single_bar',
            color=["Underweight", "Normal weight", "Overweight", "Serverly Overweight (Obesity Grade I)", "Obesity Grade II", "Obesity Grade III"],
            color_discrete_map={
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

        # Adjustments to the layout of the chart
        fig.update_yaxes(visible=False, showticklabels=False)
        fig.add_vline(x=bmi)
        fig.add_annotation(x=bmi - 2.75, y=.3, text="Your BMI", showarrow=False)
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

        # Display the chart in streamlit
        st.plotly_chart(fig)

        # Save user profile in json file
        with open("data/user_profile.json", "w") as f:
            json.dump(user_data, f)

        st.session_state['mode'] = 'set_fitness_goal'
        st.button("Continue")

# Step 2: Fitness Goal and Calorie Adjustment based on PAL, Exercise and Calorie Goal
def set_fitness_goal(weight: int, bmr: float):
    st.header("Set Your Fitness Goal (Step 2/3)")

    # Step 2.1: Select fitness goal out of 3 options and target
    fitness_goal = st.selectbox("Choose your fitness goal", ["Lose weight", "Maintain weight", "Gain weight"])

    if fitness_goal in ["Lose weight", "Gain weight "]:
        target_amount = st.number_input("Enter your target weight change in kg", step=0.1)
        time_period = st.number_input("Enter your target time period in weeks", min_value=1, step=1)
    else:
        st.write("You have selected to maintain your current weight, so no weight change target is needed.")
        target_amount = 0
        time_period = 0

    # Step 2.2: Calculate the calorie change factor based on fitness goal
    total_caloric_deficit = target_amount * 7700.
    if fitness_goal == "Lose weight":
        calorie_adjustment = -total_caloric_deficit / (7. * time_period)
    elif fitness_goal == "Gain weight":
        calorie_adjustment = total_caloric_deficit / (7. * time_period)
    else:
        calorie_adjustment = 0

    # Step 2.3: Select Physical Activity Level (PAL)
    st.header("Physical Activity Level (PAL)")
    activity_level = st.selectbox("Select your activity level", [
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

        total_daily_expenditure = (pal + 1. / 7. * hours_of_sport * 5. / 24.) * bmr

        # Step 2.6: Total Daily Expenditure and Caloric Goal Calculation
        goal_calories = total_daily_expenditure + calorie_adjustment

        # Step 2.7: Display results
        st.write(f"With your activity level and exercise, your daily caloric expenditure is: {total_daily_expenditure:.2f} calories.")
        st.write(f"To reach your fitness goal, your daily calorie target should be: {goal_calories:.2f} calories.")

        # Calculate daily protein, fat and carbs intake in grams based on the goal calories
        protein = round(1.5 * weight)
        protein_kcals = protein * 5.1
        fat = round(0.7 * weight)
        fat_kcals = fat * 9
        carbs_kcals = goal_calories - protein_kcals - fat_kcals
        carbs = round(carbs_kcals / 5.1)

        # Create a dataframe to be used in the pie chart
        df = pd.DataFrame({
            "Type": ["Protein", "Carbs", "Fat"],
            "Calories": [protein, carbs, fat]
        })

        # Create a pie chart that displays the daily intake of protein, fat and carbs
        fig = px.pie(
            df,
            values='Calories',
            names='Type',
            title=f'Grams of Protein, Fat and Carbs for a {goal_calories:.2f} Calorie Diet',
            category_orders={"Type": df["Type"].tolist()},
            width=650,
            height=400
        )

        # Adjustments to the layout of the chart
        fig.update_layout(hovermode=False)
        fig.update_traces(
            textinfo='value',
            texttemplate='%{value}g (%{percent})',
            marker=dict(colors=['#A52019', '#3E5982', '#E1A100']),
            sort=False
        )

        # Display the chart in streamlit
        st.plotly_chart(fig)

        # Step 2.8: Save fitness goal and calorie adjustment in json file
        fitness_data = {
            "fitness_goal": fitness_goal,
            "target_amount": target_amount,
            "time_period": time_period,
            "activity_level": activity_level,
            "pal": pal,
            "hours_of_sport": hours_of_sport,
            "total_daily_expenditure": total_daily_expenditure,
            "goal_calories": goal_calories
        }

        # Save in json
        with open("data/fitness_goal.json", "w") as f:
            json.dump(fitness_data, f)
        st.write("Your fitness goal details have been saved.")
        st.session_state['mode'] = 'define_calories'
        st.button("Continue")

# Function to suggest recipes using the Tasty API
def suggest_recipes_api(food, dietary_type):
    recipes = searchapi(food, dietary_type)
    return recipes

# Step 3: Define calories and get recipe suggestions
def define_calories(weight: int, goal_calories: float):
    st.header("Get Recipes For You (Step 3/3)")
    calories = st.number_input("How many calories should the recipe have?", min_value=0, step=1)

    dietary_type = st.selectbox("Select your dietary type", ["", "vegetarian", "vegan", "pescatarian", "keto", "paleo", "gluten-free", "dairy-free"])

    image = st.file_uploader("Upload a picture of your fridge", type=["jpg", "jpeg", "png"])
    if image is not None:
        st.image(image, caption='Uploaded Fridge Image')

    food_ai = []
    if image is not None:
        client = OpenAI()

        # Encode the uploaded image
        base64_image = base64.b64encode(image.read()).decode('utf-8')

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "analyze the fridge content and give me three diverse items as a comma separated lower-case list which might fit as a recipe. Only use single word ingredient names",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                    "temperature": 0.0
                }
            ],
        )

        food_ai = response.choices[0].message.content
        st.write(f"Ingredients detected: {food_ai}")

    food = st.text_input("What other ingredients do you want to use for cooking?", placeholder="chicken, beans")

    if food_ai:
        if food:
            food = food_ai + "," + food
        else:
            food = food_ai

    food = food.replace(" ", "")

    recipes = suggest_recipes_api(food, dietary_type)
    recipes = [recipe for recipe in recipes if recipe['nutrition'].get('calories', -1) < calories and recipe['nutrition'].get('calories', -1) > 0]

    if st.button("Suggest Recipes"):
        st.write("Here are some recipe suggestions for you:")

        for i, recipe in enumerate(recipes):
            with st.expander(recipe["name"]):
                st.image(recipe["thumbnail_url"], caption=recipe["name"])
                st.markdown(f"**Description:** {recipe['description']}")
                st.markdown(f"**Prep Time:** {recipe['prep_time_minutes']} minutes")
                st.markdown(f"**Total Time:** {recipe['total_time_minutes']} minutes")
                st.markdown(f"**Servings:** {recipe['num_servings']}")
                st.markdown(f"**Calories:** {recipe['nutrition']['calories']} kcal")
                st.markdown(f"**Fat:** {recipe['nutrition']['fat']} grams")
                st.markdown("**Instructions:**")
                st.write("\n".join([f"{step['display_text']}" for step in recipe["instructions"]]))

                recipe_to_save = {
                    "name": recipe["name"],
                    "description": recipe["description"],
                    "prep_time_minutes": recipe["prep_time_minutes"],
                    "total_time_minutes": recipe["total_time_minutes"],
                    "num_servings": recipe["num_servings"],
                    "nutrition": recipe["nutrition"],
                    "thumbnail_url": recipe["thumbnail_url"],
                    "instructions": [step["display_text"] for step in recipe["instructions"]]
                }

                with open(f"recipies/{recipe['name']}.json", "w") as f:
                    json.dump(recipe_to_save, f)

                goal_calories -= recipe['nutrition']['calories']
                st.write(f"Updated goal calories for the day: {goal_calories:.2f} kcal")

                # Calculate daily protein, fat and carbs intake in grams based on the goal calories
                protein = round(1.5 * weight)
                protein_kcals = protein * 5.1
                fat = round(0.7 * weight)
                fat_kcals = fat * 9
                carbs_kcals = goal_calories - protein_kcals - fat_kcals
                carbs = round(carbs_kcals / 5.1)

                # Create a dataframe to be used in the pie chart
                df = pd.DataFrame({
                    "Type": ["Protein", "Carbs", "Fat"],
                    "Calories": [protein, carbs, fat]
                })

                # Create a pie chart that displays the daily intake of protein, fat and carbs
                fig = px.pie(
                    df,
                    values='Calories',
                    names='Type',
                    title=f'Updated grams left of Protein, Fat and Carbs for a {goal_calories:.2f} Calorie Diet',
                    category_orders={"Type": df["Type"].tolist()},
                    width=650,
                    height=400
                )

                # Adjustments to the layout of the chart
                fig.update_layout(hovermode=False)
                fig.update_traces(
                    textinfo='value',
                    texttemplate='%{value}g (%{percent})',
                    marker=dict(colors=['#A52019', '#3E5982', '#E1A100']),
                    sort=False
                )

                # Display the chart in streamlit
                st.plotly_chart(fig)

# Frontend logic to control the flow of the app
if st.session_state['mode'] == "create_user_profile":
    create_user_profile()
elif st.session_state['mode'] == "set_fitness_goal":
    with open("data/user_profile.json", "r") as f:
        user_profile = json.load(f)
    set_fitness_goal(weight=user_profile['BMI'], bmr=user_profile['BMR'])
elif st.session_state['mode'] == "define_calories":
    with open("data/user_profile.json", "r") as f:
        user_profile = json.load(f)
    with open("data/fitness_goal.json", "r") as f:
        fitness_goal = json.load(f)
    define_calories(weight=user_profile['BMI'], goal_calories=fitness_goal['goal_calories'])