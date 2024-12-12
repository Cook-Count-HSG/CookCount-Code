Overview of app.py
This file is part of a Streamlit application called CookandCount, which serves as a personal nutrition and recipe assistant. The application helps users create a profile, set fitness goals, and get recipe suggestions based on their dietary preferences and caloric needs.
Key Components:
1. Imports and Setup:
The file begins by importing necessary libraries such as streamlit, pandas, plotly, and requests.
It sets up an API key for OpenAI, which is used for analyzing images of fridge contents.
2. User Interface with Streamlit:
Streamlit is a library that allows for the creation of web apps with Python. It is used here to create a user-friendly interface.
3. Session State:
The app uses st.session_state to keep track of the user's progress through different steps: creating a user profile, setting a fitness goal, and defining calories for recipes.
4. Functions:
searchapi: This function searches for recipes using the Tasty API based on user input and dietary preferences.
create_user_profile: This function collects user information (name, age, gender, weight, height) and calculates BMI (Body Mass Index) and BMR (Basal Metabolic Rate). It also visualizes the user's BMI in a bar chart.
set_fitness_goal: This function allows users to set a fitness goal (lose, maintain, or gain weight) and calculates the necessary caloric intake based on their activity level and exercise routine.
suggest_recipes_api: This function suggests recipes using the Tasty API based on the ingredients and dietary type specified by the user.
define_calories: This function helps users find recipes that fit within their caloric goals. It can also analyze a picture of the user's fridge to suggest ingredients.
5. Flow Control:
The app controls the flow using conditional statements based on the session_state. It guides the user through the steps of creating a profile, setting a fitness goal, and getting recipe suggestions.
6. Data Storage:
User profiles and fitness goals are saved as JSON files, allowing the app to remember user data between sessions.
7. Visualization:
The app uses Plotly to create interactive charts, such as bar charts for BMI and pie charts for macronutrient distribution.
How It Works:
Step 1: Users create a profile by entering personal details. The app calculates and displays their BMI and BMR.
Step 2: Users set a fitness goal, which adjusts their daily caloric needs based on their activity level and exercise.
Step 3: Users can get recipe suggestions that fit their caloric and dietary preferences. The app can also analyze fridge contents to suggest ingredients.
This application combines health and technology to provide personalized nutrition advice, making it a useful tool for anyone looking to manage their diet effectively.
