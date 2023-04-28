# PaperGPT

PaperGPT is an autonomous academic paper writing and research tool powered by OpenAI's GPT-4. It simplifies the process of writing research papers by generating outlines, conducting research, summarizing sources, writing sections, and providing editing suggestions based on user input.

## Features

- Automatically generates an outline for the research paper
- Conducts research on given topics using Google Custom Search
- Summarizes the content of top sources
- Writes sections of the research paper based on the outline and sources
- Provides editing suggestions for the written content

## Usage

Run the **'main.py'** script and provide the user input when prompted. The script will generate an outline, conduct research, write sections, and provide editing suggestions based on the user input.
The generated content will be saved in the **'conversations'** directory with separate logs for each stage of the process.

## Structure

The main components of PaperGPT are:
- **'Planner'**: Generates an outline for the research paper based on user input
- **'Researcher'**: Conducts research on given topics and summarizes the content of top sources
- **'Reader'**: Extracts and summarizes the content from a specific URL
- **'Writer'**: Writes sections of the research paper based on the outline and sources
- **'Editor'**: Provides editing suggestions for the written content
