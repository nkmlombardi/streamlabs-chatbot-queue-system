#---------------------------------------
#	Import Libraries
#---------------------------------------
import clr
import sys
import json
import os
import random
import ctypes
import codecs
import time
import codecs
import io


#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "Advanced Queue System"
Website = "https://github.com/nkmlombardi"
Description = "An improved queue system for viewer gameplay."
Creator = "Raker"
Version = "0.0.1"

#---------------------------------------
#	Set Variables
#---------------------------------------
configFile = "QueueConfig.json"
settings = {}
user = ""
responses = []
queue = []
playing = []
active = False
iteration = 0


#---------------------------------------
#	Set Variables
#---------------------------------------
defaultSettings = {
    "commands": {
        "start": "!start",
        "end": "!end",
        "pause": "!pause",
        "save": "!save",
        "load": "!load",
        "clear": "!clear",
        "join": "!join",
        "list": "!list",
        "wager": "!wager",
        "add": "!add",
        "remove": "!remove",
        "accept": "!accept"
    },

    "title": "Subscriber Sundays",
    "host": "Twitch RakerTV",
    "permission": "Everyone",

    "useCooldown": True,
    "cooldown": 0,
    "onCooldown": "$user, the command is still on cooldown for $cd seconds!",
    "userCooldown": 0,
    "onUserCooldown": "$user the command is still on user cooldown for $cd seconds!",

    "responseQueueModStarted": "/me @$moderator has started the $title queue!",
    "responseQueueModEnded": "/me @$moderator has ended the $title queue!",
    "responseQueueModCleared": "/me @$moderator has cleared the $title queue!",

    "responseQueueModAdded": "/me @$player was added to the queue by @$moderator",
    "responseQueueModRemove": "/me @$player was removed from the queue by @$moderator",
    "responseQueueModAccept": "/me @$player was accepted to play by @$moderator",
    "whisperQueueModAccept": "/w $player It is your turn to play! Please make sure you have sent a friend request in-game to $host.",
    "responseLoadFailed": "/me $user failed to load specified $file.",
    "responseLoadSuccess": "/me $user successfully loaded $file",
    "responseLoadArgMissing": "/me $user Please provide a name for queue to be loaded.",
    "responseSaveFailed": "/me $user failed to save specified $file",
    "responseSaveSuccess": "/me $user successfully saved $file",
    "responseSaveArgMissing": "/me $user Please provide a name for the saved queue.",

    "responseWagerChanged": "/me @$user has changed their wager to $wagered $currency and moved to position #$index in the queue",
    "responseQueueEmpty": "/me @$user The queue is currently empty.",
    "responseQueueUserAdded": "/me $user has been added to the queue in position #$index for $wagered points",
    "responseQueueUserDuplicate": "/me @$user You are already in the queue. To wager more points use !wager",
    "responseNotEnoughPoints": "/me $user does not have enough $currency to be added to the queue",
    "responseArgHandleMissing": "/me @$user Please provide your in-game name when typing the !join command. Ex: !join RakerTV <points>",
    "responseArgPointsMissing": "/me @$user Please include how many $currency you would like to wager to join. Ex: !join <in-game-name> 120",
    "responseArgPointsInvalid": "/me @$user Please enter a number for the amount of $currency you would like to wager to join. Ex: !join <in-game-name> 120"
}


#---------------------------------------
#	Custom Functions
#---------------------------------------
def find_index(dicts, key, value):
    class Null: pass
    for i, d in enumerate(dicts):
        if d.get(key, Null) == value:
            return i
    else:
        return False

def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
                  (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


#---------------------------------------
#	Chatbot Function
#---------------------------------------

def ScriptToggled(state):
    return


#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
    global responses, settings, configFile, emotes

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            importedSettings = json.load(file, encoding='utf-8-sig')
    except:
        settings = defaultSettings

    settings = merge_two_dicts(defaultSettings, importedSettings)

    try:
        for i in responses:
            int(i)
    except:
        MessageBox = ctypes.windll.user32.MessageBoxW
        MessageBox(0, u"Invalid values", u"Queue Script failed to load.", 0)
    return


#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    global settings, user, ScriptName, queue, playing, active

    if data.IsChatMessage():
        # PERMISSION: Moderator
        if Parent.HasPermission(data.User, "Moderator", ""):
            tempResponseString = ""
            user = data.User

            # COMMAND: START
            if data.GetParam(0).lower() == settings["commands"]["start"]:
                active = True
                tempResponseString = settings["responseQueueModStarted"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$title", settings['title'])
                Parent.SendTwitchMessage(tempResponseString)

            # COMMAND: PAUSE
            elif active and data.GetParam(0).lower() == settings["commands"]["pause"]:
                active = False
                tempResponseString = settings["responseQueueModEnded"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$title", settings['title'])
                Parent.SendTwitchMessage(tempResponseString)

            # COMMAND: END
            elif data.GetParam(0).lower() == settings["commands"]["end"]:
                active = False

                queue = []
                playing = []

                tempResponseString = settings["responseQueueModEnded"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$title", settings['title'])
                Parent.SendTwitchMessage(tempResponseString)


            # COMMAND: CLEAR
            elif data.GetParam(0).lower() == settings["commands"]["clear"]:
                if data.GetParam(1).lower() == 'queue':
                    queue = []

                elif data.GetParam(1).lower() == 'playing':
                    playing = []

                else:
                    queue = []
                    playing = []

                tempResponseString = settings["responseQueueModCleared"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$title", settings['title'])
                Parent.SendTwitchMessage(tempResponseString)


            # COMMAND: SAVE
            elif data.GetParam(0).lower() == settings["commands"]["save"]:
                path = os.path.dirname(__file__)

                if not data.GetParam(1):
                    tempResponseString = settings["responseSaveArgMissing"]

                else:
                    try:
                        with io.open(os.path.join(os.path.dirname(__file__), data.GetParam(1) + ".json"), 'w', encoding='utf-8') as f:
                            f.write(json.dumps({ 'queue': queue, 'playing': playing }, ensure_ascii=False))

                    except:
                        tempResponseString = settings["responseSaveFailed"]

                    else:
                        tempResponseString = settings["responseSaveSuccess"]

                tempResponseString = tempResponseString.replace("$user", user)
                tempResponseString = tempResponseString.replace("$file", data.GetParam(1))
                Parent.SendTwitchMessage(tempResponseString)


            # COMMAND: LOAD
            elif data.GetParam(0).lower() == settings["commands"]["load"]:
                active = False
                path = os.path.dirname(__file__)

                if not data.GetParam(1):
                    tempResponseString = settings["responseLoadArgMissing"]

                try:
                    with codecs.open(os.path.join(path, data.GetParam(1) + '.json'), encoding='utf-8-sig', mode='r') as file:
                        importedData = json.load(file, encoding='utf-8-sig')
                        tempResponseString = settings["responseLoadSuccess"]

                except:
                    tempResponseString = settings["responseLoadFailed"]

                else:
                    queue = importedData["queue"]
                    playing = importedData["playing"]

                tempResponseString = tempResponseString.replace("$user", user)
                tempResponseString = tempResponseString.replace("$file", data.GetParam(1))
                Parent.SendTwitchMessage(tempResponseString)



            # COMMAND: ADD
            elif data.GetParam(0).lower() == settings["commands"]["add"]:
                if data.GetParam(1) == 'queue':
                    queue.append({ 'user': data.GetParam(2).lower(), 'wagered': int(data.GetParam(4)), 'ign': str(data.GetParam(3)), 'time': time.time() })

                elif data.GetParam(1) == 'playing':
                    queue.append({ 'user': data.GetParam(2).lower(), 'wagered': int(data.GetParam(4)), 'ign': str(data.GetParam(3)), 'time': time.time() })

                tempResponseString = settings["responseQueueModAdded"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$player", data.GetParam(2).lower())
                Parent.SendTwitchMessage(tempResponseString)

            # COMMAND: REMOVE
            elif data.GetParam(0).lower() == settings["commands"]["remove"]:

                if data.GetParam(1) == 'queue':
                    index = find_index(queue, 'user', data.GetParam(2).lower())
                    del queue[index]

                elif data.GetParam(1) == 'playing':
                    index = find_index(playing, 'user', data.GetParam(2).lower())
                    del queue[index]

                tempResponseString = settings["responseQueueModRemove"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$player", data.GetParam(2).lower())
                Parent.SendTwitchMessage(tempResponseString)

            # COMMAND: ACCEPT
            elif data.GetParam(0).lower() == settings["commands"]["accept"]:
                index = find_index(queue, 'user', data.GetParam(1).lower())

                # Remove points from player
                Parent.RemovePoints(queue[index]["user"], queue[index]["wagered"])

                # Remove from queue and add to playing
                playing.append(queue[index])
                del queue[index]

                tempWhisperString = settings["whisperQueueModAccept"]
                tempWhisperString = tempWhisperString.replace("$host", settings["host"])
                tempWhisperString = tempWhisperString.replace("$player", data.GetParam(1).lower())
                Parent.SendTwitchMessage(tempWhisperString)

                tempResponseString = settings["responseQueueModAccept"]
                tempResponseString = tempResponseString.replace("$moderator", user)
                tempResponseString = tempResponseString.replace("$player", data.GetParam(1).lower())
                Parent.SendTwitchMessage(tempResponseString)


        # PERMISSION: Everyone
        if Parent.HasPermission(data.User, settings["permission"], "") and active:
            tempResponseString = ""
            user = data.User
            cd = ""
            index = 0
            wagered = 0


            # COMMAND: LIST
            if data.GetParam(0).lower() == settings["commands"]["list"]:
                if len(queue) > 0:
                    tempResponseString += "\n/me Waiting Queue:\n"
                    for index, entry in enumerate(queue):
                        tempResponseString += "/me {i}. {p} [{g}] [{w}]\n".format(i=index+1, p=entry["user"], w=entry["wagered"], g=entry["ign"])

                elif len(playing) > 0:
                    tempResponseString += "/me Currently Playing:\n"
                    for index, entry in enumerate(playing):
                        tempResponseString += "/me {i}. {p} [{g}] [{w}]\n".format(i=index+1, p=entry["user"], w=entry["wagered"], g=entry["ign"])

                else:
                    tempResponseString = settings["responseQueueEmpty"]

                tempResponseString = tempResponseString.replace("$user", user)
                Parent.SendTwitchMessage(tempResponseString)


            # COMMAND: WAGER
            elif data.GetParam(0).lower() == settings["commands"]["wager"]:

                if len(queue) == 0:
                    tempResponseString = settings["responseQueueEmpty"]

                # Check if points argument is valid
                elif data.GetParam(1).isdigit() is False:
                    tempResponseString = settings["responseArgPointsInvalid"]

                else:
                    index = find_index(queue, 'user', user)
                    wagered = int(data.GetParam(1))
                    delta = int(data.GetParam(1)) - queue[index]["wagered"]

                    if int(data.GetParam(1)) > (Parent.GetPoints(data.User) + queue[index]["wagered"]):
                        tempResponseString = settings["responseNotEnoughPoints"]

                    else:
                        # if (delta > 0):
                        #     Parent.RemovePoints(user, delta)
                        # elif (delta < 0):
                        #     Parent.AddPoints(user, delta)

                        queue[index]["wagered"] = wagered

                        queue.sort(key=lambda x: x['wagered'], reverse=True)
                        index = find_index(queue, 'user', user)

                        tempResponseString = settings["responseWagerChanged"]
                        tempResponseString = tempResponseString.replace("$user", user)
                        tempResponseString = tempResponseString.replace("$currency", Parent.GetCurrencyName())
                        tempResponseString = tempResponseString.replace("$wagered", str(wagered))
                        tempResponseString = tempResponseString.replace("$index", str(index + 1))
                        Parent.SendTwitchMessage(tempResponseString)


            # COMMAND: JOIN
            elif data.GetParam(0).lower() == settings["commands"]["join"]:
                paramCommand = data.GetParam(0)
                paramName = data.GetParam(1)
                paramPoints = data.GetParam(2)

                if (paramName and paramName[0] == "\""):
                    paramName = (paramName + " " + paramPoints).replace("\"", "")
                    paramPoints = data.GetParam(3)

                if (paramPoints and (paramPoints.isdigit() is False)):
                    paramName = (paramName + " " + paramPoints).replace("\"", "")
                    paramPoints = data.GetParam(3)

                # Check if in game name argument exists
                if not paramName:
                    tempResponseString = settings["responseArgHandleMissing"]

                # Check if points argument exists
                elif not paramPoints:
                    tempResponseString = settings["responseArgPointsMissing"]

                # Check if points argument is valid
                elif paramPoints.isdigit() is False:
                    tempResponseString = settings["responseArgPointsInvalid"]

                # Check if user has points they wish to wager
                elif int(paramPoints) > Parent.GetPoints(data.User):
                    tempResponseString = settings["responseNotEnoughPoints"]

                # elif (find_index(queue, 'user', user)) is not False:
                #     tempResponseString = settings["responseQueueUserDuplicate"]

                else:
                    wagered = int(paramPoints)
                    # Parent.RemovePoints(user, wagered)

                    # Insert, Re-sort, and Find
                    queue.append({ 'user': user, 'wagered': wagered, 'ign': str(paramName), 'time': time.time() })
                    # queue.sort(key=lambda x: x['wagered'], reverse=True)
                    queue = multikeysort(queue, ['-wagered', 'time'])
                    index = find_index(queue, 'user', user)
                    tempResponseString = settings["responseQueueUserAdded"]

                tempResponseString = tempResponseString.replace("$user", user)
                tempResponseString = tempResponseString.replace("$currency", Parent.GetCurrencyName())
                tempResponseString = tempResponseString.replace("$wagered", str(wagered))
                tempResponseString = tempResponseString.replace("$index", str(index + 1))
                Parent.SendTwitchMessage(tempResponseString)
    return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    global responses, settings, configFile, emotes

    Init()

    return

def OpenReadMe():
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
    global iteration

    iteration += 1

    if iteration % 10 == 0:
        with io.open(os.path.join(os.path.dirname(__file__), "autosave.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps({ 'queue': queue, 'playing': playing }, ensure_ascii=False))

    return
