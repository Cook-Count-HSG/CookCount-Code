import streamlit as st

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def suggest_recipes(calories):
    # Placeholder for recipe suggestions based on calorie intake
    if calories < 1500:
        return ["Salad", "Grilled Chicken", "Vegetable Soup"]
    elif 1500 <= calories < 2500:
        return ["Pasta", "Stir Fry", "Tacos"]
    else:
        return ["Burger", "Pizza", "Steak"]

st.title("Cook and Count")

st.header("Calculate Your BMI")
weight = st.number_input("Enter your weight in kg", min_value=0.0, step=0.1)
height = st.number_input("Enter your height in meters", min_value=0.0, step=0.01)
if st.button("Calculate BMI"):
    if height > 0:
        bmi = calculate_bmi(weight, height)
        st.write(f"Your BMI is: {bmi:.2f}")
    else:
        st.write("Please enter a valid height.")

st.header("Track Your Daily Calories")
calories = st.number_input("Enter your daily calorie intake", min_value=0, step=1)
if st.button("Suggest Recipes"):
    recipes = suggest_recipes(calories)
    st.write("Here are some recipe suggestions for you:")
    for recipe in recipes:
        st.write(f"- {recipe}")
