import os
import openai
from config import OPENAI_API_KEY, SEARCH_API_KEY, ENGINE_ID
from paperbot import Planner,parse_history,Editor
from tools import parse_data
from datetime import datetime

openai.api_key = OPENAI_API_KEY

cse_api_key = SEARCH_API_KEY
search_engine_id = ENGINE_ID

def main():

    #check if conversations folder is not empty
    if os.listdir("conversations") != []:
        #essay got interrupted, figure out what it was doing and resume
        print("conversations folder is not empty")
        #if essay.txt is in conversations folder, move it to main folder
        if "essay.txt" in os.listdir("conversations"):
            #name essay.txt to old_essay{timestamp}.txt
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            new_name = f"old_essay{timestamp}.txt"
            
            # Rename essay.txt in the 'conversations' directory
            os.rename(os.path.join("conversations", "essay.txt"), os.path.join("conversations", new_name))

            # Move the renamed file to the main directory
            os.rename(os.path.join("conversations", new_name), new_name)
        #parse_history()
    #prompt user for input
    query = input("What would you like to write about? ")


    Planner(query)

    if "essay.txt" in os.listdir("conversations"):
        os.rename("conversations/essay.txt", "essay.txt")

    #clear conversations folder

if __name__ == "__main__":
    main()