# CoupAI
Coup Game updated with GPT-powered AI decision-making

## Index
* Introduction
* Set-up
* Discussion
* Limitations 
* Future Work

##### Note: Bug discussion is handled in Limitations and Future work #####

## Introduction

This is a continuation of a two-part project with the first version being found at https://www.github.com/csingleton19/Coup

I decided to leave them separate as there were some overall design differences i.e. in the first one, I differentiated between the AIAgent and Human Player in the GameManagement.py file, but I treated them the same in this version. There are other differences too, but I also wanted people to have access to a version that could be run without internet and only Python installed, and one that needs access to the internet + specific imports

## Set-up

The set-up is pretty straight-forward since I ended up using mostly native Python in VSCode, the only package needed to install is OpenAI. This was done using Python 3.10.11 and OpenAI 1.3.8


### Native Python

This is how I set it up on my laptop, but for everything else I tend to use a miniconda environment 

1. Download and install Python 3.10.11 -> https://www.python.org/downloads/
2. Download the files that are in this repo, and be sure to keep them in the same parent folder!
3. Open up a terminal for an Ubuntu/Mac machine, or Powershell for a Windows machine
4. Navigate into the directory that you downloaded in Step 2 from the terminal (i.e. for me the command is cd /Documents/Coup where Coup is the parent folder I mentioned earlier - but that will probably be different for you)
5. pip install openai==1.3.8
6. Set up the OpenAI API
   * make an OpenAI account
   * select the API plan you prefer - I use the pay-as-you-go and prepay a specific amount, but to each their own
   * generate the API key
   * create a .env text file within the parent folder, and enter the following:
   * OPENAI_API_KEY=XX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   * #### WARNING: IF YOU PUT THIS ON GITHUB, MAKE SURE GIT IGNORES THE .ENV FILE - PROTECT YOUR API KEY ####
8. Type python interface.py in the terminal
9. Press enter
10. Enjoy, and may the odds be ever in your favor!

### (Mini)conda

Anaconda and the far superior (in my opinion) Miniconda are alternative ways to also set up an environment where the code from this will be independent from other environments you may need. This is important because some Python programs could use 3.7, and others could use 3.12, and the different versions can break if downloaded together and mishandled. The main differences are what comes with each. Anaconda comes with a lot of stuff, so it tends to be rather bloated, but Miniconda is a lightweight version that allows you to pick only what you want to install

Anaconda download link - https://www.anaconda.com/products/individual

Miniconda download link - https://docs.conda.io/en/latest/miniconda.html

1. Install Anaconda or Miniconda using the link(s) above
2. conda create -n myenv python=3.10.11 - enter this command in terminal/Powershell this creates a specific environment called myenv (which is swappable) that has Python 3.10.11 set up. You can install multiple environments side by side that don't interfere with each other
3. conda activate myenv - (or if you changed the name be sure to swap myenv for the new name), but this is also a terminal/Powershell command
4. Start at Step 2 from the Native Python section right above

### Pyenv

Pyenv is an alternative to conda that is also really popular

Pyenv download link - https://github.com/pyenv/pyenv#installation

1. Install Pyenv using the link above
2. pyenv install 3.10.11 - terminal/Powershell command to set up the python environment
3. pyenv local 3.10.11 - terminal/Powershell command
4. Start at Step 2 from the Native Python section above

#### Conda vs Pyenv

Conda takes up more space than Pyenv because Conda is a package and environment manager, whereas Pyenv is just an environment manager and doesn't handle dependencies 

## Discussion

Overall this was a really interesting project since I've been using various LLMs as decision-making engines for various projects, but never applied it to a game before. It was fun crafting the prompts and watching the AI agents play each other. Integrating the AIAgent took some reformatting of the V1 code I created, but treating the human players and AI Opponents as the same in the GameManagement file was the right choice. I would have loved to use a GPT4 model for the AIAgent, but I haven't been granted access to it yet - I used Davinci since that was what GPT4 suggested I use, however I think this was not ideal as it seems to not be as good at critical thinking as GPT4 or GPT3.5. I did some research and it seems some others agree (https://news.ycombinator.com/item?id=35110998), but it was a good experience figuring out the strengths and weaknesses of the different models firsthand!

I decided to let random logic be the fallback if there are any errors with the API, and I decided to make it so that the AIAgent makes decisions and there is a CommunicationLayer that, while it uses the same "brain" as the AIAgent, would separate the communication. I wanted to AI to have access to as much of the gamestate as possible, but when I fed it the entire log it would max out the token length if the game went on for a while, so I decided to instead feed it only the last X actions. I did keep the entire log, and when the game ends the player can examine all actions taken if they want. I also decided to leave in the debugging statements so that anyone who looks at this can understand what is happening under the hood as it happens, and adjust the logic as they wish (i.e. if an invalid action is chosen, they may prefer to have the turn end vs. given the turn player another chance).

I broke up the logic into GameState, GameManagement, Player, Character, AIAgent, and Communication Layers - with a CLI interface that they interact through. This seemed to be the easiest way to separate all concerns without going overboard - some people subscribe to one class/function per file, but I think that is insane. I thought that was a good balance of "modular enough" without going the Java approach. I wanted a GameState that was constantly updated and could be fed to the AI so they could make informed decisions. The Player and Character classes encapsulated all of the action logic available within the original game, but doesn't include any of the expansions. I built out the AIAgent logic first to make sure that it was working as intended with a CommunicationLayer skeleton, then integrated the CommunicationLayer into the entire pipeline last. 

I tried to make it as close to a real product as I would have if I had more time, but not quite there - overall I'm happy with it! Even with what I will cover in the Limitations and have previously mentioned, I think it does a good job of showcasing my design process/coding skills

## Limitations

* As I previously mentioned, I think the DaVinci model isn't all that great (or even good) when it comes to this kind of stuff. I think it would be good at text extraction, but it is a little wacky
* I'm currently out of the country and had my laptop crash before it backed up all of the code. Because of not being in home terriroty, I didn't have access to my other laptops that are already set up with Python ready to go, and the laptop that I did have access to is a lot different - I usually use Linux, which miniconda is pretty easy to set-up and there are no automatic updates, but on this Windows laptop I'm currently on it was exceedingly difficult to set up (I ended up just moving on and setting up Python globally vs in an environment - which I wanted to not do since it isn't mine) - and was also hit with an automatic update mid-setup. Luckily I had some of the code backed up to my google drive, but not all of the changes that I had made from V1 to V1 (or Coup to CoupAI if you go by repo name) made it, so I had to rebuild those systems instead of fixing the bugs I mention in Future Work

## Future Work

* I would like to replace the davinci model, but that would require a little retooling since the way I set up the query_gpt isn't directly compatible with the models I would like to use but don't have access to. I think using a better model would enable way better decision making about gamestate, future actions, and handle the communication better. The current model is a little goofy, but kind of cute when it comes to messages
* Fix the bug where it prints AI Agent cards in the beginning. It is fine when it is AI vs AI, but the human player would have an advantage over it going into a game against them
* Use asynchronous processing i.e. Gameplay and Messaging could be handled differently - ideally it would be cool to build a UI that shows each player their cards, and has a split screen with a visual of the board/deck + a terminal display that shows the logs + messages
* Work on the repeated action / invalid action logic - the AI sometimes chooses invalid actions (and repeatedly) so if I had more time I would knock this out first (or second, maybe replacing the model would be better). Either way, those two would be the first things I tackle
