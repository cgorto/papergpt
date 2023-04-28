import os
import openai
import json
import requests
import tiktoken
from bs4 import BeautifulSoup
from config import OPENAI_API_KEY, SEARCH_API_KEY, ENGINE_ID

openai.api_key = OPENAI_API_KEY

cse_api_key = SEARCH_API_KEY
search_engine_id = ENGINE_ID

outline = ""


def num_tokens_from_messages(messages):
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
    except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  # note: future models may deviate from this
    num_tokens = 0
    
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def google_custom_search(query, cse_api_key, search_engine_id):
    # Base URL for the API
    api_url = "https://www.googleapis.com/customsearch/v1"

    # Set the API parameters
    params = {
        "key": cse_api_key,
        "cx": search_engine_id,
        "q": query
    }

    # Send the request to the API
    response = requests.get(api_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        json_data = response.json()

        # Extract the search results
        items = json_data.get("items", [])

        # Extract and return only the 'title' and 'link' from the search results
        results = [{"title": item["title"], "link": item["link"]} for item in items]
        #limit results to 7
        results = results[:7]

        for result in results:
            response = Reader(result)
            #write response to a file
            with open(f"readerlog.txt", "w+") as f:
                f.write(response)
            #find first {, store everything after { as response
            index = response.find("{")
            response = response[index:]
            dictresponse = json.loads(response)
            result["summary"] = dictresponse["Summary"]
            result["score"] = dictresponse["Score"]
            print("i hope it's not stuck here")
            

        return results
    else:
        print(f"Request failed with status code {response.status_code}")
        return []
    
def extract_text_from_url(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get the text from the HTML
        text = soup.get_text()

        # Remove leading and trailing whitespace and collapse multiple spaces
        text = " ".join(text.strip().split())

        return text
    else:
        print(f"Request failed for URL {url} with status code {response.status_code}")
        return ""

def generate_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        #model="gpt-4-0314",
        #CHANGED TO CHEAPER MODEL WHILE TESTING
        #model="gpt-3.5-turbo",
        
        messages=messages,
    )
    return response['choices'][0]['message']['content'], response['choices'][0]['finish_reason']

def generate_response_gpt4(messages): #THIS IS SOLELY FOR TESTING PURPOSES, REMOVE FROM PLANNER WHEN USING ALL GPT-4 AND REPLACE MODEL IN ABOVE FUNCTION
    response = openai.ChatCompletion.create(
        model="gpt-4",
        
        messages=messages,
    )
    return response['choices'][0]['message']['content'], response['choices'][0]['finish_reason']

def Planner(user_input):
    global outline

    #store planner.txt into content
    with open("system.txt", "r") as f:
        plannercontent = f.read()
    messages = [
        {"role":"system", "content":f'{plannercontent}'},
        #get user input at some point in time, how we do this is undecided
        {"role":"user", "content":user_input} #TEST TEST TEST
        ]
    response =""
    #add something to know when to stop
    calls = 0
    while "[DONE]" not in response:
        calls += 1
        print(calls)
        response,finish_reason = generate_response_gpt4(messages)
        messages.append({"role":"assistant", "content":response})
        print(response)

        #if && in response, find second && and store everything between the two && as the outline
        if "&&" in response:
            index = response.find("&&")
            next_index = response.find("&&", index + 1)
            outline = response[index + 2:next_index]



        
        #beginning of agent calls

        if "[RESEARCHER]" in response:
            #will be format of [RESEARCHER]:"[topics]", get topics in between the two quotes, store as topics
            topics = response.split("[RESEARCHER]:")[1]
            if topics[0] == '"':
                topics = topics[1:-1]
            
            top_sources = Researcher(topics)
            researcher_calls+=1
            #save top_sources as a text file, increment the number at the end of the file name
            with open(f"researcher{researcher_calls}.txt", "w+") as f:
                f.write(top_sources)
            print("Researcher done researching")
            messages.append({"role":"user" , "content":f"[RESEARCHER]: Here is the list of sources: \n {top_sources}"})


        if "[WRITER]" in response:
            #will be format of [WRITER]:"Subset of Sources", section_num. store sources as sources, store section_num as num
            sources = response.split("[WRITER]:")[1]
            if sources[0] == '"':
                #find comma after quotes, store everything before comma as sources
                comma_index = sources.find(",")
                sources = sources[1:comma_index]
                #store everything after comma as num
                num = sources[comma_index + 1:]
                section = Writer(num,sources)
                print("Writer done writing")
                messages.append({"role":"user", "content":f"[WRITER]: Here is the finished section: \n {section}"})

        if "[EDITOR]" in response:
            changes = Editor()
            print(changes)
            messages.append({"role":"user", "content":f"[EDITOR]: Here are the changes: \n {changes}"})



    return

def Researcher(topics):
    global outline
    #store researcher.txt into content
    with open("researcher.txt", "r") as f:
        researchercontent = f.read()
    messages = [
        {"role":"system", "content":f'{researchercontent}'},
        {"role":"user", "content":f'Search Topics:{topics}\n\n Outline: {outline}'}
        ]
    print("Researcher is working")
    response,a = generate_response(messages)
    messages.append({"role":"assistant", "content":response})
    print(response)
    while "[RETURN]" not in response:
        if "[SEARCH]" in response:
            search_query = response.split("[SEARCH]:")[1]
            if search_query[0] == '"':
                search_query = search_query[1:-1]
            search_results = google_custom_search(search_query, cse_api_key, search_engine_id)
            print(search_results)
            print("Researcher is working")
            messages.append({"role":"user", "content":f"Search Results: {search_results}"})
            response,a = generate_response(messages)
            messages.append({"role": "assistant", "content": response})
            print(response) #remove later on
    
    #sort the top 10 search_results by score
    search_results.sort(key=lambda x: x["score"], reverse=True)
    #return the top 10 search_results
    return search_results[:10]



def Reader(result):
    global outline
    #store reader.txt into content
    with open("reader.txt", "r") as f:
        readercontent = f.read()

    page_content = extract_text_from_url(result["link"])

    if page_content == "":
        return json.dumps({})

    messages = [
        {"role":"system", "content":f'{readercontent}'},
        {"role":"user", "content":f'Outline: {outline}\n\n Source: {page_content}'}
        ]

    tokens = num_tokens_from_messages(messages)
    over_prop = tokens / 8192
    if over_prop > 1:
        print("source too long :(")
    while num_tokens_from_messages(messages) > 8192:
        #remove amount of text that is over the limit based on the proportion of tokens over the limit
        #remove from the end of the source, ensuring that there are enough tokens for a response (500 tokens)

        messages[1]["content"] = messages[1]["content"][:int(len(messages[1]["content"]) * (1 / over_prop))-500]

    print("Reader is working")
    response,a = generate_response(messages)
    print(response) #remove later on
    if not response:
        return json.dumps({})
    return response



def Writer(num,sources):
    global outline
    #store writer.txt into content
    with open("writer.txt", "r") as f:
        writercontent = f.read()
    messages = [
        {"role":"system", "content":f'{writercontent}'},
        {"role":"user", "content":f'Outline: {outline}\n\n Sources: {sources} \n\n Section for you to write: {num}'}
        ]
    print("Writer is working")
    response,finish_reason = generate_response(messages)
    messages.append({"role":"assistant", "content":response})
    if finish_reason == 'length':
        extra_response,a = generate_response(messages)
        print("Writer is working")
        messages.append({"role":"assistant", "content":extra_response})
    
    response += " " + extra_response
    #create a file with the name of the topic or update file if it already exists, adding response to the file
    with open(f"essay.txt", "a+") as f:
        f.write("\n" + "$" + num + "$" + "\n" + response)
    return response
def Editor():
    global outline
    #store editor.txt into content
    with open("editor.txt", "r") as f:
        editorcontent = f.read()
    #store essay.txt into essay
    with open("essay.txt", "r") as f:
        essay = f.read()
    messages = [
        {"role":"system", "content":f'{editorcontent}'},
        {"role":"user", "content":f'Outline: {outline}\n\n Essay: {essay}'}
        ]
    #while "[STOP]" not in response:
    while "[STOP]" not in response:
        print("Editor is working")
        response,a = generate_response(messages)
        if "[STOP]" in response:
            #remove [STOP] from anywhere in response
            response = response.replace("[STOP]", "")
            return response
        #get the first three characters of response
        first_three = response[:3]
        num = first_three[1]
        with open("essay.txt", "r") as f:
            essay = f.read()
        #get the index of the first $num$ in essay
        index = essay.find(first_three)
        #get the index of the next $num$ in essay
        next_index = essay.find("$" + str(int(num) + 1) + "$")
        #replace the text between the two $num$ with response
        essay = essay[:index] + response + essay[next_index:]
        messages.append({"role":"assistant", "content":response})

    with open(f"essay.txt", "w+") as f:
        f.write(response)
    return 
#def Citer():
    #return