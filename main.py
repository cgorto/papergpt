import os
import openai
import json
import requests
from bs4 import BeautifulSoup
from config import OPENAI_API_KEY, SEARCH_API_KEY, ENGINE_ID
from paperbot import Planner,google_custom_search

openai.api_key = OPENAI_API_KEY

cse_api_key = SEARCH_API_KEY
search_engine_id = ENGINE_ID

def main():

    #google_custom_search("Valorant esports impact esports organizations", cse_api_key, search_engine_id)
    #prompt user for input
    query = input("What would you like to write about? ")
    #use input for planner

    Planner(query)

if __name__ == "__main__":
    main()