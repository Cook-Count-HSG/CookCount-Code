import streamlit as st
import tasty
import http.client
import requests

tasty.api_key = 'ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586'

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def suggest_recipes(calories):
    # Use Tasty API to suggest recipes based on calorie intake


    conn = http.client.HTTPSConnection("tasty.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586",
        'x-rapidapi-host': "tasty.p.rapidapi.com"
    }

    conn.request("GET", "/recipes/list?from=0&size=20&tags=under_30_minutes", headers=headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"), max_tokens=1000)

  
def searchapi():
    url = "https://tasty.p.rapidapi.com/recipes/list"

    querystring = {"from":"0","size":"20","tags":"under_30_minutes"}

    headers = {
	"x-rapidapi-key": "ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586",
	"x-rapidapi-host": "tasty.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring) #in methode rein, erst wenn der user inputs gegeben hat

    print(response.json())
    
st.title("Cook and Count with Tasty integration")

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
