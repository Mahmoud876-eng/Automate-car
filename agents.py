"""
LangChain Agent Workflow (Minimal, Runnable)

Features:
- Tools: calculator, current_time
- Agent: OpenAI Functions-style via langchain-openai
- CLI: single question or interactive loop

Setup (Windows):
  1) python -m venv .venv
  2) .venv\Scripts\activate
  3) pip install -r requirements.txt
  4) setx OPENAI_API_KEY "YOUR_KEY"
  5) python agents.py --question "What is 12*(7-3) and current time?"
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Union

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType


# ----------------------
# Tools
# ----------------------
@tool
def calculator(expression: str) -> Union[int, float]:
	"""Evaluate a basic arithmetic expression, e.g., '2 * (3 + 4)'.
	Supports + - * / and parentheses.
	"""
	allowed = set("0123456789+-*/(). ")
	if not set(expression) <= allowed:
		raise ValueError("Only digits and + - * / ( ) are allowed.")
	# Safe eval: disable builtins
	return eval(expression, {"__builtins__": {}}, {})


@tool
def current_time(_: str = "") -> str:
	"""Return current local date and time."""
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ----------------------
# Agent Builder
# ----------------------
def build_agent(verbose: bool = True):
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		print(
			"ERROR: OPENAI_API_KEY not set.\n"
			"Set it with: setx OPENAI_API_KEY \"YOUR_KEY\" and restart terminal."
		)
		sys.exit(1)

	model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	llm = ChatOpenAI(model=model_name, temperature=0)
	tools = [calculator, current_time]
	agent = initialize_agent(
		tools=tools,
		llm=llm,
		agent=AgentType.OPENAI_FUNCTIONS,
		verbose=verbose,
		max_iterations=6,
		handle_parsing_errors=True,
	)
	return agent


def ask_agent(question: str) -> str:
	"""Ask the agent a single question and return the answer string."""
	agent = build_agent(verbose=True)
	result = agent.invoke({"input": question})
	# Agent executor returns a dict; 'output' contains final text
	return result.get("output", "")


# ----------------------
# CLI Entrypoints
# ----------------------
def interactive_demo():
	print("\nInteractive agent. Type 'exit' to quit.\n")
	agent = build_agent(verbose=True)
	while True:
		try:
			q = input("You> ").strip()
		except (KeyboardInterrupt, EOFError):
			print("\nBye!")
			break
		if not q:
			continue
		if q.lower() in {"exit", "quit"}:
			print("Bye!")
			break
		result = agent.invoke({"input": q})
		print(f"Agent> {result.get('output', '')}\n")


def main(argv=None):
	parser = argparse.ArgumentParser(description="Run a minimal LangChain agent")
	parser.add_argument(
		"--question",
		"-q",
		help="Ask a single question instead of interactive mode",
	)
	args = parser.parse_args(argv)

	if args.question:
		answer = ask_agent(args.question)
		print(answer)
	else:
		interactive_demo()


if __name__ == "__main__":
	main()
