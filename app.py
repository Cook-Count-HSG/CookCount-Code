import streamlit as st
from tasty_api import searchapi  # <-- Add this import to bring in the searchapi function

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def suggest_recipes(calories):
    # Use searchapi function to get recipes from the Tasty API
    recipes = searchapi()  # <-- Update: Call the searchapi function to get recipes
    return recipes  # <-- Update: Return the recipes list

# Streamlit App Code
st.header("Calculate Your BMI")
weight = st.number_input("Enter your weight in kg", min_value=0.0, step=0.1)
height = st.number_input("Enter your height in meters", min_value=0.01, step=0.01)  # Set min_value > 0

if st.button("Calculate BMI"):
    if height > 0:
        bmi = calculate_bmi(weight, height)
        st.write(f"Your BMI is: {bmi:.2f}")
    else:
        st.write("Please enter a valid height.")

st.header("Track Your Daily Calories")
calories = st.number_input("Enter your daily calorie intake", min_value=0, step=1)

if st.button("Suggest Recipes"):
    recipes = suggest_recipes(calories)  # <-- Update: Call suggest_recipes to get recipe list
    st.write("Here are some recipe suggestions for you:")
    for recipe in recipes:
        st.write(f"- {recipe}")  # <-- Display each recipe in Streamlit
