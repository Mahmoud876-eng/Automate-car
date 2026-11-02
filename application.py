from flask import Flask, render_template, request , session, redirect,jsonify
import requests
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from flask_session import Session
import re

import variable
#from flask_talisman import Talisman
#from flask_limiter import Limiter
#from flask_limiter.util import get_remote_address
import logging
uri = variable.password
app = Flask(__name__)
#https
#Talisman(app)
#DOS attack
#limiter = Limiter(
#    key_func=get_remote_address
#)
#limiter.init_app(app)
#sert secret key for session management
app.config["SECRET_KEY"] = "your_secret_key_here"
#session 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session = Session(app)
# Connect to MongoDB server
client = MongoClient(uri, server_api=ServerApi('1'))

# my database
db = client["infra_database"]

#my collection collection
users_collection = db["users"]
#chat bot 
from variable import api_version,key,endpoint
import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, session


app.secret_key = 'your_secret_key_here'  # Change this to a random, secure string
model_name = "gpt-4.1-nano"
deployment = "gpt-4.1-nano"
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=key,
)


#end chat bot
#prompt 
SYSTEM_PROMPT = """This project is about building a swarm-inspired safety system for road traffic.

The idea comes from how groups in nature move safely without central control—like birds flying in formation or fish schooling without colliding. Each individual follows simple local rules, and overall safety emerges at the group level.

In this project, vehicles, pedestrians, and cyclists are treated as moving agents in a shared space. A dedicated safety system continuously observes their positions, movement, and surroundings and reasons about how they interact over time.

The goal is not speed or efficiency, but preventing harm.

The system focuses especially on protecting vulnerable road users such as children, pedestrians, and cyclists. It assumes that humans make mistakes, sensors can be imperfect, and uncertainty is always present, so safety decisions are made conservatively.

Rather than reacting to accidents after they happen, the system tries to predict dangerous situations early and coordinate safe behavior across multiple vehicles so that no single vehicle has to take extreme action at the last moment.

In short:
It applies swarm-like thinking to traffic, treating the road as a shared, cooperative environment where safety emerges from coordination, prediction, and prioritization of human life.
"""

#end prompt 
#bot data

TOKEN = variable.TOKEN
CHAT_ID = variable.CHAT_ID 
#attack
@app.route('/')
#@limiter.limit("5 per minute")
def index():
    return render_template("index.html")
@app.route("/register", methods=["POST","GET"] )#connect the test1.py and the flask here got an error when u click the button in the middle
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")
        virf_password = request.form.get("confirm-password")
        if not email:
            return render_template("register.html", error="missing email")
        if not username:
            return render_template("register.html", error="missing username")
        if not password:
            return render_template("register.html", error="missing password")
        
        user_with_mail = users_collection.find_one({"email": email})
       
        if user_with_mail :
            return render_template("register.html", error="email already exists")
        
        if len(password) < 8:
            return render_template("register.html", error="password must be at least 8 characters long")
        if virf_password != password:
            return render_template("register.html", error="passwords do not match")

        user_data = {
                "username": username,
                "email": email,
                "password": password
            }    
        inserted_user = users_collection.insert_one(user_data)
        session["user_id"] = str(inserted_user.inserted_id)
        return render_template("home_user.html",username=username)
    return render_template("register.html")
@app.route("/login", methods=["POST","GET"] )
def login():
    print(request.method)
    if request.method == "POST":
        mail = request.form.get("email")
        password = request.form.get("password")
        
        if not password or not mail:
            return render_template("login.html", error="missing email or password")
        
        user_with_mail = users_collection.find_one({"email": mail})
        

        if not user_with_mail :
            return render_template("login.html", error="email not found")
        #check if the password is correct
        
        if user_with_mail:    
            if not user_with_mail['password'] == password:
                return render_template("login.html", error="password is incorrect")
            # Set session
            session["user_id"] = user_with_mail['_id']
            session["username"] = user_with_mail['username']
            return render_template("chatbot.html", username=user_with_mail['username'])
            #return render_template("home_usr.html",username=user_with_mail['username'])
        else:
            return render_template("error.html", message="mail not found")     
    return render_template("login.html")
@app.route("/bots", methods=["GET"])
def bots():
    return render_template("bots.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")

@app.route('/api/data', methods=["GET"]) 
def api_data():
    """Return current Firebase snapshot as JSON for dashboard polling."""
    FIREBASE_BASE = "https://synaptix-e0fa0-default-rtdb.europe-west1.firebasedatabase.app"
    url = f"{FIREBASE_BASE}/sensor_data.json"
    try:
        resp = requests.get(url, timeout=10)
        print(resp)
        resp.raise_for_status()
        raw = resp.json() or {}
        print(f"[application] api_data raw: {raw}")
        
        # Extract and process new variables
        gas_analog = raw.get("gas", 0)
        print(gas_analog)
        buzzer = raw.get("buzzer", False)
        distance = raw.get("distance", 0)
        flame = raw.get("flame", False)
        vibration = raw.get("vibration", False)
        gps = raw.get("gps", {"latitude": 0, "longitude": 0})

        # Apply thresholds
        payload = {
            "gas_analog": gas_analog,
            "buzzer": buzzer,
            "distance": distance,
            "flame": flame,
            "vibration": vibration,
            "gps": {
                "latitude": gps.get("latitude", 0),
                "longitude": gps.get("longitude", 0)
            },
        }
        
        return jsonify({
            "success": True,
            "data": payload,
        })
    except Exception as e:
        print(f"[application] api_data error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500
@app.route("/roads", methods=["POST","GET"] )
def road():
    return render_template("roads.html")
    
@app.route("/cars", methods=["GET"] )
def factuary():
    return render_template("cars.html")  
#maybe I  will add RAG to the chat bot later
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if 'answers' not in session:
        session['answers'] = [{
            "role": "system",
            "content": SYSTEM_PROMPT,
        }]
    
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if not user_input or user_input.strip() == "":
            return "Error: Please provide a valid user input."
        
        session['answers'].append({
            "role": "user",
            "content": user_input,
        })
        response = client.chat.completions.create(
            messages=session['answers'],
            max_completion_tokens=1024,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=deployment,
        )
        system_answer = response.choices[0].message.content
        session['answers'].append({
            "role": "system",
            "content": system_answer,
        })
        session.modified = True  # Ensure session is saved
    return render_template("chatbot.html", response=session['answers'])

   
@app.route("/logout", methods=["POST","GET"] )
def logout():
    session.clear()
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)