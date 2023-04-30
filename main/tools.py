import os
import openai
import json
import requests
import tiktoken
from bs4 import BeautifulSoup
from config import SERVICE_ACCOUNT_FILE, SCOPES
from colorama import init, Fore, Style
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('docs', 'v1', credentials=credentials)

def create_doc(title):
    try:
        body = {
            'title': title
        }
        doc = service.documents() \
            .create(body=body).execute()
        print(f'Created document with title: {doc.get("title")} and URL:'
              f'https://docs.google.com/document/d/{doc.get("documentId")}/edit')
    except HttpError as error:
        print(f'An error occurred: {error}')
        doc = None

    return doc

def update_doc_content(doc_id, new_content):
    requests = [{
        'replaceAllText': {
            'containsText': {
                'text': '{{PLACEHOLDER}}',
                'matchCase': False
            },
            'replaceText': new_content
        }
    }]

    result = service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    print(f"Replaced {result['replies'][0]['replaceAllText']['occurrencesChanged']} occurrences.")

def create_and_update_doc(title, file_name):
    # Create the document
    doc = create_doc(title)
    doc_id = doc.get('documentId')

    # Read the content from the file
    with open(file_name, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Update the document's content with the content from the file
    update_doc_content(doc_id, file_content)



def write_response(response, file_name):
    with open(f"conversations/" + file_name + ".txt", "a+") as f:
        #if response is a dictionary, convert to string
        if isinstance(response, dict):
            response = json.dumps(response)
        #convert response to string if it isn't already
        response = str(response)
        f.write(response + "\n")
    return


def parse_data(data):
    json_data = None

    if isinstance(data, dict):
        json_data = data
    else:
        try:
            # Try to load the data as JSON
            json_data = json.loads(data)
        except json.JSONDecodeError:
            # If the data is not in JSON format, parse the second format
            lines = data.split("\n")
            summary = None
            score = None

            for i, line in enumerate(lines):
                if "Summary:" in line:
                    summary = line.replace("Summary:", "").strip() or lines[i + 1].strip()
                elif "Score:" in line:
                    score = int(line.replace("Score:", "").strip() or lines[i + 1].strip())

            if summary is not None and score is not None:
                json_data = {"Summary": summary, "Score": score}

    return json_data

# Test cases




def extract_first_json_obj(string):
    decoder = json.JSONDecoder()
    try:
        obj, idx = decoder.raw_decode(string)
        return obj
    except ValueError:
        return None

def write_messages(messages, file_name):
    with open(f"conversations/" + file_name + ".txt", "w+") as f:
        f.write("[")
        for message in messages:
            f.write('{"role":''"' + message["role"] + '", "content":' + message["content"] + "}" + "\n")
        f.write("]")
    return

def read_messages(file_name):
    with open(f"conversations/" + {file_name} + ".txt", "r") as f:
        messages = json.load(f)
    return messages

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