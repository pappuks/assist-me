# assist-me
A personal assistant who takes care of your daily burden. Built with security in mind.

## High level requirement:

We will focus on building a local web based application which has access to your data and takes requests from you and performs tasks. Few examples of things we are aiming for this tool to do:
- Create calendar entries by looking at emails, messages and notes
- Create a weekly/daily to-do list 
- Prepare a menu for the week
- Handle kids study/school stuff
- Travel planning

Tools which we want access to:
- GMail (read access)
- Calender (read/write)
- iMessage (read)
- Mac Notes (read)
- Whatsapp (read)
- Slack (read)
- Amazon Shopping (read)

## High Level Architecture

We will use the below the tools and architecture:

- UI -> Open WebUI (local)
- Web access -> ngrok (allows web access)
- Tools -> MCP Server with access to all above tools
- Ollama -> Local LLM model (OSS 20B)

### Security

- All data remains on your local system.
- Access from internet is using ngrok, and we will limit access to few known email id's and integrate OAuth via Google.


### System requirement

- If running local models you need a system with 24-32 GB RAM (on M series mac) or 16-32 GB RAM GPU.
- For iMessage and Notes integration you need a Mac and the MCP server on the system.

## Installation

### ngrok 
- Install ```brew install ngrok```
- Go to ngrok.com and create your free login and follow instructions

### Open WebUI
- Install using ```pip install open-webui```
- Run using ```open-webui serve```

### Ollama
- Install by going to Ollama.com and following instructions
- Download `gpt-oss-20b` model

## Build

- We now use Claude Code to build our local MCP server with all the provided tools. 