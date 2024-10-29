import streamlit as st
import openai

openai.api_key = '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'  # Replace with your actual OpenAI API key

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def suggest_recipes(calories):
    # Use GPT API to suggest recipes based on calorie intake
    prompt = f"Suggest some recipes for a daily calorie intake of {calories} calories."
    response = openai.Chat.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=100
    )
    recipes = response.choices[0].text.strip().split('\n')
    return recipes

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
