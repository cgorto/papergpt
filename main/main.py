import os
import openai
from config import OPENAI_API_KEY, SEARCH_API_KEY, ENGINE_ID
from paperbot import Planner,parse_history

openai.api_key = OPENAI_API_KEY

cse_api_key = SEARCH_API_KEY
search_engine_id = ENGINE_ID

def main():

    #check if conversations folder is not empty
    if os.listdir("conversations") != []:
        #essay got interrupted, figure out what it was doing and resume
        print("conversations folder is not empty")
        #parse_history()
    #prompt user for input
    query = input("What would you like to write about? ")
    #use input for planner
    Planner(query)

    #move essay, sources from conversations folder to paper folder
    #clear conversations folder

if __name__ == "__main__":
    main()