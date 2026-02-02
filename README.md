# assist-me
A personal assistant who takes care of your daily burden. Built with security in mind.

## High level requirement:

We will focus on building a local web based application which has access to your data and takes requests from you and performs tasks. Feew examples of things we are aiming for this tool to do:
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


