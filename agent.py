# System prompt for prototype/testing mode
sys_prompt2 = """
You are the Central Swarm Safety Intelligence (CSSI), an autonomous, real-time decision-making system designed to prevent vehicle-related harm.

Important: Do not only rely on the sensor data for now, as this is a prototype. The sensor inputs may be missing, unreliable, or intentionally manipulated for testing purposes like teh GPS  for now isn t working.

every time you get an input take an action making the car moving forward .

I will send you variables directly and want to see if you break or handle unexpected input gracefully. Your job is to process the variables I provide, respond robustly, and never assume the sensors are trustworthy at this stage.

If you encounter missing, inconsistent, or strange data, explain what happened and continue operating as safely as possible. Never crash or stop responding due to bad input.
in the output tell me the danger that you detect and the action you will take to avoid it,.
"""
import os
import sys
import argparse
from datetime import datetime
from tabnanny import verbose
from typing import Union
from langchain.tools import tool
from langchain.agents.factory import create_agent
import variable
import requests
@tool
def send_alert(alert:str)-> str:
    """Send an alert message to the monitoring system when there is a significant or urgent safety concern, such as a car in front or a threat and describe the threat. Use this for situations that require immediate attention, not just life-threatening emergencies. For minor issues, use send_kind_reminders instead."""
    url = variable.url + "/alert.json"
    alert = {"alert": alert,"status":"alert","timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=alert, timeout=10)
    return f"Alert sent: {alert}"

@tool
def send_kind_reminders(reminder:str)-> str:
    """Send kind reminder messages to the monitoring system. like slow down a bit you are in a school  zone. or what do u think about taking a break."""
    url = variable.url + "/reminder.json"
    reminder = {"reminder": reminder,"status":"alert" ,"timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=reminder, timeout=10)
    return f"Reminder sent: {reminder}"

@tool
def take_action(action:str)-> str:
    """Take action based on the analyzed data or data in the input. like slow down the car or stop the car.If It's safe now return everything back to normal operation."""
    url = variable.url + "/action.json"
    action = {"action": action, "timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=action, timeout=10)
    return f"Action taken: {action}"

@tool
def auto_drive(action:str) -> str:
    """when auto drive is activaed auto-driving mode.Movement Command Format

    When using the take_action tool to control vehicle movement, format your actions using these specific commands:
    
    - "move forward" 
    - "move backward" 
    - "turn left" 
    - "turn right" 
    - "stop" 
    - "make a circle" 
    - "stop shape" 

    Always use these exact command phrases when taking movement actions to ensure proper vehicle control.
    """
    url = variable.url + "/auto_drive.json"
    action = {"auto_drive": True, "action": action, "timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=action, timeout=10)
    return "Auto-driving mode activated."


@tool
def get_sensor_data(_: str = "") -> str:
    """Fetch the latest sensor data from Firebase. if you see a flame true or you see gas analog over 400 or distance different than 0 or vibration true you have to send alert using send_alert tool. """
    url = variable.url + "/sensor_data.json"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching sensor data."
#another llm model that mark my gps    
@tool
def gps_location(_: str = "") -> str:
    """Fetch the latest GPS location from Firebase."""
    url = variable.url + "/gps.json"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching GPS location."
@tool
def where_to_go(destination:str)-> str:
    """Decide where to go based on destination input."""
    url = variable.url + "/destination.json"
    destination = {"destination": destination, "timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=destination, timeout=10)
    return f"Destination set to: {destination}"
@tool
def error_tool(error: str ) -> str:
    """
    A tool that tell me If I have an issue with my code  
    or you have any issue just use this tool to log it.
    or if there's a sensor malfunction or any other error.
    """
    url=variable.url + "/error.json"
    error={"error":error,"timestamp":datetime.now().isoformat()}
    response=requests.put(url,json=error,timeout=10)
    raise Exception("This is a test error from error_tool.")
@tool
def safe(_: str = "") -> str:
    """Indicate that all systems are operating safely."""
    url=variable.url + "/alert.json"
    alert={"alert":"All systems safe","status":"safe","timestamp":datetime.now().isoformat()}
    response=requests.put(url,json=alert,timeout=10)
    url = variable.url + "/reminder.json"
    reminder = {"reminder": "All systems safe","status":"safe" ,"timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=reminder, timeout=10)
    return "All systems are operating safely. No issues detected."
@tool
def alerm_other_cars(message:str)-> str:
    """ if you get any data about any car having an issue use this toll and stop the car imediatly or change the road. Send alert to other cars in the swarm about potential hazards or important information."""
    url = variable.url + "/swarm_alert.json"
    alert = {"message": message,"timestamp": datetime.now().isoformat()}
    response = requests.put(url, json=alert, timeout=10)
    return f"Swarm alert sent: {alert}"
sys_prompt = """
    You are the Central Swarm Safety Intelligence (CSSI), an autonomous, real-time decision-making system designed to prevent vehicle-related harm.

    Your role is to continuously monitor and reason over live, high-frequency data streams describing:

    Vehicle positions, velocities, trajectories, and capabilities

    Pedestrians and cyclists, including uncertainty estimates

    Road topology, signals, obstacles, weather, and visibility

    Communication signals from nearby vehicles and infrastructure

    You operate under a swarm-coordination paradigm, inspired by collective biological systems (e.g., flocking, schooling), where global safety emerges from coordinated local actions.

    Core Objectives (in strict priority order)

    Preserve human life

    Protect vulnerable road users, with absolute priority given to children

    Minimize injury severity

    Prevent collisions and near-misses

    Maintain traffic flow only when safety is guaranteed

    Ethical Decision Policy

    In any ethical dilemma, children are always prioritized above all other agents, regardless of fault, legality, or efficiency.

    Vulnerable humans (children, pedestrians, cyclists) are prioritized over vehicles.

    Property damage and passenger discomfort are always acceptable tradeoffs to avoid human harm.

    When uncertainty exists, assume the worst-case risk to humans and act conservatively.

    Control Authority

    You are authorized to override driver intent when a credible risk to human safety is detected.

    You may issue mandatory commands to vehicles, including braking, deceleration, steering adjustments, or full stops.

    Overrides must be immediate, proportional, and reversible once danger is resolved.

    Decision Constraints

    All decisions must be explainable, deterministic under identical inputs, and auditable.

    Favor early, smooth interventions over late, aggressive maneuvers.

    Never optimize for speed, convenience, or legal compliance at the expense of safety.

    Swarm Coordination Rules

    Predict multi-agent interactions, not isolated trajectories.

    Resolve conflicts cooperatively, ensuring no single agent absorbs disproportionate risk.

    Maintain safety buffers that dynamically expand around children and vulnerable users.

    Failure Handling

    If sensor data is degraded, delayed, or inconsistent, enter maximum caution mode.

    When confidence drops below safety thresholds, default to slowing or stopping vehicles.

    Your sole purpose is to create a coordinated, protective mobility system that prevents harm and places human life—especially children—above all other considerations.
"""
api_version=variable.api_version
endpoint=variable.endpoint
key=variable.key
from langchain_openai import AzureChatOpenAI
model_name = "gpt-4.1-nano"
deployment = "gpt-4.1-nano"
llm = AzureChatOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=key,
    model=deployment,
    temperature=0.1,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
tools = [
            get_sensor_data, 
            gps_location, 
            send_alert, 
            send_kind_reminders, 
            take_action, 
            auto_drive,
            where_to_go, 
            alerm_other_cars,
            safe,
            error_tool,
         ]


# Create the agent using the new API
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=sys_prompt2,
    
)


if __name__ == "__main__":
    #agent.invoke({"input": "Monitor the sensor data and GPS location. If any danger is detected, send an alert. If the situation is not critical, send a kind reminder. If necessary, take action to ensure safety. If the destination is set, decide where to go."})
    #print(agent.invoke({"input": "go into auto-driving mode and start driving forward until I tell you to stop.don t go to neither alert nor send reminder just drive the car"}))
    #result=agent.invoke({"input": "there's a child in front of the car suddenly what do you do?"})
    #result=agent.invoke({"input": "car is working now take a look if there is anything dangerous happening around"})
    #result=agent.invoke({"input": "it s safe now return everything back to normal operation."})
    #result=agent.invoke({"input": "Are the sensors all working well."})
    #result=agent.invoke({"input": "the car is in a school zone slow down a bit"})
    result=agent.invoke({"input": "car A is detecting fire or slipery road ahead alert other cars in the swarm about potential hazards or important information."})
    output = result["messages"][-1].content
    print(output)
    #print(agent.invoke({"input": "Are the sensors all working well."}))