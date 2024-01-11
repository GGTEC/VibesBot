import sys
import os
import logging
import subprocess
import utils
import webview
import threading
import validators
import webbrowser
import time
import json
import requests as req
import tkinter
import textwrap
import keyboard
import random
import yt_dlp
import datetime
import re
import tkinter.messagebox as messagebox
import pygame


from datetime import datetime, timedelta
from commands import CommandDatabaseManager
from events import EventLogManager
from users import UserDatabaseManager
from dateutil.parser import parse 
from WsClient import WebSocketClient
from sk import WebSocketServer
from lockfile import LockManager
from yt_dlp import DownloadError
from io import BytesIO
from collections import namedtuple
from auth import auth_data
from io import BytesIO
from gtts import gTTS
from tkinter import filedialog as fd
from random import randint
from discord_webhook import DiscordWebhook, DiscordEmbed


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

global caching, loaded_status, main_window, main_window_open, window_chat_open, window_chat, window_events, window_events_open, wsclient, server, conected, userdatabase, commanddatabase, eventlogdatabase

curr_version = "1.6.7"
caching = False
loaded_status = False
conected = False
main_window_open = False
window_chat_open = False
window_events_open = False
server = None
wsclient = None

lock_manager = LockManager()
lock_manager.check()

userdatabase = None
commanddatabase = None
eventlogdatabase = None

data_list = []
data_message = []


def notification(type, status, status_s, message, audio, volume, user_input):

    not_data = {
        "type": type,
        "status" : status,
        "status_s" : status_s,
        "message": message,
        "audio": audio,
        "volume": volume,
        "user_input": user_input
    }
    
    data_list.append(not_data)


def loop_notification():

    while loaded_status == True:

        try:

            playing = pygame.mixer.music.get_busy()

            if data_list != None:
                
                if len(data_list) > 0 and not playing:

                    data = data_list[0]

                    type_not = data['type']
                    status = data['status']
                    status_s = data['status_s']
                    volume = data['volume']
                    audio = data['audio']
                    message = data['message']
                    user_input = data['user_input']

                    append_notice({"type": type_not, "status" : status, "status_s" : status_s, "message": message, "user_input": user_input})
                        
                    if audio != "" and volume !=  "":

                        convert_vol = int(volume) / 100

                        while playing:
                            playing = pygame.mixer.music.get_busy()
                            time.sleep(2)

                        pygame.mixer.music.load(audio)
                        pygame.mixer.music.set_volume(convert_vol)
                        pygame.mixer.music.play()

                    if data in data_list:
                        data_list.remove(data)
                

        except Exception as e:
            utils.error_log(e)


def toast(message):

    if main_window_open:
        main_window.evaluate_js(f"toast_notifc('{message}')")


def loop_chat_slow():

    while loaded_status == True:

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        time_slow = chat_data['slow-mode-time']

        if data_message != None:

            if len(data_message) > 0:

                data = data_message[0]

                if main_window_open:

                    main_window.evaluate_js(f"append_message({json.dumps(data, ensure_ascii=False)})")

                if window_chat_open:
                    
                    window_chat.evaluate_js(f"append_message_out({json.dumps(data, ensure_ascii=False)})")

                if data in data_message:
                    data_message.remove(data)

        time.sleep(float(time_slow))


def append_message(data_receive):

    try:

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        if int(chat_data['slow-mode']) == 1:

            if float(chat_data['slow-mode-time']) > 0:

                data_message.append(data_receive)
        
        else:
                
            if main_window_open:

                main_window.evaluate_js(f"append_message({json.dumps(data_receive, ensure_ascii=False)})")

            if window_chat_open:
                
                window_chat.evaluate_js(f"append_message_out({json.dumps(data_receive, ensure_ascii=False)})")

    except Exception as e:
        utils.error_log(e)


def append_notice(data_receive):

    try:
        event_log_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","load")
        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        now = datetime.now()

        new_event = {
            "timestamp": str(now),
            "type": data_receive['type'],
            "message": data_receive['message'],
            "user_input": data_receive['user_input']
        }

        eventlogdatabase.add_event(new_event)
        event_log_data = eventlogdatabase.get_recent_events()

        data = {
            "message": data_receive["message"],
            "user_input": data_receive["user_input"],
            "font_size": event_log_config_data["slider-font-events"],
            "font_size_chat": chat_data["font-size"],
            "color_events": event_log_config_data["color-events"],
            "data_time": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "data_show": event_log_config_data["data-show-events"],
            "type_event": data_receive["type"],
            "show_commands" : event_log_config_data["show-commands"],
            "show_commands_chat" : event_log_config_data["show-commands-chat"],
            "show_music" : event_log_config_data["show-music"],
            "show_music_chat" : event_log_config_data["show-music-chat"],
            "show_follow" : event_log_config_data["show-follow"],
            "show_follow_chat" : event_log_config_data["show-follow-chat"],
            "show_likes" : event_log_config_data["show-likes"],
            "show_likes_chat" : event_log_config_data["show-likes-chat"],
            "show_gifts" : event_log_config_data["show-gifts"],
            "show_gifts_chat" : event_log_config_data["show-gifts-chat"],
            "show_chest" : event_log_config_data["show-chest"],
            "show_chest_chat" : event_log_config_data["show-chest-chat"],
            "show_share" : event_log_config_data["show-share"],
            "show_share_chat" : event_log_config_data["show-share-chat"],
            "show_join" : event_log_config_data["show-join"],
            "show_join_chat" : event_log_config_data["show-join-chat"],
            "show_events" : event_log_config_data["show-events"],
            "show_events_chat" : event_log_config_data["show-events-chat"],
            "show_goal_start" : event_log_config_data["show-goal-start"],
            "show_goal_start_chat" : event_log_config_data["show-goal-start-chat"],
            "show_goal_end" : event_log_config_data["show-goal-end"],
            "show_goal_end_chat" : event_log_config_data["show-goal-end-chat"],
            "event_list" : event_log_data,
        }

        if loaded_status:

            if data_receive["status"] == 1:

                if main_window_open:
                    main_window.evaluate_js(f"append_notice({json.dumps(data, ensure_ascii=False)})")
                
                if window_events_open:
                    window_events.evaluate_js(f"append_notice_out({json.dumps(data, ensure_ascii=False)})")

                if window_chat_open:
                    window_chat.evaluate_js(f"append_notice_chat({json.dumps(data, ensure_ascii=False)})")

            if data_receive["status_s"] == 1:

                variableMappings = {
                    "command": event_log_config_data["show-commands-html"],
                    "music" : event_log_config_data["show-music-html"],
                    "event": event_log_config_data["show-events-html"],
                    "follow": event_log_config_data["show-follow-html"],
                    "like": event_log_config_data["show-likes-html"],
                    "gift": event_log_config_data["show-gifts-html"],
                    "chest": event_log_config_data["show-chest-html"],
                    "share": event_log_config_data["show-share-html"],
                    "join": event_log_config_data["show-join-html"],
                    "goal_start": event_log_config_data["show-goal-start-html"],
                    "goal_end": event_log_config_data["show-goal-end-html"]
                }
                
                if variableMappings[data_receive["type"]]:

                    data_update = {
                        "message": data_receive["message"]
                    }

                    data_goal = {
                        "type": "event",
                        "html": utils.update_notif(data_update)
                    }

                    server.broadcast_message(json.dumps(data_goal))

    except Exception as e:
        
        if not isinstance(e, KeyError):
            utils.error_log(e)
        

def send_discord_webhook(data):
    
    """
        Send a discord webhook by a type message.

    Args:
        data (dict): A dictionary containing the type_id and other relevant data for the webhook.

    Raises:
        FileNotFoundError: If the discord.json file is not found.
        discord_webhook.DiscordWebhookException: If the webhook execution failed for any reason.
    """

    try:
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
                
        type_id = data["type_id"]

        discord_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/discord.json","load")

        webhook_status = discord_config_data[type_id]["status"]
        webhook_color = discord_config_data[type_id]["color"]
        webhook_content = discord_config_data[type_id]["content"]
        webhook_url = discord_config_data[type_id]["url"]
        webhook_title = discord_config_data[type_id]["title"]
        
        webhook_description = discord_config_data[type_id]["description"]
        webhook_profile_status = discord_config_data["profile_status"]
        webhook_profile_image = discord_config_data["profile_image"]
        webhook_profile_name = discord_config_data["profile_name"]

        if webhook_status == 1 and not webhook_url == "":
            
            webhook = DiscordWebhook(url=webhook_url)
            webhook.content = webhook_content

            embed = ""

            if type_id == "follow":
                
                username = data["follow_name"]

                aliases = {
                    "{username}": username
                }

                webhook_title = utils.replace_all(webhook_title, aliases)
                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )
 
            elif type_id == "like":
                
                username = data["username"]
                likes_send = data["likes_send"]
                total_likes = data["total_likes"]
 
                aliases = {
                    "{username}": username,
                    "{likes}" :likes_send,
                    "{total}" :total_likes
                }

                webhook_title = utils.replace_all(webhook_title, aliases)
                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )
            
            elif type_id == "gifts":

                username = data["username"]
                gifts_send = data["gifts_send"]
                gift_name = data["gift_name"]
                diamonds = data["diamonds"]
 
                aliases = {
                    "{username}": username,
                    "{amount}" :gifts_send,
                    "{gift}" :gift_name,
                    "{diamonds}" :diamonds
                }

                webhook_title = utils.replace_all(webhook_title, aliases)
                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )
             
            elif type_id == "share":

                username = data["username"]
 
                aliases = {
                    "{username}": username,
                }

                webhook_title = utils.replace_all(webhook_title, aliases)
                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )

            elif type_id == "envelope":

                username = data["username"]
 
                aliases = {
                    "{username}": username,
                }

                webhook_title = utils.replace_all(webhook_title, aliases)
                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )

            elif type_id == "subscriber":

                username = data["username"]
 
                aliases = {
                    "{username}": username,
                }

                webhook_title = utils.replace_all(webhook_title, aliases)
                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )
                                                      
            elif type_id == "live_start":
                
                aliases = {
                    "{url}": f"https://tiktok.com/@{authdata.USERNAME()}/live"
                }

                webhook_description = utils.replace_all(webhook_description, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )

            elif type_id == "goal_start":
                aliases = {
                    "{target}": str(data["target"]),
                    "{current}": str(data["current"]),
                    "{description}": str(data["description"]),
                    "{type}": data["goal_type"],
                }

                webhook_description = utils.replace_all(webhook_description, aliases)
                webhook_title = utils.replace_all(webhook_title, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )

            elif type_id == "goal_end":
                
                aliases = {
                    "{target}": str(data["target"]),
                    "{current}": str(data["current"]),
                    "{type}": data["goal_type"],
                }

                webhook_description = utils.replace_all(webhook_description, aliases)
                webhook_title = utils.replace_all(webhook_title, aliases)

                embed = DiscordEmbed(
                    title=webhook_title,
                    description=webhook_description,
                    color=webhook_color,
                )

            if webhook_profile_status == 1 and webhook_profile_image.endswith(".png"):
                

                embed.set_author(
                    name=webhook_profile_name,
                    url=f"https://www.tiktok.com/@{authdata.USERNAME()}",
                    icon_url=webhook_profile_image,
                )

            if embed != "":
                webhook.add_embed(embed)
                webhook.execute()

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)


def send_discord_webhook_auth(message,username):
        
    try:

        WEBHOOKURL = os.getenv('WEBHOOKURL')

        webhook_login = DiscordWebhook(url=WEBHOOKURL)

        embed_login = DiscordEmbed(
            title= f'{message}',
            description= F'https://www.tiktok.com/@{username}' ,
            color= '03b2f8'
        )

        embed_login.set_author(name=username, url=f'https://www.tiktok.com/@{username}')
        
        webhook_login.add_embed(embed_login)
        webhook_login.execute() 

    except Exception as e:
        utils.error_log(e)
        

def event_log(data_save):
    
    data_save = json.loads(data_save)
    type_id = data_save['type_id']
    
    if type_id == "get":
        
        
        event_log_data = eventlogdatabase.get_recent_events()
        event_log_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","load")

        if event_log_data is not None:

            data = {
                "slider-font-events" : event_log_config_data["slider-font-events"],
                "font-events-overlay" : event_log_config_data["font-events-overlay"],
                "color-events" : event_log_config_data["color-events"],
                "background_color" : event_log_config_data["background-color"],
                "text_color" : event_log_config_data["text-color"],
                "event-delay" : event_log_config_data["event-delay"],
                "data-show-events" : event_log_config_data["data-show-events"], 
                "show-commands" : event_log_config_data["show-commands"],
                "show-music" : event_log_config_data["show-music"],
                "show-follow" : event_log_config_data["show-follow"],
                "show-likes" : event_log_config_data["show-likes"],
                "show-gifts" : event_log_config_data["show-gifts"],
                "show-chest" : event_log_config_data["show-chest"],
                "show-share" : event_log_config_data["show-share"],
                "show-join" : event_log_config_data["show-join"],
                "show-events" : event_log_config_data["show-events"],
                "show-goal-start" : event_log_config_data["show-goal-start"],
                "show-goal-end" : event_log_config_data["show-goal-end"],
                "event-list" : event_log_data,
            }
            
            return  json.dumps(data, ensure_ascii=False)

    elif type_id == "save":
        
        try:
            
            event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","load")

            event_log_data["slider-font-events"] = data_save["slider-font-events"]
            event_log_data["font-events-overlay"] = data_save["font-events-overlay"]
            event_log_data["color-events"] = data_save["color-events"]
            event_log_data["data-show-events"] = data_save["data-show-events"] 
            event_log_data["background-color"] = data_save["background-color"]
            event_log_data["text-color"] = data_save["text-color"]
            event_log_data["event-delay"] = data_save["event-delay"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","save",event_log_data)
            
            toast("Salvo")

        except Exception as e:
            
            utils.error_log(e)
            toast("error")

    elif type_id == "get_state":
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","load")

        event_type =  data_save['type']

        data = {
            "show-event" : event_log_data[f"show-{event_type}"],
            "show-event-html" : event_log_data[f"show-{event_type}-html"],
            "show-event-chat" : event_log_data[f"show-{event_type}-chat"],
            "show-event-alert" : event_log_data[f"show-{event_type}-alert"]
        }

        return  json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save_state":
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","load")

        try:
            event_type = data_save['type']

            event_log_data[f"show-{event_type}"] = data_save["show-event"]
            event_log_data[f"show-{event_type}-html"] = data_save["show-event-html"]
            event_log_data[f"show-{event_type}-chat"] = data_save["show-event-chat"]
            event_log_data[f"show-{event_type}-alert"] = data_save["show-event-alert"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","save",event_log_data)

            toast("Salvo")
            
        except Exception as e:
            
            utils.error_log(e)
            toast("error")


def select_file_py(type_id):
    
    if type_id == "sound":
        filetypes = (("audio files", "*.mp3"), ("All files", "*.*"))

    elif type_id == "video":
        filetypes = (
            ("video files", "*.mp4"),
            ("gif files", "*.gif"),
            ("All files", "*.*"),
        )

    elif type_id == "image":
        filetypes = (("png files", "*.png"), ("gif files", "*.gif"))

    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)

    folder = fd.askopenfilename(
        initialdir=f"{utils.local_work('appdata_path')}",
        filetypes=filetypes,
    )

    root.destroy()

    return folder


def commands_py(data_receive):
    
    data = json.loads(data_receive)

    type_rec = data["type_id"]

    if type_rec == "create":

        if commanddatabase.create_command(data):

            toast("success")
            
        else:
            
            toast("error")

    elif type_rec == "edit":

        if commanddatabase.edit_command(data):

            toast("success")
            
        else:
            
            toast("error")
            


    elif type_rec == "delete":
        
        if commanddatabase.delete_command(data["command"]):

            toast("success")
            
        else:
            
            toast("error")

    elif type_rec == "get_info":

        response = commanddatabase.get_command_info(data["command"])

        if response:

            return response

        else:
            
            toast("error")


    elif type_rec == "get_list":

        
        response = commanddatabase.get_command_list()

        return response


    elif type_rec == "command-list":

        try:

            commands = commanddatabase.get_all_command_data()

            command_data_queue = utils.manipulate_json(
                f"{utils.local_work('appdata_path')}/queue/commands.json",
                "load",
                None,
            )

            command_data_giveaway = utils.manipulate_json(
                f"{utils.local_work('appdata_path')}/giveaway/commands.json",
                "load",
                None,
            )

            command_data_player = utils.manipulate_json(
                f"{utils.local_work('appdata_path')}/player/config/commands.json",
                "load",
                None,
            )

            command_data_tts = utils.manipulate_json(
                f"{utils.local_work('appdata_path')}/config/tts.json",
                "load",
                None,
            )

            command_data_balance = utils.manipulate_json(
                f"{utils.local_work('appdata_path')}/balance/commands.json",
                "load",
                None,
            )

            data = {
                "commands": [commands],
                "commands_queue": [command_data_queue],
                "commands_giveaway": [command_data_giveaway],
                "commands_player": [command_data_player],
                "commands_tts": [command_data_tts],
                "commands_balance": [command_data_balance],
            }
            
            return json.dumps(data, ensure_ascii=False)
            
        except Exception as e:
            utils.error_log(e)


def tts_command(data_receive):
    
    data = json.loads(data_receive)

    type_id = data["type_id"]

    tts_json_path = (f"{utils.local_work('appdata_path')}/config/tts.json")

    if type_id == "get":
        
        tts_command_data = utils.manipulate_json(tts_json_path, "load")
        
        if tts_command_data is not None:
            
            data = {
                "command": tts_command_data["command"],
                "status": tts_command_data["status"],
                "prefix": tts_command_data["prefix"],
                "delay": tts_command_data["delay"],
                "user_level" : tts_command_data["user_level"],
                "cost" : tts_command_data["cost"],
                "cost_status" : tts_command_data["cost_status"]
            }

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

    elif type_id == "save":
        
        try:

            tts_command_data = utils.manipulate_json(tts_json_path, "load")

            if tts_command_data is not None:
                
                tts_command_data["command"] = data["command"]
                tts_command_data["status"] = data["status"]
                tts_command_data["prefix"] = data["prefix"]
                tts_command_data["delay"] = data["delay"]
                tts_command_data["user_level"] = data["user_level"]
                tts_command_data["cost"] = data["cost"]
                tts_command_data["cost_status"] = data["cost_status"]

                utils.manipulate_json(tts_json_path, "save", tts_command_data)

            toast('Salvo')
        except Exception as e:
            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)


def camp_command(data_receive):
    
    data = json.loads(data_receive)

    def update_match_state(champ_data_running, match):


        match_key = f"match_{match['match']}"

        champ_data_running[match_key] = match

        if len(champ_data_running) > 1:

            last_match_key = f"match_{len(champ_data_running)}"
            last_match = champ_data_running[last_match_key]

            winner_of_first_match = champ_data_running["match_1"]['winner']

            #Adicionando o perdedor da primeira partida como desafiante da ultima partida
            if len(last_match['participants']) == 1:

                participants_of_first_match = set(champ_data_running["match_1"]['participants'])
                loser_of_first_match = (participants_of_first_match - {winner_of_first_match}).pop()

                last_match['participants'].append(loser_of_first_match)
                
                winner_of_second_match = champ_data_running["match_2"]['winner']
            
            #Verificando se a terceira partida terminou e definindo o terceiro colocado
            if len(champ_data_running) == 3:


                winner_of_second_match = champ_data_running["match_2"]['winner']
                
                participants_of_first_match = set(champ_data_running["match_1"]['participants'])
                loser_of_first_match = (participants_of_first_match - {winner_of_first_match}).pop()

                participants_of_second_match = set(champ_data_running["match_2"]['participants'])
                loser_of_second_match = (participants_of_second_match - {winner_of_second_match}).pop()
                
                participants_of_third_match = set(champ_data_running["match_3"]['participants'])

                if loser_of_second_match in participants_of_third_match and loser_of_first_match in participants_of_third_match:

                    winner_of_third_match = champ_data_running["match_3"]['winner']

                    if not winner_of_third_match == None:

                        champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                        endcamp_list = champ_data_part['end_camp']

                        endcamp_list['third'] = winner_of_third_match
        
                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data_part)
                
                else:

                    winner = match['winner']

                    champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                    if winner not in champ_data['winners']:

                        champ_data['winners'].append(winner)

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data)
                        
                        aliases = {"{winner}": str(winner)}

                        message_data = utils.messages_file_load("response_add_winner")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")
                
            else:

                winner = match['winner']

                champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                if winner not in champ_data['winners']:

                    champ_data['winners'].append(winner)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data)

                    aliases = {"{winner}": str(winner)}

                    message_data = utils.messages_file_load("response_add_winner")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("event", message_data["status"], message_data["status_s"], message, "", "", "")


            #Criando a terceira partida para definir o terceiro colocado
            if len(champ_data_running) == 2:

                champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                participants_of_first_match = set(champ_data_running["match_1"]['participants'])
                participants_of_second_match = set(champ_data_running["match_2"]['participants'])

                winner_of_first_match = champ_data_running["match_1"]['winner']
                loser_of_first_match = (participants_of_first_match - {winner_of_first_match}).pop()

                if loser_of_first_match not in participants_of_second_match:

                    if len(participants_of_first_match) and len(participants_of_second_match) == 2:

                        winner_of_first_match = champ_data_running["match_1"]['winner']
                        winner_of_second_match = champ_data_running["match_2"]['winner']

                        if not winner_of_first_match == None and not winner_of_second_match == None:

                            loser_of_first_match = (participants_of_first_match - {winner_of_first_match}).pop()
                            loser_of_second_match = (participants_of_second_match - {winner_of_second_match}).pop()

                            champ_data_running["match_3"] = {
                                "match": 3,
                                "winner": None,
                                "participants": [
                                    loser_of_second_match,
                                    loser_of_first_match
                                ],
                                "match_status": False
                            }
                
                else:

                    winner_of_second_match = champ_data_running["match_2"]['winner']

                    if not winner_of_second_match == None:

                        loser_of_second_match = (participants_of_second_match - {winner_of_second_match}).pop()

                        champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                        endcamp_list = champ_data_part['end_camp'][0]

                        endcamp_list['third'] = loser_of_second_match
        
                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data_part)

            return champ_data_running
        
        else:

            winner_of_first_match = champ_data_running["match_1"]['winner']

            if not winner_of_first_match == None:

                participants_of_first_match = set(champ_data_running["match_1"]['participants'])
                loser_of_first_match = (participants_of_first_match - {winner_of_first_match}).pop()

                champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                endcamp_list = champ_data_part['end_camp'][0]

                endcamp_list['winner'] = winner_of_first_match
                endcamp_list['second'] = loser_of_first_match

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data_part)
            
            return champ_data_running

    def get_match_state():
            
        champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")
        champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "load")

        champ_list = champ_data_part['new_champ']

        if not champ_data:

            if len(champ_list) > 0:

                matches = {}
                match_number = 0
                random.shuffle(champ_list)

                for i in range(0, len(champ_list), 2):

                    match_number += 1
                    participants = champ_list[i:i + 2]
                    
                    match_key = f"match_{match_number}"
                    
                    matches[match_key] = {
                        "match": match_number,
                        "winner": None,
                        "participants": participants,
                        "match_status": False
                    }

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "save", matches)

                return matches
            
            else:
                return False

        else:

            return champ_data
        
    if not isinstance(data, list):

        type_id = data["type_id"]

        champ_json_path = (f"{utils.local_work('appdata_path')}/champ/commands.json")

        if type_id == "get":

            champ_command_data = utils.manipulate_json(champ_json_path, "load")
            
            data = {
                "command": champ_command_data["command"],
                "status": champ_command_data["status"],
                "delay": champ_command_data["delay"],
                "user_level" : champ_command_data["user_level"],
                "cost" : champ_command_data["cost"],
                "cost_status" : champ_command_data["cost_status"]
            }

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

        if type_id == "get_command":

            command = data["command_select"]

            champ_command_data = utils.manipulate_json(champ_json_path, "load")
            
            data = {
                "command": champ_command_data[command]["command"],
                "status": champ_command_data[command]["status"],
                "delay": champ_command_data[command]["delay"],
                "user_level" : champ_command_data[command]["user_level"],
                "cost" : champ_command_data[command]["cost"],
                "cost_status" : champ_command_data[command]["cost_status"]
            }

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump
        
        elif type_id == "save":
            
            try:
                champ_command_data = utils.manipulate_json(champ_json_path, "load")

                if champ_command_data is not None:
                    
                    command = data["command_select"]

                    champ_command_data[command]["command"] = data["command"]
                    champ_command_data[command]["status"] = data["status"]
                    champ_command_data[command]["delay"] = data["delay"]
                    champ_command_data[command]["user_level"] = data["user_level"]
                    champ_command_data[command]["cost"] = data["cost"]
                    champ_command_data[command]["cost_status"] = data["cost_status"]

                    utils.manipulate_json(champ_json_path, "save", champ_command_data)

                toast('Salvo')

            except Exception as e:

                toast('Ocorreu um erro ao salvar')
                utils.error_log(e)

        elif type_id == "get_matches":

            champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "load")
            
            data_dump = json.dumps(champ_data, ensure_ascii=False)

            return data_dump

        elif type_id == "get_participants":

            champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")
            
            part = champ_data['new_champ']

            data_dump = json.dumps(part, ensure_ascii=False)

            return data_dump

        elif type_id == "remove":

            user = data["data"]

            champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")
            
            part = champ_data['new_champ']

            part.remove(user)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save",champ_data)

            data_dump = json.dumps(part, ensure_ascii=False)

            return data_dump

        elif type_id == "start_matches":
            
            champ_data = get_match_state()

            if champ_data != False:

                return champ_data
            
            else:
                toast("A fila de participantes do campeonato está vazia.")

        elif type_id == "disable_match":

            status = data["status"]
            match = data["match"]

            champ_data_running =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "load")

            champ_data_running[f"match_{match}"] = {
                "match": match,
                "winner": None,
                "participants": champ_data_running[f"match_{match}"]['participants'],
                "match_status": status
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "save", champ_data_running)

        elif type_id == "winner":

            match = data['data']

            champ_data_running =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "load")
            
            champ_data_running = update_match_state(champ_data_running, match)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "save", champ_data_running)
            
            return champ_data_running
        
        elif type_id == "end_matches":

            champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")
            champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "load")

            new_champ = champ_data_part['new_champ']
            winners = champ_data_part['winners']

            new_champ.clear()
            new_champ.extend(winners)
            winners.clear()

            champ_data = {}

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data_part)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "save", champ_data)

            message_data = utils.messages_file_load("response_end_champ")

            notification("event", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

            champ_data = get_match_state()

            return champ_data

        elif type_id == "end_champ":

            champ_data_part = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")
            champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "load")

            end_camp = champ_data_part['end_camp']

            end_camp_send = end_camp.copy()

            champ_data_part['winners'] = []
            champ_data_part['new_champ'] = []
            champ_data_part['end_camp'] = {
                "winner": "",
                "second": "",
                "third": ""
            },

            champ_data = {}

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/running.json", "save", champ_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data_part)

            message_data = utils.messages_file_load("response_end_champ")

            notification("event", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

            return end_camp_send

        elif type_id == "add_user":

            user_add = data["data"]

            try:
                champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","load")
                
                user_add = f"{user_add} | {user_add}"
                
                if user_add not in champ_data['new_champ']:
                    
                    champ_data['new_champ'].append(user_add)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)


                    toast("Usuário adicionado.")

                else:

                    toast("Usuário já está na lista.")
                    
            except Exception as e:
                utils.error_log(e)
                toast("Ocorreu um erro ao adicionar o usuário.")


def balance_command(data_receive):
    
    data = json.loads(data_receive)
    type_id = data["type_id"]
    balance_json_path = (f"{utils.local_work('appdata_path')}/balance/commands.json")

    if type_id == "get":
        
        balance_command_data = utils.manipulate_json(balance_json_path, "load")
        
        if balance_command_data is not None:
            
            command_info = balance_command_data[data["command"]]

            data = {
                "command": command_info["command"],
                "status": command_info["status"],
                "delay": command_info["delay"],
                "user_level" : command_info["user_level"],
                "cost" : command_info["cost"],
                "cost_status" : command_info["cost_status"]
            }

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

    elif type_id == "save":
        
        try:
            balance_command_data = utils.manipulate_json(balance_json_path, "load")

            command_info = balance_command_data[data["command_type"]]
            
            if command_info is not None:
                
                command_info["command"] = data["command"]
                command_info["status"] = data["status"]
                command_info["delay"] = data["delay"]
                command_info["user_level"] = data["user_level"]
                command_info["cost"] = data["cost"]
                command_info["cost_status"] = data["cost_status"]

                utils.manipulate_json(balance_json_path, "save", balance_command_data)

            toast('Salvo')
        except Exception as e:
            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)


def loop_giveaway():

    giveaway_config_path = f"{utils.local_work('appdata_path')}/giveaway/config.json"
    giveaway_result_path =  f"{utils.local_work('appdata_path')}/giveaway/result.json"
    giveaway_names_path = f"{utils.local_work('appdata_path')}/giveaway/names.json"
    giveaway_backup_path = f"{utils.local_work('appdata_path')}/giveaway/backup.json"

    giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)
    result_data = utils.manipulate_json(giveaway_result_path, "load")
    giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)

    reset_give = giveaway_data["clear"]
    
    while len(result_data) == 0:
        time.sleep(1)
        result_data = utils.manipulate_json(giveaway_result_path, "load") 

    name = result_data[0]

    userinfo = userdatabase.get_user_data(name)
    
    if userinfo:

        username = userinfo['username']
        nickname = userinfo['display_name']

    else:

        username = name
        nickname = name

    aliases = {
        "{username}": username,
        "{nickname}": nickname,
    }

    
    utils.manipulate_json(giveaway_backup_path, "save", giveaway_name_data)

    if reset_give == 1:

        reset_data = []

        utils.manipulate_json(giveaway_names_path, "save", reset_data)

    message_data = utils.messages_file_load("giveaway_response_win")
    message = utils.replace_all(message_data['response'], aliases)

    notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

    toast(f"{nickname} Ganhou o sorteio!")


def giveaway_py(type_id, data_receive):

    giveaway_config_path = f"{utils.local_work('appdata_path')}/giveaway/config.json"
    giveaway_commands_path = f"{utils.local_work('appdata_path')}/giveaway/commands.json"
    giveaway_names_path = f"{utils.local_work('appdata_path')}/giveaway/names.json"
    giveaway_backup_path = f"{utils.local_work('appdata_path')}/giveaway/backup.json"
    giveaway_result_path =  f"{utils.local_work('appdata_path')}/giveaway/result.json"

    if type_id == "get_config":

        giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)

        if giveaway_data is not None:

            data = {
                "giveaway_name": giveaway_data["name"],
                "giveaway_clear": giveaway_data["clear"],
                "giveaway_enable": giveaway_data["enable"],
                "giveaway_mult": giveaway_data["allow_mult_entry"],
                "giveaway_pointer": giveaway_data["pointer"],
                "giveaway_color1": giveaway_data["color1"],
                "giveaway_color2": giveaway_data["color2"]
            }

            return json.dumps(data, ensure_ascii=False)

    elif type_id == "get_commands":

        giveaway_commands_data = utils.manipulate_json(f"{giveaway_commands_path}", "load", None)
        giveaway_commands_data = giveaway_commands_data[f"{data_receive}"]
        
        if giveaway_commands_data is not None:

            data = {
                "command": giveaway_commands_data["command"],
                "status": giveaway_commands_data["status"],
                "delay": giveaway_commands_data["delay"],
                "last_use": giveaway_commands_data["last_use"],
                "user_level": giveaway_commands_data["user_level"],
                "cost" : giveaway_commands_data["cost"],
                "cost_status" : giveaway_commands_data["cost_status"]
            }

            data_dump = json.dumps(data, ensure_ascii=False)

            return data_dump

    elif type_id == "show_names":

        giveaway_names_data = utils.manipulate_json(giveaway_names_path, "load", None)

        if giveaway_names_data is not None:
            return json.dumps(giveaway_names_data, ensure_ascii=False)
        else:
            toast("Não há nenhum nome na lista de sorteio")

    elif type_id == "save_config":

        try:

            data = json.loads(data_receive)

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)
            
            giveaway_data["name"] = data["giveaway_name"]
            giveaway_data["clear"] = data["giveaway_clear_check"]
            giveaway_data["enable"] = data["giveaway_enable"]
            giveaway_data["allow_mult_entry"] = data["giveaway_mult"]

            utils.manipulate_json(giveaway_config_path, "save", giveaway_data)

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)

            if giveaway_data["enable"] == 1 and data["giveaway_enable"] == 0:

                aliases = {
                    "{giveaway_name}": giveaway_data["name"],
                }

                message_data = utils.messages_file_load("giveaway_status_disable")
                message = utils.replace_all(message_data['reponse'], aliases)

                toast(message)

                notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

            elif giveaway_data["enable"] == 0 and data["giveaway_enable"] == 1:

                aliases = {
                    "{giveaway_name}": giveaway_data["name"],
                }

                message_data = utils.messages_file_load("giveaway_status_enable")
                message = utils.replace_all(message_data['response'], aliases)
                
                toast(message)

                notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "save_style":

        try:

            data = json.loads(data_receive)

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)
            
            giveaway_data["pointer"] = data["giveaway_pointer"]
            giveaway_data["color1"] = data["giveaway_color1"]
            giveaway_data["color2"] = data["giveaway_color2"]
            
            utils.manipulate_json(giveaway_config_path, "save", giveaway_data)

            toast("success")

            giveaway_names_path = f"{utils.local_work('appdata_path')}/giveaway/names.json"
            giveaway_names_data = utils.manipulate_json(giveaway_names_path, "load", None)

            data_giveaway = {
                'type': 'giveaway',
                'action' : 'update',
                'names': giveaway_names_data, 
                'pointer' : giveaway_data['pointer'],
                'color1' : giveaway_data['color1'],
                'color2' : giveaway_data['color2']
            }

            if server.started:
                server.broadcast_message(json.dumps(data_giveaway))
                
        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "save_commands":

        data = json.loads(data_receive)

        type_command = data["type_command"]

        try:

            giveaway_commands_data = utils.manipulate_json(f"{giveaway_commands_path}", "load", None)
            giveaway_command = giveaway_commands_data[f'{type_command}']

            giveaway_command["command"] = data["command"]
            giveaway_command["status"] = data["status"]
            giveaway_command["delay"] = data["delay"]
            giveaway_command["user_level"] = data["user_level"]
            giveaway_command["cost"] = data["cost"]
            giveaway_command["cost_status"] = data["cost_status"]

            utils.manipulate_json(f"{giveaway_commands_path}","save",giveaway_commands_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "add_user":
        
        if isinstance(data_receive, dict):

            data = data_receive

        else:

            data = json.loads(data_receive)

        new_name = data["new_name"]

        try:

            userinfo = userdatabase.get_user_data(new_name)

            if userinfo:
            
                username = userinfo['username']
                nickname = userinfo['display_name']

            else:

                username = new_name
                nickname = new_name

            def append_name(nickname):

                giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)
                giveaway_name_data.append(nickname)

                utils.manipulate_json(giveaway_names_path, "save", giveaway_name_data)

                back_giveaway_name_data = utils.manipulate_json(giveaway_backup_path, "load", None)
                back_giveaway_name_data.append(nickname)

                utils.manipulate_json(giveaway_backup_path, "save", back_giveaway_name_data)

                aliases = {
                    "{username}": username,
                    "{nickname}": nickname,
                }

                message_data = utils.messages_file_load("giveaway_response_user_add")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

                toast(message)

            giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)
            giveaway_config_data = utils.manipulate_json(giveaway_config_path, "load", None)

            if giveaway_config_data["enable"] == 1:

                giveaway_mult_config = giveaway_config_data["allow_mult_entry"]

                aliases = {
                    "{username}": username,
                    "{nickname}": nickname,
                }

                if giveaway_mult_config == 0:

                    if nickname in giveaway_name_data or username in giveaway_name_data or new_name in giveaway_name_data:

                        message_data = utils.messages_file_load("giveaway_response_mult_add")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

                        toast(message)

                    else:

                        append_name(nickname)

                else:

                    append_name(nickname)
                
            else:

                aliases = {
                    "{username}": username,
                    "{nickname}": nickname
                }

                message_data = utils.messages_file_load("giveaway_status_disabled")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "execute":
        
        try:

            utils.manipulate_json(giveaway_result_path, "save", [])

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)
            giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)

            reset_give = giveaway_data["clear"]
            
            name = random.choice(giveaway_name_data)

            userinfo = userdatabase.get_user_data(name)
            
            if userinfo:

                username = userinfo['username']
                nickname = userinfo['display_name']

            else:

                username = name
                nickname = name

            aliases = {
                "{username}": username,
                "{nickname}": nickname,
            }

            utils.manipulate_json(giveaway_backup_path, "save", giveaway_name_data)
            utils.manipulate_json(giveaway_result_path, "save", [name])

            if reset_give == 1:

                reset_data = []

                utils.manipulate_json(giveaway_names_path, "save", reset_data)


            message_data = utils.messages_file_load("giveaway_response_win")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            toast(f"{nickname} Ganhou o sorteio!")

        except Exception as e:
            
            utils.error_log(e)
            toast("Erro ao executar o sorteio")

    elif type_id == "execute_overlay":

        utils.manipulate_json(giveaway_result_path, "save", [])

        loop_giv = threading.Thread(target=loop_giveaway, args=(), daemon=True)
        loop_giv.start()
    
        data_giveaway = {
            "type": f"giveaway",
            "action": "execute",
        }

        if server.started:
            server.broadcast_message(json.dumps(data_giveaway))

    elif type_id == "update_overlay":

        giveaway_config_path = f"{utils.local_work('appdata_path')}/giveaway/config.json"
        giveaway_names_path = f"{utils.local_work('appdata_path')}/giveaway/names.json"

        giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)
        giveaway_names_data = utils.manipulate_json(giveaway_names_path, "load", None)

        data_giveaway = {
            'type': 'giveaway',
            'action' : 'update',
            'names': giveaway_names_data, 
            'pointer' : giveaway_data['pointer'],
            'color1' : giveaway_data['color1'],
            'color2' : giveaway_data['color2']
        }

        if server.started:
            server.broadcast_message(json.dumps(data_giveaway))

    elif type_id == "clear_list":

        try:
            utils.manipulate_json(giveaway_names_path, "save", [])
            toast("Lista de sorteio limpa")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def queue(type_id, data_receive):
    
    json_path =f"{utils.local_work('appdata_path')}/queue/queue.json"

    if type_id == "get":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "config" : {
                "roles_queue": queue_config_data["queue_prioriry_roles"],
                "roles_status": queue_config_data["queue_prioriry_role_status"],
                "roles_pri" : queue_config_data["queue_prioriry"],
                }
            }

        return data

    elif type_id == "queue_add":

        queue_data = utils.manipulate_json(json_path, "load")
        
        if data_receive not in queue_data['normal']:

            queue_data['normal'].append(data_receive)

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_add_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_namein_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == "queue_rem":

        queue_data = utils.manipulate_json(json_path, "load")
        
        if data_receive in queue_data['normal']:

            queue_data['normal'].remove(data_receive)

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_rem_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_noname_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == "clear_queue":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_data['normal'] = []

        utils.manipulate_json(json_path, "save", queue_data)

        aliases = {"{value}": str(data_receive)}
        message_data = utils.messages_file_load("response_clear_queue")
        message = utils.replace_all(message_data['response'], aliases)

        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        return True
    
    elif type_id == "clear_queue_pri":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_data['priority'] = []

        utils.manipulate_json(json_path, "save", queue_data)

        aliases = {"{value}": str(data_receive)}
        message_data = utils.messages_file_load("response_clear_queue_pri")
        message = utils.replace_all(message_data['response'], aliases)

        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        return True

    elif type_id == "queue_add_pri":

        queue_data = utils.manipulate_json(json_path, "load")
        
        if data_receive not in queue_data['priority']:

            queue_data['priority'].append(data_receive)

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_add_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_namein_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == "queue_rem_pri":

        queue_data = utils.manipulate_json(json_path, "load")
        
        if data_receive in queue_data['priority']:

            queue_data['priority'].remove(data_receive)

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_rem_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {"{value}": str(data_receive)}
            message_data = utils.messages_file_load("response_noname_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == "get_commands":

        try:
            command_queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "load")
            config_queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

            if data_receive == "add_queue":

                data = {
                    "command": command_queue_data[data_receive]["command"],
                    "status": command_queue_data[data_receive]["status"],
                    "spend_user" : config_queue_data['spend_user_balance'],
                    "delay": command_queue_data[data_receive]["delay"],
                    "last_use": command_queue_data[data_receive]["last_use"],
                    "user_level": command_queue_data[data_receive]["user_level"],
                    "cost" : command_queue_data[data_receive]["cost"],
                    "cost_status" : command_queue_data[data_receive]["cost_status"]
                }
            else:

                data = {
                    "command": command_queue_data[data_receive]["command"],
                    "status": command_queue_data[data_receive]["status"],
                    "delay": command_queue_data[data_receive]["delay"],
                    "last_use": command_queue_data[data_receive]["last_use"],
                    "user_level": command_queue_data[data_receive]["user_level"],
                    "cost" : command_queue_data[data_receive]["cost"],
                    "cost_status" : command_queue_data[data_receive]["cost_status"]
                }

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "save_commands":

        data_received = json.loads(data_receive)

        try:

            command_queue_data = utils.manipulate_json( f"{utils.local_work('appdata_path')}/queue/commands.json", "load")
            config_queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

            type_command = data_received["type_command"]

            command_queue_data[type_command] = {
                "command": data_received["command"],
                "status": data_received["status"],
                "delay": data_received["delay"],
                "last_use": command_queue_data[type_command]["last_use"],
                "user_level": data_received["user_level"],
                "cost" : data_received["cost"],
                "cost_status" : data_received["cost_status"]
            }

            if type_command == "add_queue":
                config_queue_data['spend_user_balance'] = data_received["status_spend"]

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "save", config_queue_data)
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json", "save", command_queue_data)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")

    elif type_id == "save_config":

        try:

            queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

            queue_config_data["queue_prioriry_roles"] = data_receive["roles_queue"]
            queue_config_data["queue_prioriry_role_status"] = data_receive["role_status"]
            queue_config_data["queue_prioriry"] = data_receive["roles_pri"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "save", queue_config_data)

            toast('Salvo')

        except Exception as e:

            toast('error')
            utils.error_log(e)


def not_config_py(data_receive, type_id, type_not):

    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_not.json", "load")

    if type_id == "get":

        file_data = event_config_data[type_not]

        data = {"not": file_data["status"], "response_chat": file_data["response_chat"]}

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save":

        try:
            data = json.loads(data_receive)

            event_config_data[type_not]["status"] = data["not"]
            event_config_data[type_not]["response_chat"] = data["response_chat"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_not.json", "save", event_config_data)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")


def messages_config(type_id, data_receive):

    json_path = f"{utils.local_work('appdata_path')}/commands/commands_config.json"
    message_data = utils.manipulate_json(json_path, "load")

    if type_id == "get":

        messages_data_get = {
            "STATUS_COMMANDS": message_data["STATUS_COMMANDS"],
            "STATUS_RESPONSE": message_data["STATUS_RESPONSE"],
            "STATUS_ERROR_TIME": message_data["STATUS_ERROR_TIME"],
            "STATUS_ERROR_USER": message_data["STATUS_ERROR_USER"],
            "STATUS_MUSIC": message_data["STATUS_MUSIC"],
            "STATUS_MUSIC_CONFIRM": message_data["STATUS_MUSIC_CONFIRM"],
            "STATUS_MUSIC_ERROR": message_data["STATUS_MUSIC_ERROR"],
        }

        return json.dumps(messages_data_get, ensure_ascii=False)

    elif type_id == "save":
        try:
            data = json.loads(data_receive)

            message_data["STATUS_COMMANDS"] = data["status_commands"]
            message_data["STATUS_RESPONSE"] = data["status_response"]
            message_data["STATUS_ERROR_TIME"] = data["status_delay"]
            message_data["STATUS_ERROR_USER"] = data["status_permission"]
            message_data["STATUS_MUSIC"] = data["status_next"]
            message_data["STATUS_MUSIC_CONFIRM"] = data["status_music"]
            message_data["STATUS_MUSIC_ERROR"] = data["status_error_music"]

            utils.manipulate_json(json_path, "save", message_data)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")


def responses_config(type_id, data):

    json_path = f"{utils.local_work('appdata_path')}/messages/messages_file.json"
    
    type_id = data['type_id']

    if type_id == "get_response":

        key = data['key']

        responses_data = utils.messages_file_load(key)

        return responses_data

    elif type_id == "save-response":

        try:
            
            key = data['key']
            response = data['response']
            status = data['status']
            status_s = data['status_s']

            responses_data = utils.manipulate_json(json_path, "load")

            responses_data[key] = {
                "status": status,
                "status_s": status_s,
                "response": response,
            }

            utils.manipulate_json(json_path, "save", responses_data)

            toast("success")

        except Exception as e:

            toast("error")
            utils.error_log(e)


def discord_config(data_discord_save, mode, type_id):

    discord_json_path = f"{utils.local_work('appdata_path')}/config/discord.json"

    if mode == "save":

        try:

            data_receive = json.loads(data_discord_save)

            discord_data = utils.manipulate_json(discord_json_path, "load")

            url_webhook = data_receive["webhook_url"]
            embed_color = data_receive["embed_color"]
            embed_content = data_receive["embed_content"]
            embed_title = data_receive["embed_title"]
            embed_description = data_receive["embed_description"]
            status = data_receive["webhook_status"]

            discord_data[type_id] = {
                "url": url_webhook,
                "status": status,
                "color": embed_color,
                "content": embed_content,
                "title": embed_title,
                "description": embed_description,
            }

            utils.manipulate_json(discord_json_path, "save", discord_data)
            toast("success")

        except Exception as e:
            toast("error")
            utils.error_log(e)

    elif mode == "get":

        discord_data = utils.manipulate_json(discord_json_path, "load")

        url_webhook = discord_data[type_id]["url"]
        embed_content = discord_data[type_id]["content"]
        embed_title = discord_data[type_id]["title"]
        embed_description = discord_data[type_id]["description"]
        embed_color = discord_data[type_id]["color"]
        status = discord_data[type_id]["status"]


        data_get = {
            "url_webhook": url_webhook,
            "embed_content": embed_content,
            "embed_color": embed_color,
            "embed_title": embed_title,
            "embed_description": embed_description,
            "status": status
        }

        return json.dumps(data_get, ensure_ascii=False)

    elif mode == "save-profile":

        discord_data = utils.manipulate_json(discord_json_path, "load")
        data_receive = json.loads(data_discord_save)

        discord_data["profile_status"] = data_receive["webhook_profile_status"]
        discord_data["profile_image"] = data_receive["webhook_profile_image_url"]
        discord_data["profile_name"] = data_receive["webhook_profile_name"]

        utils.manipulate_json(discord_json_path, "save", discord_data)

    elif mode == "get-profile":

        discord_data = utils.manipulate_json(discord_json_path, "load")

        data_get = {
            "webhook_profile_status": discord_data["profile_status"],
            "webhook_profile_image_url": discord_data["profile_image"],
            "webhook_profile_name": discord_data["profile_name"],
        }

        return json.dumps(data_get, ensure_ascii=False)


def ranks_config(data):
    
    data_receive = json.loads(data)

    type_id = data_receive["type_id"]

    config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "load")
    
    if type_id == "get":

        data = {
            "status": config_data["status"],
            "interval": config_data["interval"],
            "max_users": config_data["max_users"],
            "bg": config_data["bg"],
            "op": config_data["op"],
            "rank_type" : config_data["rank_type"],
            "rank_side" : config_data["rank_side"],
            "font_size" : config_data["font_size"],
            "font_color" : config_data["font_color"],
            "card_size" : config_data["card_size"],
            "image_size" : config_data["image_size"],
        }

        return  json.dumps(data, ensure_ascii=False)

    elif type_id == "save":

        try:

            config_data["status"] = data_receive['status']
            config_data["interval"] = data_receive['interval']
            config_data["max_users"] = data_receive['max_users']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "save",config_data)

            toast("success")

        except Exception as e:

            toast("error")
            utils.error_log(e)

    elif type_id == "save_rank":

        try:

            config_data["bg"] = data_receive['bg']
            config_data["op"] = data_receive['op']
            config_data["rank_type"] = data_receive['rank_type']
            config_data["rank_side"] = data_receive['rank_side']
            config_data["font_size"] = data_receive['font_size']
            config_data["font_color"] = data_receive['font_color']
            config_data["card_size"] = data_receive['card_size']
            config_data["image_size"] = data_receive['image_size']


            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "save",config_data)

            toast("success")
            
        except Exception as e:

            toast("error")
            utils.error_log(e)


def votes(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive['type_id']

    def determine_winner(options):
        winner = None
        max_votes = -1

        for option, info in options.items():
            votes = info.get("votes", 0)
            if votes > max_votes:
                max_votes = votes
                winner = option

        return winner, max_votes

    if type_id == "get_options":

        data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "load")

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "create_options":

        try:

            name = data_receive['name']

            data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "load")
            
            options = data["options"]

            new_option_key = f"option{len(options) + 1}"
            options[new_option_key] = {
                "name": f"{name}",
                "votes": 0
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "save", data)

            toast("Opção adicionada")

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            toast("error")
            utils.error_log(e)
        
    elif type_id == "remove_options":

        try:

            option = data_receive['option']

            data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "load")

            del data["options"][option]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "save", data)

            toast("Opção removida")

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            toast("error")
            utils.error_log(e)

    elif type_id == "end_votes":

        try:

            data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "load")

            data["status"] = 'Ended'
            data["voted"] = []

            winner, votes = determine_winner(data[options])           

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "save", data)

            toast("Votação finalizada")

            aliases = {
                "{winner}" : winner,
                "{votes}": votes,
                "{name}" : data["name"]
            }

            message_data = utils.messages_file_load("command_vote_ended")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            toast("error")
            utils.error_log(e)

    elif type_id == "new_votes":

        try:

            name = data_receive['name']
            option1 = data_receive['option1']
            option2 = data_receive['option2']

            data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "load")

            data["name"] = name
            
            data["status"] = 'Voting'

            data["options"] = {}

            data["options"]["option1"] = {
                "name" : option1,
                "votes" : 0
            }

            data["options"]["option2"] = {
                "name" : option2,
                "votes" : 0
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json", "save", data)

            aliases = {
                "{name}" : data["name"]
            }

            message_data = utils.messages_file_load("command_vote_started")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            toast("Votação criada")

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            toast("error")
            utils.error_log(e)

    elif type_id == "get_commands":

        command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/commands.json", "load")
        
        
        data = {
            "command": command_data["command"],
            "status": command_data["status"],
            "delay": command_data["delay"],
            "user_level" : command_data["user_level"],
            "cost" : command_data["cost"],
            "cost_status" : command_data["cost_status"]
        }

        data_dump = json.dumps(data, ensure_ascii=False)

        return data_dump
        
    elif type_id == "save_commands":

        try:

            command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/commands.json", "load")

            if command_data is not None:
                
                command_data["command"] = data_receive["command"]
                command_data["status"] = data_receive["status"]
                command_data["delay"] = data_receive["delay"]
                command_data["user_level"] = data_receive["user_level"]
                command_data["cost"] = data_receive["cost"]
                command_data["cost_status"] = data_receive["cost_status"]

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/commands.json", "save", command_data)

            toast('Salvo')

        except Exception as e:
            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)

    elif type_id == "save_html":
        
        try:

            update_votes = utils.update_votes(data_receive)


            data_goal = {
                'type': 'votes',
                'html': update_votes
            }
                
            if server.started:
                server.broadcast_message(json.dumps(data_goal))

            return update_votes
            
        except Exception as e:
            
            toast('erro')
            utils.error_log(e)

    elif type_id == "get_html":
        
        html_info = utils.update_votes(data_receive)

        data_dump = json.dumps(html_info, ensure_ascii=False)

        return data_dump


def subathon(data):

    config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/config.json", "load")
    commands_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/commands.json", "load")
    style_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/style.json", "load")
    gifts_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "load")

    data_receive = json.loads(data)

    type_id = data_receive['type_id']

    if type_id == "get_gift_info":

        gift_id = data_receive["id"]
        
        name = gifts_data["gifts"][gift_id]["name_br"]

        if name == "" or name == None:
            name = gifts_data["gifts"][gift_id]["name"]

        data = {
            "name" : name,
            "time" : gifts_data["gifts"][gift_id]["time"],
            "status_subathon" : gifts_data["gifts"][gift_id]["status_subathon"]
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save_gift_info":

        try:

            gift_id = data_receive["id"]
            
            gifts_data["gifts"][gift_id]["time"] = data_receive['time']
            gifts_data["gifts"][gift_id]["status_subathon"] = data_receive['status']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "save", gifts_data)

            toast('Salvo')

        except Exception as e:
            
            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)

    elif type_id == "get":
        
        data = {
            "status": config_data["status"],
            "gifts": gifts_data["gifts"],
            'time_global' : config_data["time_global"],
            "time_type" : config_data["time_type"]
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save":
        
        try:

            data = {
                "status": data_receive["status"],
                "time_global" : data_receive["time_global"],
                "time_type" : data_receive["time_type"], 
            }

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/config.json", "save", data)

            toast('Salvo')
            
        except Exception as e:
            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)

    elif type_id == "get_commands":

        command_type = data_receive['type_command']

        data = commands_data[command_type]

        return json.dumps(data, ensure_ascii=False)  

    elif type_id == "save_commands":

        try:

            command_type = data_receive['type_command']

            if commands_data is not None:
                
                commands_data[command_type]["command"] = data_receive["command"]
                commands_data[command_type]["status"] = data_receive["status"]
                commands_data[command_type]["delay"] = data_receive["delay"]
                commands_data[command_type]["user_level"] = data_receive["user_level"]
                commands_data[command_type]["cost"] = data_receive["cost"]
                commands_data[command_type]["cost_status"] = data_receive["cost_status"]

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/commands.json", "save", commands_data)

            toast('Salvo')
            
        except Exception as e:
            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)

    elif type_id == "add":

        value_int = data_receive['value']

        data_goal = {
            'type': 'clock',
            'action' : 'add',
            'time': value_int
        }
            
        if server.started:
            server.broadcast_message(json.dumps(data_goal))


        aliases = {
            '{value}' : value_int
        }

        message_data = utils.messages_file_load("subathon_minutes_add")
        message = utils.replace_all(message_data['response'], aliases)
        
        notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

    elif type_id == "remove":


        value_int = data_receive['value']

        data_goal = {
            'type': 'clock',
            'action' : 'remove',
            'time': value_int
        }
            
        if server.started:
            server.broadcast_message(json.dumps(data_goal))


        aliases = {
            '{value}' : value_int
        }

        message_data = utils.messages_file_load("subathon_minutes_remove")
        message = utils.replace_all(message_data['response'], aliases)
        
        notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

    elif type_id == "reset":

        data_goal = {
            'type': 'clock',
            'action' : 'reset',
        }
            
        if server.started:
            server.broadcast_message(json.dumps(data_goal))


        message_data = utils.messages_file_load("subathon_minutes_reset")
        message = message_data['response']
        
        notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

    elif type_id == "get_style":

        return json.dumps(style_data, ensure_ascii=False)

    elif type_id == "save_style":

        try:

            background_opacity = utils.convert_opacity_to_hex(float(data_receive['opacity'])) 
            background_color = f"{data_receive['color2']}{background_opacity}"

            style_data['color1'] = data_receive['color1']
            style_data['color2'] = background_color
            style_data['opacity'] = data_receive['opacity']


            utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/style.json", "save", style_data)
            
            
            style_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/style.json", "load")

            data = {
                "type" : 'clock',
                "action" : 'style',
                "color1" : style_data['color1'],
                "color2" : style_data['color2']
            }

            if server.started:
                server.broadcast_message(json.dumps(data))

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/style.json", "save", style_data)

            toast('Salvo')
            
        except Exception as e:

            toast('Ocorreu um erro ao salvar')
            utils.error_log(e)              


def tiktok_auth(data_receive):

    try:
        
        data_receive = json.loads(data_receive)

        data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "load")

        username = data_receive["username"]
        data["USERNAME"] = username.lower()
        data["SESSIONID"] = data_receive["sessionid"]
        data["ERROR"] = data_receive["error_status"]

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "save", data)

        if data_receive['error_status'] == True:
            
            send_discord_webhook_auth("Nova autenticação", username.lower())

        start_websocket_CS()

        toast("success")

        return True
    
    except Exception as e:
        utils.error_log(e)

        toast("error")

        return False


def tiktok_alerts(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    event_config_json_path = f"{utils.local_work('appdata_path')}/events/event_not.json"

    event_config_data = utils.manipulate_json(event_config_json_path, "load")

    if type_id == "get":

        data = {
            "like_delay": event_config_data["ttk_like"]["delay"],
            "share_delay": event_config_data["ttk_share"]["delay"],
            "follow_sound_status": event_config_data["ttk_follow"]["sound"],
            "follow_sound_loc": event_config_data["ttk_follow"]["sound_loc"],
            "follow_sound_volume": event_config_data["ttk_follow"]["sound_volume"],
            "like_sound_status": event_config_data["ttk_like"]["sound"],
            "like_sound_loc": event_config_data["ttk_like"]["sound_loc"],
            "like_sound_volume": event_config_data["ttk_like"]["sound_volume"],
            "share_sound_status": event_config_data["ttk_share"]["sound"],
            "share_sound_loc": event_config_data["ttk_share"]["sound_loc"],
            "share_sound_volume": event_config_data["ttk_share"]["sound_volume"]
        }

        return  json.dumps(data, ensure_ascii=False)

    elif type_id in ("save_sound_follow", "save_sound_like", "save_sound_share"):

        try:
            event_type = type_id.split("_")[2]

            event_config_data[f"ttk_{event_type}"]["sound"] = data_receive["sound"]
            event_config_data[f"ttk_{event_type}"]["sound_loc"] = data_receive["sound_loc"]
            event_config_data[f"ttk_{event_type}"]["sound_volume"] = data_receive["sound_volume"]
            
            if event_type != "follow":
                event_config_data[f"ttk_{event_type}"]["delay"] = data_receive["delay"]

            utils.manipulate_json(event_config_json_path, "save", event_config_data)
            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def tiktok_gift(data_receive):

    ttk_data_gifts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "load")

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    if type_id == "get":

        data = {
            "status" : ttk_data_gifts["status"],
            "volume" : ttk_data_gifts["volume"],
            "sound" : ttk_data_gifts["audio"],
            "gifts": ttk_data_gifts["gifts"]
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save_sound_gift":

        try:

            gift_id = data_receive["id"]

            ttk_data_gifts["gifts"][gift_id]["name_br"] = data_receive["name"]
            ttk_data_gifts["gifts"][gift_id]["status"] = data_receive["status"]
            ttk_data_gifts["gifts"][gift_id]["audio"] = data_receive["sound_loc"]
            ttk_data_gifts["gifts"][gift_id]["volume"] = data_receive["sound_volume"]
            ttk_data_gifts["gifts"][gift_id]["keys"] = data_receive["keys"]
            ttk_data_gifts["gifts"][gift_id]["key_status"] = data_receive["key_status"]
            ttk_data_gifts["gifts"][gift_id]["key_time"] = data_receive["key_time"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "save", ttk_data_gifts)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")

    elif type_id == "save_point_gift":

        try:

            gift_id = data_receive["id"]

            ttk_data_gifts["gifts"][gift_id]["points-global"] = data_receive["status"]
            ttk_data_gifts["gifts"][gift_id]["points"] = data_receive["points"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "save", ttk_data_gifts)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")

    elif type_id == "get_gift_info":

        gift_id = data_receive["id"]
        
        data = {
            "name" : ttk_data_gifts["gifts"][gift_id]["name_br"],
            "audio": ttk_data_gifts["gifts"][gift_id]["audio"],
            "status": ttk_data_gifts["gifts"][gift_id]["status"],
            "volume": ttk_data_gifts["gifts"][gift_id]["volume"],
            "points_status": ttk_data_gifts["gifts"][gift_id]["points-global"],
            "points": ttk_data_gifts["gifts"][gift_id]["points"],
            "keys" : ttk_data_gifts["gifts"][gift_id]["keys"],
            "key_status" : ttk_data_gifts["gifts"][gift_id]["key_status"],
            "key_time" : ttk_data_gifts["gifts"][gift_id]["key_time"]
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "global_gift_save":

        try:

            ttk_data_gifts["status"] = data_receive["status"]
            ttk_data_gifts["audio"] = data_receive["sound"]
            ttk_data_gifts["volume"] = data_receive["volume"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "save", ttk_data_gifts)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def tiktok_logs(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    event_config_path = f"{utils.local_work('appdata_path')}/events/event_not.json"

    event_config_data = utils.manipulate_json(event_config_path, "load")

    if type_id == "get":

        type_not = data_receive["type_not"]

        file_data = event_config_data[type_not]

        data = {"status": file_data["status"], "message": file_data["response_chat"]}

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save":
        
        try:

            type_not = data_receive["type_not"]
            event_config_data[type_not]["status"] = data_receive["status"]
            event_config_data[type_not]["response_chat"] = data_receive["message"]

            utils.manipulate_json(event_config_path, "save", event_config_data)
            
            toast("success")

        except Exception as e:
            
            utils.error_log(e)
            toast("error")


def tiktok_goal(data):

    data = json.loads(data)

    type_id = data["type_id"]

    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "load")

    if type_id == "get":

        goal_type = data["goal_type"]

        if goal_type == "gift":

            ttk_data_gifts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "load")

            gift_list = []

            for key, value in ttk_data_gifts["gifts"].items():

                if value["name_br"] != "":
                    name = value["name_br"]
                else:
                    name = value["name"]

                gift_list.append({"id": value["id"], "name": name})

            data = {
                "status": goal_data[goal_type]["status"],
                "goal": goal_data[goal_type]["goal"],
                "gift_list": gift_list,
                "event": goal_data[goal_type]["event"],
                "goal_add": goal_data[goal_type]["goal_after"],
                "status_sound": goal_data[goal_type]["sound_status"],
                "sound_file": goal_data[goal_type]["sound_file"],
                "sound_volume": goal_data[goal_type]["sound_volume"],
            }

        else:

            data = {
                "status": goal_data[goal_type]["status"],
                "goal": goal_data[goal_type]["goal"],
                "event": goal_data[goal_type]["event"],
                "goal_add": goal_data[goal_type]["goal_after"],
                "status_sound": goal_data[goal_type]["sound_status"],
                "sound_file": goal_data[goal_type]["sound_file"],
                "sound_volume": goal_data[goal_type]["sound_volume"],
            }

        return json.dumps(data, ensure_ascii=False)

    if type_id == "save":
        
        try:

            goal_type = data["goal_type"]

            if goal_type == "gift":
                goal_data[goal_type]["gift"] = data["gift"]

            goal_data[goal_type]["status"] = data["status"]
            goal_data[goal_type]["goal"] = data["goal"]
            goal_data[goal_type]["goal_after"] = data["goal_add_value"]
            goal_data[goal_type]["event"] = data["event"]
            goal_data[goal_type]["sound_status"] = data["sound_status"]
            goal_data[goal_type]["sound_file"] = data["sound_file"]
            goal_data[goal_type]["sound_volume"] = data["sound_volume"]

            data_goal = {
                "type": "update_goal",
                "type_goal": goal_type,
                "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
            }

            server.broadcast_message(json.dumps(data_goal))
        

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    if type_id == "save_html":
        
        try:

            type_goal = data['type_goal']

            update_goal = utils.update_goal(data)

            data_goal = {
                'type': 'update_goal',
                'type_goal': type_goal,
                'html': update_goal
            }
                
            if server.started:
                server.broadcast_message(json.dumps(data_goal))

            return update_goal
            
        except Exception as e:
            
            toast('erro')
            utils.error_log(e)

    if type_id == "get_html":
        
        html_info = utils.update_goal(data)

        data_dump = json.dumps(html_info, ensure_ascii=False)

        return data_dump


def highlighted(data):

    data_receive = json.loads(data)

    type_id = data_receive["type_id"]

    if type_id == "get":
        
        data_loads = utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "load")

        data = {
            "text": data_loads["text"],
            "show_text": data_loads["show_text"],
            "background": data_loads["background"],
            "border": data_loads["border"]
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save_text":

        try:

            data_loads = utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "load")

            data_loads['text'] = data_receive["text"]
            data_loads['show_text'] = data_receive["show_text"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "save", data_loads)

            data_loads = utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "load")

            data_broadcast = {
                'type': 'highlighted',
                'show_text' : data_loads["show_text"],
                'background' : data_loads['background'],
                'border' : data_loads['border'],
                'html': data_loads["text"]
            }

            if server.started:
                server.broadcast_message(json.dumps(data_broadcast))

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error") 

    elif type_id == "save_style":

        try:

            data_loads = utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "load")

            data_loads['background'] = data_receive["background_color"]
            data_loads['border'] = data_receive["border_color"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "save", data_loads)


            data_loads = utils.manipulate_json(f"{utils.local_work('appdata_path')}/highlighted/config.json", "load")

            data_broadcast = {
                'type': 'highlighted',
                'show_text' : data_loads["show_text"],
                'background' : data_loads['background'],
                'border' : data_loads['border'],
                'html': data_loads["text"]
            }

            if server.started:
                server.broadcast_message(json.dumps(data_broadcast))

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error") 


def disclosure_py(type_id, data_receive):

    disclosure_json_path = f"{utils.local_work('appdata_path')}/config/disclosure.json"

    if type_id == "save":

        disclosure_data = utils.manipulate_json(disclosure_json_path, "load")
        disclosure_data["message"] = data_receive
        utils.manipulate_json(disclosure_json_path, "save", disclosure_data)

    elif type_id == "get":

        disclosure_data = utils.manipulate_json(disclosure_json_path, "load")
        disclosure_message = disclosure_data.get("message", "")

        if not disclosure_message:

            disclosure_message = "Digite aqui a sua mensagem rápida de divulgação em chats"

        return disclosure_message


def playlist_py(type_id, data):

    playlist_json_path = f"{utils.local_work('appdata_path')}/player/list_files/playlist.json"
    config_json_path = f"{utils.local_work('appdata_path')}/player/config/config.json"

    def start_add(playlist_url):
        
        try:
            playlist_data = utils.manipulate_json(playlist_json_path, "load")
            
            check_have = any(playlist_data.keys())

            if not check_have:
                last_key = 0
            else:
                playlist_keys = [int(x) for x in playlist_data.keys()]
                last_key = max(playlist_keys)

            def cli_to_api(*opts):
                default = yt_dlp.parse_options([]).ydl_opts
                diff = {k: v for k, v in yt_dlp.parse_options(opts).ydl_opts.items() if default[k] != v}
                return diff

            ytdlp_opts = cli_to_api('--flat-playlist','--quiet','--ignore-errors')
            
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                playlist = ydl.extract_info(playlist_url, download=False)

                for video in playlist["entries"]:
                    
                    last_key = last_key + 1
                    video_title = video['title']
                    video_url = video['url']


                    playlist_data[last_key] = {"MUSIC": video_url, "USER": "playlist", "MUSIC_NAME": video_title}
                
                utils.manipulate_json(playlist_json_path, "save", playlist_data)

        except Exception as e:
            
            utils.error_log(e)

    if type_id == "add":

        def is_youtube_url(string):
            
            youtube_regex = re.compile(
                r"(http(s)?://)?(www\.)?(youtube\.com/(watch\?v=|playlist\?list=)|youtu\.be/)[^\s]+"
            )

            match = youtube_regex.match(string)

            if match:
                return True
            else:
                return False

        if is_youtube_url(data):

            if re.match(r"https?://(www\.)?youtube\.com/playlist\?list=.*", data):

                toast("Adicionando, aguarde")
                threading.Thread(target=start_add, args=(data,), daemon=True).start()

            elif re.match(r"https?://(www\.)?youtube\.com/watch\?v=.*&list=.*", data):

                url = re.sub(r"watch\?v=[^&]*&?", "", data)
                url = url.replace("list=", "playlist?list=")

                toast("Adicionando, aguarde")
                threading.Thread(target=start_add, args=(url,), daemon=True).start()


            else:

                toast("A URL deve ser do YouTube e conter uma ID de playlist, ex: https://www.youtube.com/watch?v=xxxxxxxxxx&list=xxxxxxxxxxxxxxxxxxxxxxxxxx ou https://www.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        else:

            toast("A URL deve ser do YouTube e conter uma ID de playlist, ex: https://www.youtube.com/watch?v=xxxxxxxxxx&list=xxxxxxxxxxxxxxxxxxxxxxxxxx ou https://www.youtube.com/playlist?list=xxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    elif type_id == "save":

        playlist_stats_data = utils.manipulate_json(config_json_path, "load")
        playlist_stats_data["STATUS"] = data

        utils.manipulate_json(config_json_path, "save", playlist_stats_data)

        if data == 1:
            toast("Reprodução de playlist ativada")
        else:
            toast("Reprodução de playlist desativada")

    elif type_id == "get":

        playlist_stats_data = utils.manipulate_json(config_json_path, "load")
        return playlist_stats_data.get("STATUS", 0)

    elif type_id == "clear":

        playlist_data = {}
        utils.manipulate_json(playlist_json_path, "save", playlist_data)

    elif type_id == "queue":

        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")

        playlist_data = utils.manipulate_json(playlist_json_path, "load")
        list_queue_list = {}

        for key in queue_data:
            music = queue_data[key]["MUSIC_NAME"]
            user = queue_data[key]["USER"]
            list_queue_list[music] = user

        for key in playlist_data:
            music = playlist_data[key]["MUSIC_NAME"]
            user = playlist_data[key]["USER"]
            list_queue_list[music] = user


        return json.dumps(list_queue_list, ensure_ascii=False)


def sr_config_py(type_id, data_receive):

    config_path = f"{utils.local_work('appdata_path')}/player/config/"
    commands_path = f"{config_path}commands.json"
    notfic_path = f"{utils.local_work('appdata_path')}/config/notfic.json"
    config_json_path = f"{config_path}config.json"

    commands_music_data = utils.manipulate_json(commands_path, "load")
    not_music_data = utils.manipulate_json(notfic_path, "load")
    status_music_data = utils.manipulate_json(config_json_path, "load")

    if type_id == "get":
        data = {
            "allow_music": status_music_data["STATUS_MUSIC_ENABLE"],
            "max_duration": status_music_data["max_duration"],
            "skip_votes": status_music_data["skip_votes"],
            "skip_mod": status_music_data["skip_mod"],
            "not_status": not_music_data["HTML_PLAYER_ACTIVE"],
        }

        music_dump = json.dumps(data, ensure_ascii=False)

        return music_dump

    if type_id == "get_command":
        
        try:

            data = {
                "command": commands_music_data[data_receive]["command"],
                "status": commands_music_data[data_receive]["status"],
                "delay": commands_music_data[data_receive]["delay"],
                "last_use": commands_music_data[data_receive]["last_use"],
                "user_level": commands_music_data[data_receive]["user_level"],
                "cost" : commands_music_data[data_receive]["cost"],
                "cost_status" : commands_music_data[data_receive]["cost_status"]
            }


            return json.dumps(data, ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "save":

        data = json.loads(data_receive)

        try:
            allow = data["allow_music_save"]
            max_duration = data["max_duration"]
            skip_votes = data["skip_votes"]
            skip_mod = data["skip_mod"]
        
            utils.manipulate_json(notfic_path, "save", not_music_data)
            utils.manipulate_json(commands_path, "save", commands_music_data)

            status_music_data["STATUS_MUSIC_ENABLE"] = allow
            status_music_data["max_duration"] = max_duration
            status_music_data["skip_votes"] = skip_votes
            status_music_data["skip_mod"] = skip_mod

            utils.manipulate_json(config_json_path, "save", status_music_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "save_command":

        try:
            data = json.loads(data_receive)

            type_command = data["type_command"]

            commands_music_data[type_command] = {
                "command": data["command"],
                "status": data["status"],
                "delay": data["delay"],
                "last_use": commands_music_data[type_command]["last_use"],
                "user_level": data["user_level"],
                "cost" : data["cost"],
                "cost_status" : data["cost_status"]
            }

            utils.manipulate_json(commands_path, "save", commands_music_data)

            toast("Comando salvo")

        except Exception as e:

            utils.error_log(e)
            toast("Ocorreu um erro ao salvar o comando")

    elif type_id == "get-status":

        return status_music_data["STATUS_MUSIC_ENABLE"]

    elif type_id == "list_add":

        config_music_data = utils.manipulate_json(config_json_path, "load")
        config_music_data["blacklist"].append(data_receive)

        utils.manipulate_json(config_json_path, "save", config_music_data)
        toast("Termo ou nome adicionado")

    elif type_id == "list_get":

        config_music_data = utils.manipulate_json(config_json_path, "load")

        return json.dumps(config_music_data["blacklist"], ensure_ascii=False)

    elif type_id == "list_rem":

        config_music_data = utils.manipulate_json(config_json_path, "load")

        if data_receive in config_music_data["blacklist"]:

            config_music_data["blacklist"].remove(data_receive)

            utils.manipulate_json(config_json_path, "save", config_music_data)

            toast("Termo ou nome removido")

        else:

            toast("O termo ou nome não está na lista")

        config_music_data = utils.manipulate_json(config_json_path, "load")

        return json.dumps(config_music_data["blacklist"], ensure_ascii=False)


def update_check(type_id):

    if type_id == "check":
        
        try:
            
            response = req.get("https://api.github.com/repos/GGTEC/VibesBot/releases/latest")
            response_json = json.loads(response.text)
            version = response_json["tag_name"]

            if version != curr_version:
                
                debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")

                debug_data['updated'] = "False"
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json", "save", debug_data)

                return True

            else:

                return False
            
        except:
            
            return False

    elif type_id == "open":

        url = "https://github.com/GGTEC/VibesBot/releases"
        webbrowser.open(url, new=0, autoraise=True)

        close()


def get_video_info(title):

    def remove_string(value):

        try:
            symbols = [["[", "]"], ["(", ")"], ['"', '"']]
            for symbol in symbols:
                if value.find(symbol[0]) and value.find(symbol[1]):
                    value = value.replace(
                        value[
                            (index := value.find(symbol[0])) : value.find(
                                symbol[1], index + 1
                            )
                            + 1
                        ],
                        "",
                    ).strip()
            return value
        except:
            return value

    ydl_opts = {"skip_download": True, "quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        try:

            if validators.url(title):

                video_info = ydl.extract_info(title, download=False)

            else:

                video_info = ydl.extract_info(f"ytsearch:{title}", download=False)["entries"][0]
            
            video_id = video_info.get("id", None)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title = video_info.get("title", None)
            video_length = video_info.get("duration", None)
            video_thumb = video_info.get("thumbnail", None)

            data = {
                "url": video_url,
                "title": remove_string(video_title),
                "thumb": video_thumb,
                "length": video_length,
            }

            result = namedtuple("result", data.keys())(*data.values())

            return result
        
        except:
            
            return '404'


def start_play(link, user):

    global caching

    music_dir = f"{utils.local_work('datadir')}/web/src/player/cache/music.webm"

    if os.path.exists(music_dir):
        os.remove(music_dir)

    def download_music(link):
        def my_hook(d):
            if d["status"] == "finished":
                toast("Download concluído, Em pós processamento")

        try:
            ydl_opts = {
                "progress_hooks": [my_hook],
                "final_ext": "webm",
                "format": "bestaudio",
                "noplaylist": True,
                "quiet": True,
                "no_color": True,
                "outtmpl": f"{music_dir}",
                "force-write-archive": True,
                "force-overwrites": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            return True

        except Exception as e:
            utils.error_log(e)
            return False

    try:

        caching = True

        response = get_video_info(link)

        if response == "404":

            notification("event", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

        else:

            media_name = response.title
            music_link = response.url
            music_thumb = response.thumb

            title_split = media_name.split(" - ")
            music_name = title_split[0]
            music_artist = title_split[1] if len(title_split) > 1 else ""

            with open(f"{utils.local_work('datadir')}/web/src/player/images/album.png", "wb") as album_art_local:
                album_art_local.write(req.get(music_thumb).content)

            if main_window_open:
                main_window.evaluate_js(f"update_image()")

            if download_music(music_link):

                with open(f"{utils.local_work('appdata_path')}/player/list_files/currentsong.txt", "w", encoding="utf-8") as file_object:
                    file_object.write(f"{media_name}")

                music_name_short = textwrap.shorten(media_name, width=30, placeholder="...")

                music_data = {
                    "redeem_user": user,
                    "music": music_name_short,
                    "artist": music_artist,
                }

                server.broadcast_message(json.dumps({"type": "music", "html": utils.update_music(music_data)}))

                if main_window_open:
                    main_window.evaluate_js(f"update_music_name('{music_name}', '{music_artist}')")

                aliases = {
                    "{music_name}": music_name,
                    "{music_name_short}": music_name_short,
                    "{music_artist}": music_artist,
                    "{username}": user,
                    "{nickname}": user,
                }

                if main_window_open:
                    main_window.evaluate_js(f"player('play', 'http://localhost:7000/src/player/cache/music.webm', '1')")

                toast(f"Reproduzindo {music_name_short} - {music_artist}")

                message_data = utils.messages_file_load("music_playing")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")


                config_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

                config_data_player["skip_requests"] = 0

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)

                caching = False
                
            else:
                
                caching = False
                
                toast(f"Erro ao processar música {link} - {user}")

                message_data = utils.messages_file_load("music_process_cache_error")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

    except Exception as e:
        
        utils.error_log(e)

        toast(f"Erro ao processar música {link} - {user}")

        aliases = {
            "{username}": user,
            "{nickname}": user,
        }

        message_data = utils.messages_file_load("music_process_cache_error")
        message = utils.replace_all(message_data['response'], aliases)

        notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

        caching = False


def loopcheck():
    
    while loaded_status == True:

        try:

            playlist_path = f"{utils.local_work('appdata_path')}/player/list_files/playlist.json"
            queue_path = f"{utils.local_work('appdata_path')}/player/list_files/queue.json"
            config_path = f"{utils.local_work('appdata_path')}/player/config/config.json"
                
            playlist_data = utils.manipulate_json(playlist_path, "load")
            playlist_execute_data = utils.manipulate_json(config_path, "load")
            
            queue_data = utils.manipulate_json(queue_path,"load")

            playlist_execute = int(playlist_execute_data["STATUS"])

            check_have_playlist = any(playlist_data.keys())
            check_have_queue = any(queue_data.keys())

            if main_window_open:
                playing = main_window.evaluate_js(f"player('playing', 'none', 'none')")
            
            if not caching and playing == "False":

                if check_have_queue:

                    queue_keys = [int(x) for x in queue_data.keys()]
                    music_data_key = str(min(queue_keys))

                    music = queue_data[music_data_key]["MUSIC"]
                    user = queue_data[music_data_key]["USER"]

                    del queue_data[music_data_key]

                    utils.manipulate_json(queue_path, "save", queue_data)

                    start_play(music, user)

                    time.sleep(3)

                elif check_have_playlist:

                    if playlist_execute == 1:
                        
                        playlist_keys = [int(x) for x in playlist_data.keys()]
                        music_data = str(min(playlist_keys))

                        music = playlist_data[music_data]["MUSIC"]
                        user = playlist_data[music_data]["USER"]

                        del playlist_data[music_data]

                        utils.manipulate_json(playlist_path, "save", playlist_data)

                        start_play(music, user)
                        
                    else:
                        time.sleep(3)
                else:
                    time.sleep(3)
                    if main_window_open:
                        main_window.evaluate_js(f"update_music_name('Aguardando', 'Aguardando')")

            time.sleep(3)


        except Exception as e:
            
            if not isinstance(e, KeyError):
                utils.error_log(e)
            
            time.sleep(3)


def music_process(data):

    config_music_path = F"{utils.local_work('appdata_path')}/player/config/config.json"
    queue_json_path = F"{utils.local_work('appdata_path')}/player/list_files/queue.json"

    user_data_load = userdatabase.get_user_data(data["userid"])
    
    config_music_data = utils.manipulate_json(config_music_path, 'load')
    queue_data = utils.manipulate_json(queue_json_path, 'load')
    
    blacklist = config_music_data["blacklist"]
    max_duration = int(config_music_data["max_duration"])

    user_input = data["user_input"].strip()

    username = user_data_load["username"]
    nickname = user_data_load["display_name"]

    last_key = str(max(map(int, queue_data.keys()), default=0) + 1) if queue_data else "1"

    def start_process():
        
        try:

            toast(f"Processando pedido {user_input} - {nickname}")

            if not any(item in user_input for item in blacklist):

                response = get_video_info(user_input)

                if response == "404":

                    aliases = {
                        "{username}": username,
                        "{music}": user_input,
                        "{nickname}" : nickname
                    } 

                    message_data = utils.messages_file_load("music_process_error")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("music", message_data["status"],message_data["status_s"], message, "", "", "")
                    
                
                else:

                    music_name, video_url, music_length = response.title, response.url, response.length

                    if music_length < max_duration:

                        queue_data[last_key] = {
                            "MUSIC": video_url,
                            "USER": nickname, 
                            "MUSIC_NAME": music_name
                        }

                        utils.manipulate_json(queue_json_path, 'save', queue_data)

                        aliases = {
                            "{username}": username, 
                            "{nickname}": nickname,
                            "{user_input}": video_url, 
                            "{music}": music_name
                        }

                        message_data = utils.messages_file_load("music_added_to_queue")
                        message = utils.replace_all(message_data['response'], aliases)
                    
                        notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

                    else:

                        music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                        aliases = {
                            "{max_duration}": str(max_duration), 
                            "{username}": str(username),
                            "{nickname}": str(nickname),
                            "{user_input}": str(user_input),
                            "{music}": str(music_name),
                            "{music_short}": str(music_name_short)
                        }

                        message_data = utils.messages_file_load("music_length_error")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

            else:

                music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                aliases = {
                    "{max_duration}": str(max_duration), 
                    "{username}": str(username),
                    "{nickname}": str(nickname),
                    "{user_input}": str(user_input),
                    "{music}": str(music_name),
                    "{music_short}": str(music_name_short)
                }

                message_data = utils.messages_file_load("music_blacklist")
                message = utils.replace_all(message_data['response'], aliases)

                notification("music", message_data["status"],message_data["status_s"], message, "", "", "")


        except Exception as e:

            utils.error_log(e)

            aliases = {
                "{username}": str(username),
                "{nickname}": str(nickname),
                "{user_input}": str(user_input)
            }

            message_data = utils.messages_file_load("music_add_error")
            message = utils.replace_all(message_data['response'], aliases)

            notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

    def convert_address(original_address):
        result = re.match(r"youtu\.be\/(\w+)\?.*", original_address)
        if result:
            video_code = result.group(1)
            new_address = f"https://www.youtube.com/watch?v={video_code}"
            return new_address
        else:
            return original_address

    if validators.url(user_input):

        if "youtube" in user_input or "youtu" in user_input:
            start_process(convert_address(user_input))

        else:

            message_data = utils.messages_file_load("music_link_youtube")
            
            notification("music", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")
    else:

        start_process()


def open_py(type_id, link_profile):
    
    if type_id == "user":
        webbrowser.open("https://tiktok.com/@" + link_profile, new=0, autoraise=True)

    if type_id == "link":
        webbrowser.open(link_profile, new=0, autoraise=True)

    elif type_id == "appdata":

        try:

            path = utils.local_work("appdata_path")
            path = os.path.normpath(path)

            subprocess.Popen(f"explorer {path}")

        except subprocess.CalledProcessError as e:

            utils.error_log(e)
            toast("Ocorreu um erro.")

    elif type_id == "errolog":

        from logerror import LogManager

        logdatabase = LogManager()

        recent_logs = logdatabase.get_recent_logs()

        return recent_logs

    elif type_id == "errolog_clear":
        
        
        from logerror import LogManager

        logdatabase = LogManager()
        
        logdatabase.clear_logs()

        toast("Relatório de erros limpo")

    elif type_id == "discord":
        webbrowser.open("https://discord.gg/KAjHFffdYa", new=0, autoraise=True)

    elif type_id == "wiki":
        webbrowser.open("https://ggtec.netlify.app/apps/vb/", new=0, autoraise=True)

    elif type_id == "debug-get":
        
        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")

        return debug_data["debug"]

    elif type_id == "debug-save":
        
        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")
        debug_data["debug"] = link_profile

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","save",debug_data)

        if link_profile == 1:
            
            toast( f"Configuração salva, reinicie o programa para iniciar no modo Debug Visual...")
            
        elif link_profile == 0:
            
            toast(f"Configuração salva, reinicie o programa para sair do modo Debug Visual...")

    elif type_id == "rel-get":
        
        auth_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json","load")

        return auth_data["error_status"]

    elif type_id == "rel-save":
        
        auth_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json","load")
        
        auth_data["error_status"] = link_profile

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json","save",auth_data)

        toast( f"Configuração salva")
            

def chat_config(data_save, type_config):

    chat_file_path = f"{utils.local_work('appdata_path')}/chat/chat_config.json"

    if type_config == "save":

        try:

            chat_data = utils.manipulate_json(chat_file_path, "load")

            data_received = json.loads(data_save)

            chat_data.update({
                "chat-color-name": data_received["chat_color_name"],
                "chat-color-border": data_received["chat_color_border"],
                "chat-name-select": data_received["chat_name_select"],
                "chat-border-select": data_received["chat_border_select"],
                "chat-animation" : data_received["chat_animation"],
                "data-show": data_received["data_show"],
                "type-data": data_received["type_data"],
                "time-format": data_received["time_format"],
                "font-size": data_received["font_size"],
                "wrapp-message" : data_received["wrapp_message"],
                "show-user-picture": data_received["show_profile_pic"],
                "chat-log-status" : data_received["chat_log_status"],
                "chat-log-days" : data_received["chat_log_days"],
                "slow-mode" : data_received["slow_mode"],
                "slow-mode-time" : data_received["slow_mode_time"]
            })

            utils.manipulate_json(chat_file_path, "save", chat_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_config == "get":

        chat_data = utils.manipulate_json(chat_file_path, "load")
        
        chat_data_return = {
            "chat_color_name": chat_data.get("chat-color-name"),
            "chat_color_border": chat_data.get("chat-color-border"),
            "chat_name_select": chat_data.get("chat-name-select"),
            "chat_border_select": chat_data.get("chat-border-select"),
            "chat_animation": chat_data.get("chat-animation"),
            "time_format": chat_data.get("time-format"),
            "type_data": chat_data.get("type-data"),
            "data_show": chat_data.get("data-show"),
            "font_size": chat_data.get("font-size"),
            "wrapp_message": chat_data.get("wrapp-message"),
            "show_profile_pic" : chat_data.get("show-user-picture"), 
            "chat_log_days": chat_data.get("chat-log-days"),
            "chat_log_status": chat_data.get("chat-log-status"),
            "slow_mode" : chat_data.get("slow-mode"),
            "slow_mode_time" : chat_data.get("slow-mode-time")
        }
        
        return json.dumps(chat_data_return, ensure_ascii=False)


def roles_config(data):

    data = json.loads(data)

    type_id = data["type_id"]

    chat_file_path = f"{utils.local_work('appdata_path')}/chat/roles_config.json"
    chat_data = utils.manipulate_json(chat_file_path, "load")
    
    if type_id == "get":

        chat_data_return = {
            "gift_role": chat_data.get("gift-role"),
            "like_role": chat_data.get("like-role"),
            "share_role": chat_data.get("share-role")
        }
        
        return json.dumps(chat_data_return, ensure_ascii=False)
    
    elif type_id == "save":

        try:

            chat_data.update({
                "gift-role": data["gift_role"],
                "like-role": data["like_role"],
                "share-role": data["share_role"],
            })

            utils.manipulate_json(chat_file_path, "save", chat_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def points_config(data):

    data = json.loads(data)

    type_id = data["type_id"]

    points_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/points.json","load")

    if type_id == "get":

        chat_data_return = {
            "gift_points": points_data_load.get("gifts"),
            "like_points": points_data_load.get("likes"),
            "share_points": points_data_load.get("shares"),
            "follow_points": points_data_load.get("follow")
        }
        
        return json.dumps(chat_data_return, ensure_ascii=False)
    
    elif type_id == "save":

        try:

            points_data_load.update({
                "gifts": float(data["gift_points"]),
                "likes": float(data["like_points"]),
                "shares": float(data["share_points"]),
                "follow": float(data["follow_points"])
            })

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/points.json", "save", points_data_load)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")
            
    elif type_id == "clear-points":

        try:

            userdatabase.clear_user_points()

            toast("Pontos de usuários limpo")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def userdata_py(type_id, username):

    if type_id == "get":

        userdata = userdatabase.get_all_users_data()

        return userdata

    elif type_id == "load":

        data = userdatabase.get_user_data(username)

        return data

    elif type_id == "remove":

        try:

            result = userdatabase.remove_user(username)

            return result
            
        except Exception as e:

            toast("erro")
            utils.error_log(e)
        
            return False

    elif type_id == "save":

        try:

            data = json.loads(username)
            
            userdatabase.edit_user_database(data)

            toast("success")

        except Exception as e:

            toast("erro")
            utils.error_log(e)

    elif type_id == "backup":
         
        try:

            userdatabase.backup_database()

        except Exception as e:
            utils.error_log(e)

    elif type_id == "restore_backup":

        try:
            userdatabase.restore_database()

        except Exception as e:
            utils.error_log(e)

    elif type_id == "external":
        
        main_window.evaluate_js(f"userdata_modal('edit','{username}')")


def commands_module(data) -> None:
    
    def check_perm(user_list, command_list):
        
        list_1 = set(user_list)
        list_2 = set(command_list)

        if list_1.intersection(list_2):
            return True
        else:
            return False

    def compare_strings(s1, s2):
        
        if len(s1) != len(s2):
            return False

        for char1, char2 in zip(s1, s2):
            if char1 != char2:
                return False

        return True

    command_data_prefix = utils.manipulate_json(f"{utils.local_work('appdata_path')}/commands/commands_config.json","load")
    command_data_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","load")
    command_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","load")
    command_data_queue = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","load")
    command_data_tts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/tts.json","load")
    command_data_balance = utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json","load")
    command_data_champ = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/commands.json","load")
    command_data_votes = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/commands.json","load")
    command_data_subathon = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/commands.json","load")
    
    user = data["userid"]
    message_text = data["message"]
    username = data["username"]
    display_name = data["display_name"]
    
    user_data_load_db = userdatabase.get_user_data(user)

    user_roles = user_data_load_db["roles"]
    
    command_string = message_text.lower()

    if len(re.split(r'\s+', command_string, maxsplit=1)) > 1:

        command, sufix = re.split(r'\s+', command_string, maxsplit=1)
        
    else:

        sufix = None
        command = command_string.strip()

    prefix = command[0]

    status_commands = command_data_prefix["STATUS_COMMANDS"]

    random_value = randint(0, 100)

    aliases = {
        "{username}": str(username),
        "{nickname}": str(display_name),
        "{user_id}" : str(user),
        "{command}": str(command),
        "{prefix}": str(prefix),
        "{sufix}": str(sufix),
        "{random}": str(random_value),
        "{value}": str(sufix),
    }

    def extract_top_n_from_string(input_string):
        
        match = re.search(r'{top-(\d+)}', input_string)
        if match:
            return int(match.group(1))
        else:
            return None
    
    def generate_top_users_string(names_and_points, format_string, type_top):

        try:
            
            if not names_and_points or not format_string:

                message_data = utils.messages_file_load("balance_top_error_response")

                notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                return False

            match = re.match(r"{top-(\d+)}", format_string)

            if match:

                num_names = int(match.group(1))

            else:

                message_data = utils.messages_file_load("balance_top_error_response")

                
                notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                return False


            sorted_names_and_points = sorted(names_and_points, key=lambda x: x[1], reverse=True)

            selected_users = sorted_names_and_points[:min(num_names, len(sorted_names_and_points))]
            result_string = f"{', '.join([f'{name} ({points} {type_top})' for name, points in selected_users])} "


            return result_string.strip()

        except Exception as e:

            return f"Error: {str(e)}"
                
    def press_keys(command_info):

        try:

            keys = command_info["keys"]
            time_key = command_info["time_key"]

            keys_filter = [item for item in keys if item.lower() != 'none']

            string_resultante = '+'.join(keys_filter)
            
            if time_key > 0 or time_key != "":

                keyboard.press(string_resultante)

                time.sleep(time_key)

                keyboard.release(string_resultante)

            else:

                keyboard.press_and_release(string_resultante)

        except Exception as e:
            utils.error_log(e)

    def send_error_level(commandinfo):

        user_level = commandinfo["user_level"]

        if isinstance(user_level, str):
            result = user_level.strip("[]").replace("'", "")
            user_level = result.split(", ")

        user_level_string = ""

        if len(user_level) == 1:
            user_level_string = user_level[0]
        elif len(user_level) == 2:
            user_level_string = f"{user_level[0]} ou {user_level[1]}"
        else:
            for i in range(len(user_level) - 1):
                user_level_string += user_level[i] + ", "
            user_level_string += "ou " + user_level[-1]
         
        aliases = {
            "{nickname}" : display_name,
            "{username}": username,
            '{user_level}' : str(user_level_string),
            '{command}' : str(command)
        }

        message_data = utils.messages_file_load("error_user_level")
        message = utils.replace_all(message_data['response'], aliases)

        follow_role_name = utils.messages_file_load('follow_role_name')
        gifts_role_name = utils.messages_file_load('gifts_role_name')
        Likes_role_name = utils.messages_file_load('Likes_role_name')
        shares_role_name = utils.messages_file_load('shares_role_name')
        subscriber_role_name = utils.messages_file_load('subscriber_role_name')
        subscriber_custom_role_name = utils.messages_file_load('subscriber_custom_role_name')
        moderator_role_name = utils.messages_file_load('moderator_role_name')

        aliases_roles = {
            "follow" : follow_role_name['response'],
            "gifts" : gifts_role_name['response'],
            "Likes" : Likes_role_name['response'],
            "shares" :shares_role_name['response'],
            "subscriber" : subscriber_role_name['response'],
            "subscriber_custom" : subscriber_custom_role_name['response'],
            "moderator" : moderator_role_name['response']
        }

        message = utils.replace_all(message, aliases_roles)
        
        notification("command", message_data["status"],message_data["status_s"], message, "", "", "")
        
    def check_status(command_info, aliases):

        message_data = utils.messages_file_load("event_command")
        message = utils.replace_all(message_data['response'], aliases)

        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
        
        status = command_info["status"]
        user_level = command_info["user_level"]
        delay = int(command_info["delay"])
        last_use = command_info["last_use"]
        cost = command_info["cost"]
        cost_status = command_info["cost_status"]

        message_delay, check_time, current = utils.check_delay(delay, last_use)
        
        if status:
        
            if check_perm(user_roles, user_level):
            
                if check_time:
                    
                    if "moderator" in user_level:
                        
                        return current, 'None', True,  'ok'
                    
                    else:
                        
                        if userdatabase.check_cost(user, cost, cost_status):
                            
                            return current, 'None', True,  'ok'
                        
                        else:

                            result = userdatabase.get_user_data(user)

                            if result:
                                
                                value_user = int(result["points"])


                            aliases = {
                                "{cost}" : str(cost),                
                                "{nickname}" : display_name,
                                "{username}": username,
                                "{balance}" : str(value_user)
                            }

                            message_data = utils.messages_file_load("command_cost")
                            message = utils.replace_all(message_data['response'], aliases)

                            message_data['response'] = message

                            return current, message_data, False, 'cost'
                        
                else:

                    return current, message_delay, False, 'delay'
                
            else:

                aliases = {
                    "{nickname}" : display_name,
                    "{username}": username,
                    "{user_level}": str(user_level),
                    "{command}": str(command),
                }


                message_data = utils.messages_file_load("error_user_level")
                message_error = utils.replace_all(message_data['response'], aliases)
                message_data['response'] = message_error

                return current, message_data, False, 'level'

        else:
            
            message_data = utils.messages_file_load("command_disabled")
            message_error = utils.replace_all(message_data['response'], aliases)
            message_data['response'] = message_error

            return current, message_data, False, 'disabled'

    if status_commands == 1:

        command_exists = commanddatabase.command_exists(command)

        if command_exists:

            command_info = commanddatabase.get_command(command)

            command_info = json.loads(command_info)

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                
                response = command_info["response"]

                if response != None:

                    response = utils.replace_all(response, aliases)

                if command_info["type"] == "audio":

                    audio_path = command_info["sound"]
                    audio_volume = command_info['volume']

                    notification("command", 0, 0, None, audio_path, audio_volume, sufix)

                elif command_info["type"] == "audiotext":

                    audio_path = command_info["sound"]
                    audio_volume = command_info['volume']

                    notification("command", 1, 1, response, audio_path, audio_volume, sufix)

                elif command_info["type"] == "tts":

                    if not response == None:

                        user_input_short = textwrap.shorten(response, width=300, placeholder=" ")
                        tts = gTTS(text=user_input_short, lang="pt", slow=False)

                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)

                        rando = random.randint(1, 10)

                        audio_path = f"{utils.local_work('appdata_path')}/temp/tts{rando}.mp3"
                        with open(audio_path, "wb") as f:
                            f.write(mp3_fp.read())

                        notification("command",  1, 1, response, audio_path, 50, sufix)

                    else:

                        message_data = utils.messages_file_load("error_tts_no_text_command")

                        notification("command", message_data["status"],message_data["status_s"], message_data['response'], "", "", sufix)

                elif command_info["type"] == "text":

                    notification("command", 1, 1, response, "", "", sufix)

                if command_info["keys_status"] == 1:

                    threading.Thread(target=press_keys, args=(command_info,), daemon=True).start()


                commanddatabase.update_delay(command, current)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)
                                   
        elif compare_strings(command, command_data_giveaway["add_user"]["command"]):

            command_info = command_data_giveaway["add_user"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    user_input = sufix

                    giveaway_py("add_user", {"new_name": user_input})

                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)
                    
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["enter"]["command"]):

            command_info = command_data_giveaway["enter"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                giveaway_py("add_user", {"new_name": display_name,})

                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["execute_giveaway"]["command"]):

            command_info = command_data_giveaway["execute_giveaway"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                giveaway_py("execute", 'Null')

                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["clear_giveaway"]["command"]):

            command_info = command_data_giveaway["clear_giveaway"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                reset_data = []
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "save", reset_data)

                message_data = utils.messages_file_load("giveaway_clear")
                message = utils.replace_all(message_data['response'], aliases)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
        
                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["check_name"]["command"]):

            command_info = command_data_giveaway["check_name"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")
                    
                    if sufix in giveaway_name_data:
                        
                        user_info = userdatabase.get_user_data(sufix)
                        username = user_info["username"]
                        display_name = user_info["display_name"]


                        aliases_command = {
                            "{value}" : str(sufix),
                            "{nickname}" : display_name,
                            "{username}": username
                        }

                        message_data = utils.messages_file_load("response_user_giveaway")
                        message = utils.replace_all(message_data['response'], aliases)
                        message = utils.replace_all(message, aliases_command)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = utils.messages_file_load("response_no_user_giveaway")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["check_self_name"]["command"]):

            command_info = command_data_giveaway["check_self_name"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                giveaway_name_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "load")

                if display_name in giveaway_name_data:

                    user_info = userdatabase.get_user_data(display_name)
                    username = user_info["username"]
                    display_name = user_info["display_name"]


                    aliases_command = {
                        "{value}" : str(sufix),
                        "{nickname}" : display_name,
                        "{username}": username
                    }

                    message_data = utils.messages_file_load("response_user_giveaway")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message, aliases_command)
                
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    user_info = userdatabase.get_user_data(display_name)
                    username = user_info["username"]
                    display_name = user_info["display_name"]

                    aliases_command = {
                        "{value}" : str(sufix),
                        "{nickname}" : display_name,
                        "{username}": username
                    }

                    message_data = utils.messages_file_load("response_no_user_giveaway")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message, aliases_command)
                
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_player["volume"]["command"]):

            command_info = command_data_player["volume"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    if sufix.isdigit():

                        volume_value_int = int(sufix)

                        if volume_value_int in range(0, 101):

                            volume_value = volume_value_int / 100

                            if main_window_open:
                               main_window.evaluate_js(f"player('volume', 'none', {volume_value})")

                            aliases_commands = {
                                "{volume}": str(volume_value_int),
                            }

                            message_data = utils.messages_file_load("command_volume_confirm")
                            message = utils.replace_all(message_data['response'], aliases)

                            message = utils.replace_all(message, aliases_commands)
                            
                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)



                        else:
                            
                            aliases_commands = {
                                "{volume}": str(volume_value_int),
                            }

                            message_data = utils.messages_file_load("command_volume_error")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_commands)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = utils.messages_file_load("command_volume_number")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    if main_window_open:
                        volume_atual = main_window.evaluate_js(
                            f"player('get_volume', 'none', 'none')"
                        )

                    aliases_commands = {
                        "{volume}": str(volume_atual),
                    }

                    message_data = utils.messages_file_load("command_volume_response")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message,aliases_commands)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_player["skip"]["command"]):

            command_info = command_data_player["skip"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                config_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","load")

                skip_votes = int(config_data_player["skip_votes"])
                skip_requests = int(config_data_player["skip_requests"])
                skip_mod = config_data_player["skip_mod"]
                skip_users = config_data_player["skip_users"]

                if main_window_open:
                    playing = main_window.evaluate_js(f"player('playing', 'none', 'none')")

                if not playing == "False":
                    
                    if "moderator" in user_roles and skip_mod == 1:

                        if main_window_open:
                            main_window.evaluate_js(f"player('stop', 'none', 'none')")

                        message_data = utils.messages_file_load("command_skip_confirm")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                        command_data_player["skip"]["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)

                        config_data_player["skip_requests"] = 0

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player)

                    else:

                        if not user in skip_users:

                            skip_requests = int(skip_requests) + 1

                            aliases_commands = {
                                "{votes}": str(skip_requests),
                                "{minimum}": str(skip_votes),
                            }

                            message_data = utils.messages_file_load("skip_votes")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_commands)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            if int(skip_requests) == skip_votes:

                                if main_window_open:
                                    main_window.evaluate_js(f"player('stop', 'none', 'none')")

                                message_data = utils.messages_file_load("command_skip_confirm")
                                message = utils.replace_all(message_data['response'], aliases)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                                command_data_player["skip"]["last_use"] = current

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player,)

                                config_data_player["skip_requests"] = 0
                                config_data_player["skip_users"] = []

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player)

                            else:

                                skip_users.append(display_name)

                                config_data_player["skip_users"] = skip_users
                                config_data_player["skip_requests"] = int(skip_requests)

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player,)

                        else:

                            message_data = utils.messages_file_load("command_skip_inlist")
                            message = utils.replace_all(message_data['response'], aliases)
                            
                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            command_data_player["skip"]["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player,)

                else:
                    
                    message_data = utils.messages_file_load("command_skip_noplaying")
                    message = utils.replace_all(message_data['response'], aliases)
                    
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    command_data_player["skip"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)
            
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)
        
        elif compare_strings(command, command_data_player['request']['command']):

            command_info = command_data_player['request']

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                prefix_sr = command_data_player['request']['command']
                user_input = command_string.split(prefix_sr)

                if len(user_input) > 1 and user_input[1] != "":
                    
                    user_input = user_input[1]
                    
                    if sr_config_py('get-status','null') == 1:

                        data = {
                            "userid": user,
                            "user_input" : user_input
                        }

                        threading.Thread(target=music_process, args=(data,), daemon=True).start()
                        
                    else:
                        
                        message_data = utils.messages_file_load("music_disabled")
                        message = utils.replace_all(message_data['response'], aliases)
                    
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                        command_data_player['request']['last_use'] = current
                        
                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)
                        

                else:

                    message_data = utils.messages_file_load("command_value")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_player['atual']['command']):

            command_info = command_data_player['atual']

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                           
                f = open(f"{utils.local_work('appdata_path')}/player/list_files/currentsong.txt", "r+", encoding="utf-8")
                current_song = f.read()

                aliases_commands = {'{music}': str(current_song)}

                message_data = utils.messages_file_load("command_current_confirm")
                message = utils.replace_all(message_data['response'], aliases)
                message = utils.replace_all(message,aliases_commands)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                command_data_player['atual']['last_use'] = current
        
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_player['next']['command']):

            command_info = command_data_player['next']

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                playlist_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/playlist.json", "load")
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/list_files/queue.json", "load")

                check_playlist = any(playlist_data.keys())
                check_queue = any(queue_data.keys())

                if check_queue:

                    queue_keys = [int(x) for x in queue_data.keys()]
                    min_key_queue = min(queue_keys)
                    min_key_queue_str = str(min_key_queue)

                    next_song = queue_data[min_key_queue_str]['MUSIC_NAME']
                    resquest_by = queue_data[min_key_queue_str]['USER']

                    aliases_commands = {
                        '{music}': str(next_song),
                        '{request_by}': str(resquest_by)
                    }

                    message_data = utils.messages_file_load("command_next_confirm")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message,aliases_commands)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                elif check_playlist:

                    playlist_keys = [int(x) for x in playlist_data.keys()]
                    min_key_playlist = min(playlist_keys)
                    min_key_playlist_str = str(min_key_playlist)

                    next_song = playlist_data[min_key_playlist_str]['MUSIC_NAME']
                    resquest_by = playlist_data[min_key_playlist_str]['USER']

                    aliases_commands = {
                        '{music}': str(next_song),
                        '{request_by}': str(resquest_by)
                    }

                    message_data = utils.messages_file_load("command_next_confirm")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message,aliases_commands)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = utils.messages_file_load("command_next_no_music")
                    message = utils.replace_all(message_data['response'], aliases)
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                            
                command_data_player['next']['last_use'] = current
        
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_queue["add_queue"]["command"]):
            
            command_info = command_data_queue["add_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    command, display_name = re.split(r'\s+', message_text, maxsplit=1)
            
                    queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")
                    queue_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json","load")
                    
                    user_found = userdatabase.get_user_data(display_name)
                    
                    if user_found:
                        
                        usercheck_userid  = user_found["userid"]
                        usercheck_display_name = user_found["display_name"]
                        usercheck_username = user_found["username"]
                        user_roles = user_found["roles"]

                        user_add = f"{usercheck_display_name} | {usercheck_username}"
                        
                        if user_add not in queue_data['normal'] or user_add not in queue_data['priority']:

                            if queue_config['spend_user_balance'] == 1:

                                cost = command_data_queue["self_add_queue"]["cost"]

                                check = userdatabase.check_cost(usercheck_userid, cost, 1)

                                if check:

                                    if queue_config['queue_prioriry_role_status']:

                                        priority_roles = queue_config['queue_prioriry_roles']

                                        priority_check = check_perm(user_roles,priority_roles)

                                        if priority_check:

                                            if queue_config['queue_prioriry']:

                                                queue_data['priority'].append(user_add)
                                                pos = queue_data['priority'].index(user_add)

                                            else:

                                                queue_data['normal'].insert(0,user_add)
                                                pos = queue_data['normal'].index(user_add)

                                        else:

                                            queue_data['normal'].append(user_add)
                                            pos = queue_data['normal'].index(user_add)

                                    else:
                                        queue_data['normal'].append(user_add)
                                        pos = queue_data['normal'].index(user_add)
                                    
                                    aliases_commands = {
                                        "{value}" : user_add,
                                        "{pos}": str(pos + 1)
                                    }
                
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                                    message_data = utils.messages_file_load("response_queue")
                                    message = utils.replace_all(message_data['response'], aliases)
                                    message = utils.replace_all(message,aliases_commands)

                                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                                    if main_window_open:
                                        main_window.evaluate_js(f"queue_js_get()")
                                    
                                else:

                                    message_data = utils.messages_file_load("balance_user_insuficient")
                                    message = utils.replace_all(message_data['response'], aliases)

                                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                            else:

                                if queue_config['queue_prioriry_role_status']:

                                    priority_roles = queue_config['queue_prioriry_roles']

                                    priority_check = check_perm(user_roles,priority_roles)

                                    if priority_check:

                                        if queue_config['queue_prioriry']:

                                            queue_data['priority'].append(user_add)
                                            pos = queue_data['priority'].index(user_add)

                                        else:

                                            queue_data['normal'].insert(0,user_add)
                                            pos = queue_data['normal'].index(user_add)

                                    else:

                                        queue_data['normal'].append(user_add)
                                        pos = queue_data['normal'].index(user_add)

                                else:

                                    queue_data['normal'].append(user_add)
                                    pos = queue_data['normal'].index(user_add)

                                aliases_comm = {
                                    "{value}" : user_add,
                                    "{pos}": str(pos + 1)
                                }
            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                                message_data = utils.messages_file_load("response_add_queue")
                                message = utils.replace_all(message_data['response'], aliases)
                                message = utils.replace_all(message, aliases_comm)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                                
                                if main_window_open:
                                    main_window.evaluate_js(f"queue_js_get()")

                        else:
                            
                            if user_add in queue_data['normal']:

                                pos = queue_data['normal'].index(user_add)

                            elif user_add in queue_data['priority']:

                                pos = queue_data['priority'].index(user_add)

                            aliases_comm = {
                                "{pos}": str(pos + 1)
                            }

                            message_data = utils.messages_file_load("response_namein_queue")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_comm)

                            notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

                            
                            if main_window_open:
                                main_window.evaluate_js(f"queue_js_get()")

                    else:

                        message_data = utils.messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                        
                    command_data_queue["add_queue"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_queue["self_add_queue"]["command"]):
            
            command_info = command_data_queue["self_add_queue"]
            
            queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

            queue_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json","load")

            user_add = f"{display_name} | {username}"
            
            if user_add not in queue_data['normal'] and user_add not in queue_data['priority']:

                current, message_error, status, type_error = check_status(command_info, aliases)

                if status:
                    
                    if queue_config['queue_prioriry_role_status']:

                        priority_roles = queue_config['queue_prioriry_roles']

                        priority_check = check_perm(user_roles,priority_roles)

                        if priority_check:

                            if queue_config['queue_prioriry']:

                                queue_data['priority'].append(user_add)
                                pos = queue_data['priority'].index(user_add)

                            else:

                                queue_data['normal'].insert(0,user_add)
                                pos = queue_data['normal'].index(user_add)

                        else:
                            queue_data['normal'].append(user_add)
                            pos = queue_data['normal'].index(user_add)

                    else:
                        queue_data['normal'].append(user_add)
                        pos = queue_data['normal'].index(user_add)


                    aliases_comm = {
                        "{pos}": str(pos + 1)
                    }
                    

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                    message_data = utils.messages_file_load("response_add_queue")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message, aliases_comm)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    

                    
                    if main_window_open:
                        main_window.evaluate_js(f"queue_js_get()")


                    command_data_queue["self_add_queue"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

                else:

                    if type_error == "level":

                        send_error_level(command_info)

                    else:
                        notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)
                    

            else:

                
                if user_add in queue_data['normal']:

                    pos = queue_data['normal'].index(user_add)

                elif user_add in queue_data['priority']:

                    pos = queue_data['priority'].index(user_add)

                aliases_comm = {
                    "{pos}": str(pos + 1)
                }

                message_data = utils.messages_file_load("response_namein_queue")
                message = utils.replace_all(message_data['response'], aliases)
                message = utils.replace_all(message, aliases_comm)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

        elif compare_strings(command, command_data_queue["check_queue"]["command"]):

            command_info = command_data_queue["check_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)
                    
            if status:
            
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

                message_data = utils.messages_file_load("response_get_queue")
                message = utils.replace_all(message_data['response'], aliases)

                match = re.search(r'\{queue-(\d*)\}', message)

                if match:

                    number = int(match.group(1))

                    queue_normal = [item.split(' | ')[0] for item in queue_data['normal']]

                    replacement = ', '.join(queue_normal[:number])

                    message = message.replace(match.group(0), replacement)



                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                

                command_data_queue["check_queue"]["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_queue["check_queue_p"]["command"]):

            command_info = command_data_queue["check_queue_p"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
            
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

                message_data = utils.messages_file_load("response_get_queue")
                message = utils.replace_all(message_data['response'], aliases)

                match = re.search(r'\{queue-(\d*)\}', message)

                if match:

                    number = int(match.group(1))

                    queue_pry = [item.split(' | ')[0] for item in queue_data['priority']]

                    replacement = ', '.join(queue_pry[:number])

                    message = message.replace(match.group(0), replacement)


                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                command_data_queue["check_queue_p"]["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}queue/commands.json","save",command_data_queue)

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_queue["rem_queue"]["command"]):

            command_info = command_data_queue["rem_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
         
                if sufix:

                    command, username = re.split(r'\s+', message_text, maxsplit=1)

                    user_found = userdatabase.get_user_data(username)

                    if user_found:

                        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")
                        
                        usercheck_display_name = user_found["display_name"]
                        usercheck_username = user_found["username"]

                        user_add = f"{usercheck_display_name} | {usercheck_username}"

                        if user_add in  queue_data['normal'] or user_add in queue_data['priority']:

                            if user_add in queue_data['normal']:

                                pos = queue_data['normal'].remove(user_add)

                            elif user_add in queue_data['priority']:

                                pos = queue_data['priority'].remove(user_add)

                            utils.manipulate_json( f"{utils.local_work('appdata_path')}/queue/queue.json","save", queue_data)

                            if main_window_open:
                                main_window.evaluate_js(f"queue_js_get()")
                                
                            message_data = utils.messages_file_load("response_rem_queue")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                        else:

                            message_data = utils.messages_file_load("response_noname_queue")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    command_data_queue["rem_queue"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_tts["command"]):

            command_info = command_data_tts

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    try:
                        
                        message_data = utils.messages_file_load("tts_prefix")
                        message_prefix = utils.replace_all(message_data['response'], aliases)

                        if command_info['prefix']:
                            sufix = f"{message_prefix} {sufix}"

                        user_input_short = textwrap.shorten(sufix, width=300, placeholder=" ")
                        tts = gTTS(text=user_input_short, lang="pt", slow=False)

                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)

                        rando = random.randint(1, 100000)

                        audio_path = f"{utils.local_work('appdata_path')}/temp/tts{rando}.mp3"
                        with open(audio_path, "wb") as f:
                            f.write(mp3_fp.read())


                        notification("tts",  0, 0, "", audio_path, 50, sufix)

                        command_data_tts["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/tts.json", "save", command_data_tts)

                    except Exception as e:
                        utils.error_log(f"{e}")

                else:

                    message_data = utils.messages_file_load("error_tts_no_text")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
         
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_champ["enter_camp"]["command"]):

            command_info = command_data_champ["enter_camp"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","load")
                
                user_add = f"{display_name} | {username}"
                
                if user_add not in champ_data['new_champ']:

                    champ_data['new_champ'].append(user_add)

                    message_data = utils.messages_file_load("response_add_champ")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)

                    if main_window_open:
                        main_window.evaluate_js(f"getMatchesLoad()")

                else:

                    message_data = utils.messages_file_load("response_in_champ")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/commands.json", "save", command_info)


            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_champ["add_camp"]["command"]):

            command_info = command_data_champ["add_camp"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    command, display_name = re.split(r'\s+', message_text, maxsplit=1)

                    user_found = userdatabase.get_user_data(display_name)
                    
                    if user_found:

                        champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","load")
                        
                        usercheck_userid  = user_found["userid"]
                        usercheck_display_name = user_found["display_name"]
                        usercheck_username = user_found["username"]

                        user_add = f"{usercheck_display_name} | {usercheck_username}"
                        
                        if user_add not in champ_data['new_champ']:

                            champ_data['new_champ'].append(user_add)

                            message_data = utils.messages_file_load("response_add_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)

                            if main_window_open:
                                main_window.evaluate_js(f"getMatchesLoad()")

                        else:

                            message_data = utils.messages_file_load("response_in_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                            
                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/commands.json", "save", command_info)

                    else:

                        message_data = utils.messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_champ["remove_camp"]["command"]):

            command_info = command_data_champ["remove_camp"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    command, display_name = re.split(r'\s+', message_text, maxsplit=1)

                    user_found = userdatabase.get_user_data(display_name)
                    
                    if user_found:

                        champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","load")
                        
                        usercheck_userid  = user_found["userid"]
                        usercheck_display_name = user_found["display_name"]
                        usercheck_username = user_found["username"]

                        user_add = f"{usercheck_display_name} | {usercheck_username}"
                        
                        if user_add in champ_data['new_champ']:

                            champ_data['new_champ'].remove(user_add)

                            message_data = utils.messages_file_load("response_remove_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)

                            if main_window_open:
                                main_window.evaluate_js(f"getMatchesLoad()")

                        else:

                            message_data = utils.messages_file_load("response_not_in_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                            
                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/commands.json", "save", command_info)

                    else:

                        message_data = utils.messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_votes["command"]):

            def getVoteKey(dict, vote):
                for key, value in dict.items():
                    if value["name"] == vote:
                        return key
                return None

            command_info = command_data_votes

            current, message_error, status, type_error = check_status(command_info, aliases)

            options = utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json","load")

            if status:
                
                if user not in options['voted']:

                    if options['status'] == "Voting":

                        if sufix:

                            keyfound = getVoteKey(options['options'], sufix)

                            if keyfound is not None:

                                option = options["options"][keyfound]
                                option["votes"] += 1
                                name = option["name"]

                                options['voted'].append(user)

                                aliases_commands = {
                                    "{name}" : name
                                }
                                
                                message_data = utils.messages_file_load("command_vote_voted")
                                message = utils.replace_all(message_data['response'], aliases)
                                message = utils.replace_all(message, aliases_commands)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json","save",options)


                                update_votes = utils.update_votes({"type_id" : "update_votes"})

                                data_goal = {
                                    'type': 'votes',
                                    'html': update_votes
                                }
                                    
                                if server.started:
                                    server.broadcast_message(json.dumps(data_goal))

                                command_data_votes["last_use"] = current

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/commands.json", "save", command_data_votes)

                                if main_window_open:
                                    main_window.evaluate_js(f"votes('get_options')")

                            else:
                                message_data = utils.messages_file_load("command_vote_notfound")
                                message = utils.replace_all(message_data['response'], aliases)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                        else:
                            message_data = utils.messages_file_load("command_sufix")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                    else:

                        message_data = utils.messages_file_load("command_vote_norun")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = utils.messages_file_load("command_vote_arvoted")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
  
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["user_balance"]["command"]):

            command_info = command_data_balance["user_balance"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                likes = user_data_load_db["likes"]
                gifts = user_data_load_db["gifts"]
                shares = user_data_load_db["shares"]
                points = user_data_load_db["points"]

                aliases_balance = {
                    "{likes}" : likes,
                    "{gifts}" : gifts,
                    "{shares}" : shares,
                    "{points}" : points,
                    "{rank}" : str(userdatabase.get_user_rank(user))
                }

                message_data = utils.messages_file_load("balance")
                message = utils.replace_all(message_data['response'], aliases)
                message = utils.replace_all(message, aliases_balance)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                command_data_tts["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")

        
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["mod_balance"]["command"]):

            command_info = command_data_balance["mod_balance"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    command, username = re.split(r'\s+', message_text, maxsplit=1)

                    user_found = userdatabase.get_user_data(username)

                    if user_found:

                        usercheck_username = user_found["display_name"]
                        likes = user_found["likes"]
                        gifts = user_found["gifts"]
                        shares = user_found["shares"]
                        points = user_found["points"]

                        aliases_balance = {
                            "{usercheck}" : usercheck_username,
                            "{likes}" : likes,
                            "{gifts}" : gifts,
                            "{shares}" : shares,
                            "{points}" : points,
                            "{rank}" : str(userdatabase.get_user_rank(user))
                        }

                        message_data = utils.messages_file_load("balance_moderator")
                        message = utils.replace_all(message_data['response'], aliases)
                        message = utils.replace_all(message, aliases_balance)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                        command_data_tts["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")

                    else:

                        message_data = utils.messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["mod_balance_give"]["command"]):

            command_info = command_data_balance["mod_balance_give"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                command, username, value = re.split(r'\s+', message_text, maxsplit=2)

                if value.isdigit():
                    
                    user_found = userdatabase.get_user_data(username)
                    
                    if user_found:

                        usercheck_id = user_found["userid"]
                        usercheck_username = user_found["display_name"]
                        likes = user_found["likes"]
                        gifts = user_found["gifts"]
                        shares = user_found["shares"]
                        points = user_found["points"]

                        userdatabase.give_balance(usercheck_id, value)

                        aliases_balance = {
                            "{usercheck}" : usercheck_username,
                            "{likes}" : likes,
                            "{gifts}" : gifts,
                            "{shares}" : shares,
                            "{points}" : points
                        }

                        message_data = utils.messages_file_load("balance_user_gived")
                        message = utils.replace_all(message_data['response'], aliases)
                        message = utils.replace_all(message, aliases_balance)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                        command_data_tts["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")

                    else:

                        message_data = utils.messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = utils.messages_file_load("command_root_sufix_number")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                                    
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["mod_balance_take"]["command"]):

            command_info = command_data_balance["mod_balance_take"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                command, username, value = re.split(r'\s+', message_text, maxsplit=2)

                if value.isdigit():
                    
                    user_found = userdatabase.get_user_data(username)

                    if user_found:
                        
                        usercheck_userid = user_found["userid"]
                        usercheck_username = user_found["display_name"]
                        likes = user_found["likes"]
                        gifts = user_found["gifts"]
                        shares = user_found["shares"]
                        points = user_found["points"]

                        check = userdatabase.check_cost(usercheck_userid, int(value), 1)

                        if check:

                            aliases_balance = {
                                "{usercheck}" : usercheck_username,
                                "{likes}" : likes,
                                "{gifts}" : gifts,
                                "{shares}" : shares,
                                "{points}" : points
                            }

                            message_data = utils.messages_file_load("balance_user_spended")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_balance)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            command_data_tts["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")

                        else:

                            message_data = utils.messages_file_load("balance_user_insuficient")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    else:

                        message_data = utils.messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)
                     
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = utils.messages_file_load("command_root_sufix_number")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

  
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_points"]["command"]):

            command_info = command_data_balance["top_points"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('points',10)

                names_and_points = [(user['display_name'], user['points']) for user in users]

                message_data = utils.messages_file_load("balance_top_points")

                top_n = extract_top_n_from_string(message_data['response'])

                if top_n is not None:

                    response = generate_top_users_string(names_and_points,f"{{top-{top_n}}}", 'Pontos') 

                    if not response == False:

                        aliases_command = {
                            f"{{top-{top_n}}}" : response
                        }

                        message_top = utils.replace_all(message_data['response'], aliases_command)
                        message = utils.replace_all(message_top, aliases)

                        notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                        command_data_tts["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")
      
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_likes"]["command"]):

            command_info = command_data_balance["top_likes"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('likes',10)

                names_and_points = [(user['display_name'], user['likes']) for user in users]

                message_data = utils.messages_file_load("balance_top_likes")

                top_n = extract_top_n_from_string(message_data['response'])

                if top_n is not None:

                    response = generate_top_users_string(names_and_points,f"{{top-{top_n}}}", 'Curtidas') 

                    if not response == False:

                        aliases_command = {
                            f"{{top-{top_n}}}" : response
                        }

                        message_top = utils.replace_all(message_data['response'], aliases_command)
                        message = utils.replace_all(message_top, aliases)

                        notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")
      
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_shares"]["command"]):

            command_info = command_data_balance["top_shares"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('shares',10)

                names_and_points = [(user['display_name'], user['shares']) for user in users]

                message_data = utils.messages_file_load("balance_top_shares")

                top_n = extract_top_n_from_string(message_data['response'])

                if top_n is not None:

                    response = generate_top_users_string(names_and_points,f"{{top-{top_n}}}", 'Compartilhamentos') 

                    if not response == False:

                        aliases_command = {
                            f"{{top-{top_n}}}" : response
                        }

                        message_top = utils.replace_all(message_data['response'], aliases_command)
                        message = utils.replace_all(message_top, aliases)

                        notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")
      
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_gifts"]["command"]):

            command_info = command_data_balance["top_gifts"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('gifts',10)

                names_and_points = [(user['display_name'], user['gifts']) for user in users]

                message_data = utils.messages_file_load("balance_top_gifts")

                top_n = extract_top_n_from_string(message_data['response'])

                if top_n is not None:

                    response = generate_top_users_string(names_and_points,f"{{top-{top_n}}}", 'Presentes') 

                    if not response == False:

                        aliases_command = {
                            f"{{top-{top_n}}}" : response
                        }

                        message_top = utils.replace_all(message_data['response'], aliases_command)
                        message = utils.replace_all(message_top, aliases)

                        notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/commands.json", command_data_balance, "save")
      
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_subathon["add_minutes"]["command"]):

            command_info = command_data_subathon["add_minutes"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                
                if sufix:

                    if sufix.isdigit():

                        value_int = int(sufix)

                        data_goal = {
                            'type': 'clock',
                            'action' : 'add',
                            'time': value_int
                        }
                            
                        if server.started:
                            server.broadcast_message(json.dumps(data_goal))

                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/commands.json", "save", command_data_subathon)

                        message_data = utils.messages_file_load("subathon_minutes_add")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = utils.messages_file_load("command_volume_number")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    
  
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_subathon["remove_minutes"]["command"]):

            command_info = command_data_subathon["remove_minutes"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                
                if sufix:

                    if sufix.isdigit():

                        value_int = int(sufix)

                        data_goal = {
                            'type': 'clock',
                            'action' : 'remove',
                            'time': value_int
                        }
                            
                        if server.started:
                            server.broadcast_message(json.dumps(data_goal))

                        command_data_subathon["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/commands.json", "save", command_data_subathon)

                        message_data = utils.messages_file_load("subathon_minutes_remove")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = utils.messages_file_load("command_volume_number")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    
  
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)
        
        elif compare_strings(command, command_data_subathon["clear_minutes"]["command"]):

            command_info = command_data_subathon["clear_minutes"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                
                if sufix:

                    data_goal = {
                        'type': 'clock',
                        'action' : 'reset',
                    }
                        
                    if server.started:
                        server.broadcast_message(json.dumps(data_goal))

                    command_data_subathon["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/commands.json", "save", command_data_subathon)

                    message_data = utils.messages_file_load("subathon_minutes_reset")
                    message = utils.replace_all(message_data['response'], aliases)
                    
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                else:

                    message_data = utils.messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    
  
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

    else:


        message_data = utils.messages_file_load("commands_disabled")
        message = utils.replace_all(message_data['response'], aliases)

        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


def on_resize(width, height):

    min_width = 1200
    min_height = 600

    if width < min_width or height < min_height:
        if main_window_open:
            main_window.resize(min_width, min_height)


def loaded():
    
    global loaded_status

    loaded_status = True

    authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

    username = authdata.USERNAME()

    if username == "":

        data = {"autenticated": "false"}

    else:

        data = {"autenticated": "true"}
        
        log_chat('start', None)

        loop = threading.Thread(target=loopcheck, args=(), daemon=True)
        loop.start()

        loop_r = threading.Thread(target=looprank, args=(), daemon=True)
        loop_r.start()

        loop_nt = threading.Thread(target=loop_notification, args=(), daemon=True)
        loop_nt.start()

        loop_ct = threading.Thread(target=loop_chat_slow, args=(), daemon=True)
        loop_ct.start()

    return json.dumps(data, ensure_ascii=False)


def update_ranking(type_id, limit):

    try:

        rank_data = userdatabase.get_all_users_rank(type_id, limit)

        if not rank_data == None:

            data = {
                "type_id": type_id,
                "info": rank_data,
            }

            data_goal = {
                "type": f"rank_{type_id}",
                "html": utils.update_ranks(data),
            }

            if server.started:
                server.broadcast_message(json.dumps(data_goal))

    except Exception as e:
        utils.error_log(e)


def looprank():

    global loaded_status

    rank_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "load")
    status_rank = rank_config['status']

    while loaded_status == True and userdatabase.is_connected:

        if status_rank == 1: 

            try:
                rank_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "load")

                status_rank = rank_config['status']
                max_users = rank_config['max_users']

                update_ranking("likes", int(max_users))
                update_ranking("shares", int(max_users))
                update_ranking("gifts", int(max_users))
                update_ranking("points", int(max_users))

                interval = int(rank_config['interval'])

                if interval < 10:
                    interval = 10

                time.sleep(interval)


            except Exception as e:
                utils.error_log(e)

                interval = int(rank_config['interval'])

                if interval < 10:
                    interval = 10

                time.sleep(interval)
        else:

            interval = int(rank_config['interval'])

            if interval < 10:
                interval = 10

            time.sleep(interval)


def update_goal(goal_type, ammount):
    
    try:

        goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

        total_list = ["total_follow", "total_share", "total_likes", "total_gifts", "total_diamonds", "total_specs"]

        if goal_type in total_list:

            if goal_type == "total_follow":

                follows = int(goal_data["follow"]["current"])
                total_follow = int(ammount) + follows
                goal_data["follow"]["current"] = total_follow

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_follow

            elif goal_type == "total_likes":

                goal_data["likes"]["current"] = int(ammount)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return True

            elif goal_type == "total_share":

                total_shares = int(goal_data["share"]["current"]) + int(ammount)
                goal_data["share"]["current"] = total_shares

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_shares
            
            elif goal_type == "total_diamonds":  

                total_diamonds = int(goal_data["diamonds"]["current"]) + int(ammount)
                goal_data["diamonds"]["current"] = int(total_diamonds)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_diamonds

            elif goal_type == "total_gifts":           

                total_gifts = int(goal_data["gift"]["current"]) + int(ammount)
                goal_data["gift"]["current"] = total_gifts

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_gifts
            
            elif goal_type == "total_specs":      


                if int(ammount) >= int(goal_data["max_viewer"]["current"]):

                    goal_data["max_viewer"]["current"] = int(ammount)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                    return int(ammount)
                
                else:
                    current = goal_data["max_viewer"]["current"]

                    return current

        elif goal_data[goal_type]["status"] == 1:

            if int(ammount) >= int(goal_data[goal_type]["goal"]):
                
                if goal_data[goal_type]["event"] == "double":
                    
                    goal = int(goal_data[goal_type]["goal"])

                    while not goal > ammount:
                        goal = int(goal_data[goal_type]["goal"]) * 2

                    goal_data[goal_type]["goal"] = goal

                elif goal_data[goal_type]["event"] == "add":
                    
                    goal = int(goal_data[goal_type]["goal"])

                    while not goal > ammount:
                        goal += int(goal_data[goal_type]["goal_after"])

                    goal_data[goal_type]["goal"] = goal

                elif goal_data[goal_type]["event"] == "multiply": 

                    goal = int(goal_data[goal_type]["goal"])

                    while not goal > ammount:
                        goal = int(goal_data[goal_type]["goal"]) * int(goal_data[goal_type]["goal_after"])

                    goal_data[goal_type]["goal"] = goal

                else:
                    
                    if int(ammount) >= int(goal_data[goal_type]["goal"]):
                        goal = int(goal_data[goal_type]["goal_after"])

                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","save",goal_data)

                message_data = utils.messages_file_load("goal_end")

                data_goal = {
                    "type": "update_goal",
                    "type_goal": goal_type,
                    "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
                }
                                
                send_discord_webhook({'type_id' : 'goal_end', 'target':f'{goal}' ,'current' : f'{ammount}', 'goal_type' : {goal_type}})

                aliases = {
                    "{current}" : ammount,
                    "{target}" : goal_data[goal_type]["goal"],
                    "{type}" : goal_type,
                }

                message = utils.replace_all(message_data['response'], aliases)
                audio = goal_data[goal_type]["sound_file"]
                volume = goal_data[goal_type]["sound_volume"]

                notification("goal_end", message_data["status"], message_data["status_s"], message, audio, volume, "")
                

                    
            else:

                goal = int(goal_data[goal_type]["goal"])

                data_goal = {
                    "type": "update_goal",
                    "type_goal": goal_type,
                    "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
                }

            server.broadcast_message(json.dumps(data_goal))
        
    except Exception as e:

        utils.error_log(e)


def update_roles(data):

    try:

        type_id = data["type_id"]
        user = data["userid"]

        result = userdatabase.get_user_data(user)

        if result:

            roles = result['roles']

            roles_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/roles_config.json", "load")
            points_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/points.json","load")

            if type_id == "likes":

                likes = int(data["likes"])

                user_likes = int(result['likes'])
                new_likes = user_likes + likes

                userdatabase.update_user_value('likes', new_likes,user)

                if "likes" not in roles and new_likes > int(roles_data["like-role"]):
                    roles.append("likes")

            elif type_id == "shares":

                user_shares = int(result['shares'])
                new_shares = user_shares + 1

                userdatabase.update_user_value('shares', new_shares, user)

                if "shares" not in roles and new_shares > int(roles_data["share-role"]):
                    roles.append("shares")

            elif type_id == "follow":

                if "follow" not in roles:

                    roles.append("follow")

                    points = float(result['points'])
                    points += float(points_data_load["follow"])

                    userdatabase.update_user_value('points', points, user)

            elif type_id == "gifts":

                gifts = int(data["gifts"])

                user_gifts = int(result['gifts'])
                new_gifts = user_gifts + gifts
                
                userdatabase.update_user_value('gifts', new_gifts, user)

                if "gifts" not in roles and new_gifts > int(roles_data["gift-role"]):
                    roles.append("gifts")

            elif type_id == "comment":

                role_mapping = ["follow","moderator","subscriber","spec"]

                for role in role_mapping:
                    if role in data:
                        if data[role] == True and role not in roles:
                            roles.append(role)
                        elif data[role] == False and role in roles:
                            roles.remove(role)
      
            userdatabase.update_user_value('roles', roles, user)

        return True

    except Exception as e:
        utils.error_log(e)
        return False


def update_points(data):

    points_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/balance/points.json","load")
    ttk_data_gifts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json", "load")

    try:


        type_id = data["type_id"]
        user = data["userid"]

        result = userdatabase.get_user_data(user)

        if result:

            user_points = float(result['points'])

            if type_id == "likes":
                likes = int(data["likes"])
                config_points = float(points_data_load["likes"])
                received_points = config_points * likes
                user_points += received_points

            elif type_id == "shares":
                config_points = float(points_data_load["shares"])
                user_points += config_points

            elif type_id == "follow":
                config_points = float(points_data_load["follow"])
                user_points += config_points

            elif type_id == "gifts":
                gifts = data["gifts"]
                gift_id = data["gift_id"]
                gits_data = ttk_data_gifts['gifts']
                gift_global_status = gits_data[gift_id]['points-global']

                if int(gift_global_status) == 1:
                    config_points = float(points_data_load["gifts"])
                else:
                    config_points = float(gits_data[gift_id]['points'])

                received_points = config_points * gifts
                user_points += received_points

            userdatabase.update_user_value('points', user_points, user)

    except Exception as e:
        utils.error_log(e)


def show_alert(data):

    config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_log_config.json","load")

    variableMappings = {
        "command": config_data["show-commands-alert"],
        "music" : config_data["show-music-alert"],
        "event": config_data["show-events-alert"],
        "follow": config_data["show-follow-alert"],
        "like": config_data["show-likes-alert"],
        "gift": config_data["show-gifts-alert"],
        "chest": config_data["show-chest-alert"],
        "share": config_data["show-share-alert"],
        "join": config_data["show-join-alert"],
        "goal_start": config_data["show-goal-start-alert"],
        "goal_end": config_data["show-goal-end-alert"]
    }

    if variableMappings[data["type"]]:

        data_update = {
            "img" : data['profile_pic'],
            "message" : data['message']
        }

        data_goal = {
            "type": "alert",
            "html": utils.update_alert(data_update)
        }

        server.broadcast_message(json.dumps(data_goal))


def log_chat(type_id, data):

    if type_id == "save":

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        if chat_data['chat-log-status'] == 1:

            chatlogsave = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chatlog.json", "load")

            date_now = str(datetime.now().date())

            if not date_now in chatlogsave:

                chatlogsave[date_now] = []

            else:

                chat_data = chatlogsave[date_now]
                chat_data.append(data)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chatlog.json", "save", chatlogsave)

    elif type_id == "start":

        chatlogdata = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chatlog.json", "load")
        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        date = datetime.now().date()

        max_days = chat_data['chat-log-days']

        if chatlogdata:

            chatlogdatacopy = chatlogdata.copy()

            keys_to_remove = []

            for key in chatlogdatacopy.keys():

                past_date = parse(key).date()
                date_now = date

                diff = date_now - past_date
                elapsed = diff.days

                if int(elapsed) > int(max_days):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del chatlogdatacopy[key]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chatlog.json", "save", chatlogdatacopy)

        chatlogdata = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chatlog.json", "load")
        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        if chatlogdata and chat_data['chat-log-status'] == 1:

            # Definindo uma variável de contagem

            total_items = 0
            selected_items = {}

            # Invertendo a ordem das chaves do dicionário
            for key in reversed(list(chatlogdata.keys())):
                
                # Invertendo a ordem dos subdicionários dentro de cada lista
                for data in reversed(chatlogdata[key]):

                    # Verificando se o limite de 20 itens foi atingido
                    if total_items >= 20:
                        break

                    selected_items[total_items] = data

                    # Incrementando a variável de contagem
                    total_items += 1

                # Verificando novamente se o limite de 20 itens foi atingido
                if total_items >= 20:
                    break

            selected_items = {k: selected_items[k] for k in reversed(selected_items)}

            for _, data_message in selected_items.items():

                if main_window_open:
                        main_window.evaluate_js(f"append_message({json.dumps(data_message, ensure_ascii=False)})")

                if window_chat_open:
                        window_chat.evaluate_js(f"append_message_out({json.dumps(data_message, ensure_ascii=False)})")

    elif type_id == "get":

        chatlogdata = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chatlog.json", "load")

        return  json.dumps(chatlogdata, ensure_ascii=False)


def on_connect(event):

    global conected

    event = utils.DictDot(event)

    new_room = event.room_id
    total_follows = event.followers
    new_gift_info = event.giftdata

    gift_data = json.loads(new_gift_info)

    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")
    room_id_store = goal_data['room']

    try:
        
        if room_id_store != new_room:

            if utils.update_dict_gifts(gift_data):

                goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

                goal_data['room'] = new_room

                goal_data["diamonds"]["current"] = 0
                goal_data["gift"]["current"] = 0
                goal_data["share"]["current"] = 0
                goal_data["max_viewer"]["current"] = 0
                goal_data["likes"]["current"] = 0
                goal_data["follow"]["current"] = int(total_follows)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","save",goal_data)
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",{"likes" : {}})
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","save",{"shares" : {}})
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save", [])

                message_data = utils.messages_file_load("event_ttk_connect")

                notification("event", message_data["status"], message_data["status_s"], message_data['response'], "", "", "")

                send_discord_webhook({"type_id": "live_start"})

                conected = True

            else:
                
                message_data = utils.messages_file_load(f"event_ttk_connect")

                notification("event", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

                conected = True
        else:
            conected = True

    except Exception as e:

        utils.error_log(e)


def on_disconnect(event):

    event = utils.DictDot(event)

    message_data = utils.messages_file_load("event_ttk_disconected")
    
    notification("live_end", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

    if main_window_open:
        main_window.evaluate_js(f"update_specs_tiktok('disconect')")

    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

    goal_data["max_viewer"]["max_specs"] = 0
    goal_data["diamonds"]["total_diamonds"] = 0
    goal_data["share"]["total_shares"] = 0
    goal_data["gift"]["total_gifts"] = 0

    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","save",goal_data)

    send_discord_webhook({"type_id": "live_end"})


def on_comment(event):

    event = utils.DictDot(event)

    username = event.username

    if conected or username == 'usuarioexemplo':

        try:

            display_name = event.nickname
            userid = event.userid
            username = event.username
            comment = event.comment
            follower = event.is_following
            moderator = event.is_moderator
            subscriber = event.is_subscriber     
            badges_list = event.badges_list
            top_gifter = event.is_top_gifter
            profilepic = event.profilePictureUrl

            if all((comment, username, userid, display_name)):

                chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")
                
                now = datetime.now()
                
                format = chat_data["time-format"]
                
                if chat_data["data-show"] == 1:
                    
                    if chat_data["type-data"] == "passed":
                        
                        chat_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                        
                    elif chat_data["type-data"] == "current":
                        
                        chat_time = now.strftime(format)

                else:

                    chat_time = ""

                badges = []

                if len(badges_list) > 0:

                    for badge in badges_list:
                        
                        first_url = None
                        
                        if badge['type'] == "image":

                            if "url" in badge:

                                first_url = badge['url']

                                badge_dict = {
                                    "label": '',
                                    "name": '',
                                    "first_url": first_url,
                                }

                                badges.append(badge_dict)
                        
                        elif "name" in badge:
                            
                            if badge['name'] == "Moderator":

                                badge_dict = {
                                    "label": '',
                                    "name": '',
                                    "first_url": "https://p16-webcast.tiktokcdn.com/webcast-va/moderater_badge_icon.png~tplv-obj.image",
                                }

                                badges.append(badge_dict)
                                
                            if badge['name'] == "New gifter":

                                if "url" in badge:
                                
                                    first_url = badge['url']

                                    badge_dict = {
                                        "label": '',
                                        "name": '',
                                        "first_url": first_url,
                                    }

                                    badges.append(badge_dict)

                if follower > 0:
                    follower = True

                data_res = {
                    "type_id" : "comment",
                    "userid": userid,
                    "username": username,
                    "display_name": display_name,
                    "message": comment,
                    "badges": badges,
                    "follow": follower,
                    "moderator": moderator,
                    "subscriber": subscriber,
                    "top_gifter": top_gifter,
                    "profile_pic" : profilepic,  
                    "font_size": chat_data["font-size"],
                    "chat_color_border": chat_data["chat-color-border"],
                    "chat_color_name": chat_data["chat-color-name"],
                    "chat_name_select": chat_data["chat-name-select"],
                    "chat_border_select": chat_data["chat-border-select"],
                    "show_user_picture": chat_data["show-user-picture"],
                    "chat_animation" : chat_data["chat-animation"],
                    "wrapp_message": chat_data["wrapp-message"],
                    "data_show": chat_data["data-show"],
                    "chat_time": chat_time,
                    "type_data": chat_data["type-data"],
                }

                userdatabase.add_user_database(data_res)
                update_roles(data_res)

                log_chat('save', data_res)

                append_message(data_res)

                commands_module(data_res)

        except Exception as e:
            
            utils.error_log(e)


def on_like(event):

    if conected:
            
        event = utils.DictDot(event)

        event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_not.json", "load")
        like_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","load")

        try:

            display_name = event.nickname
            userid = event.userid
            username = event.username
            likes_send = event.likes
            total_likes = event.total_likes
            follower = event.is_following
            moderator = event.is_moderator
            subscriber = event.is_subscriber    
            profilePictureUrl = event.profilePictureUrl
            
            
            like_list = like_data["likes"]
            
            if userid not in like_list:
                
                current_time = int(time.time())
                
                like_list[userid] = current_time
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)
                
                aliases = {
                    "{nickname}" : display_name,
                    "{username}": username,
                    "{likes}" : likes_send,
                    "{total_likes}" :total_likes
                }
                
                message_data = utils.messages_file_load("event_ttk_like")
                message = utils.replace_all(message_data['response'], aliases)

                data_append = {
                    "type": "like",
                    "message": message,
                    "user_input": "",
                    "profile_pic": profilePictureUrl
                }


                show_alert(data_append)

                send_discord_webhook({"type_id": "like", "username" : display_name, "likes_send" : likes_send, "total_likes" : total_likes})

                if event_config_data["ttk_like"]["sound"] == 1:
                    
                    audio_path = event_config_data["ttk_like"]["sound_loc"]
                    audio_volume = event_config_data["ttk_like"]["sound_volume"]

                    notification("like", message_data["status"],message_data["status_s"], message, audio_path, audio_volume, "")

                else:

                    notification("like", message_data["status"],message_data["status_s"], message, "", "", "")
                
            else:
                
                delay = event_config_data["ttk_like"]["delay"]

                last_like = like_list[userid]

                message_delay, check_time, current = utils.check_delay(delay, last_like)

                if check_time:
                    
                    like_list[userid] = current
                    
                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)

                    aliases = {
                        "{nickname}" : display_name,
                        "{username}": username,
                        "{likes}" : likes_send
                    }

                    message_data = utils.messages_file_load("event_ttk_like")
                    message = utils.replace_all(message_data['response'], aliases)

                    data_append = {
                        "type": "like",
                        "message": message,
                        "user_input": "",
                        "profile_pic": profilePictureUrl
                    }

                    show_alert(data_append)
                    send_discord_webhook({"type_id": "like", "username" : display_name, "likes_send" : likes_send, "total_likes" : total_likes})
                    
                    notification("like", message_data["status"],message_data["status_s"], message, "", "", "")

            data_user = {
                "type_id": "likes",
                "userid": userid,
                "username": username,
                "display_name": display_name,
                "follow": follower,
                "moderator": moderator,
                "subscriber": subscriber,
                "profile_pic": profilePictureUrl,
                "likes": likes_send
            }

            userdatabase.add_user_database(data_user)
            update_roles(data_user)
            update_points(data_user)

            return_likes = update_goal("total_likes", total_likes)

            if return_likes:

                update_goal("likes", total_likes)
                

        except Exception as e:
            utils.error_log(e)


def on_join(event):

    if conected:
        
        event = utils.DictDot(event)

        userid = event.userid
        username = event.username
        display_name = event.nickname
        profilePictureUrl = event.profilePictureUrl

        join_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","load")

        if userid != None:

            if userid not in join_list:
                
                join_list.append(userid)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save",join_list)
                
                aliases = {
                    "{nickname}" : display_name,
                    "{username}": username
                }

                message_data = utils.messages_file_load("event_ttk_join")
                message = utils.replace_all(message_data['response'], aliases)

                data_append = {
                    "type": "join",
                    "message": message,
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }
                
                show_alert(data_append)

                notification("join", message_data["status"],message_data["status_s"], message, "", "", "")


def on_gift(event):

    def time_mult(time_str, mult_val):

        time_obj = datetime.strptime(time_str, "%H:%M:%S")

        newtime = time_obj + timedelta(hours=time_obj.hour * (mult_val - 1),
                                            minutes=time_obj.minute * (mult_val - 1),
                                            seconds=time_obj.second * (mult_val - 1))

        result_str = newtime.strftime("%H:%M:%S")

        return result_str

    def send_gift_not(gift_id, gifts_data, global_status, global_audio, global_volume, aliases):
                
        message_data = utils.messages_file_load("event_ttk_gift")
        message = utils.replace_all(message_data['response'], aliases)

        if gift_id in gifts_data:
            
            if "audio" in gifts_data[gift_id].keys():

                audio = gifts_data[gift_id]["audio"]
                volume = gifts_data[gift_id]["volume"]
                status = gifts_data[gift_id]["status"]
            
                if status == 1:

                    notification("gift", message_data["status"],message_data["status_s"], message, audio, volume, "")

                elif global_status == 1:

                    notification("gift", message_data["status"],message_data["status_s"], message, global_audio, global_volume, "")
            else:

                if global_status == 1:
                    
                    notification("gift", message_data["status"],message_data["status_s"], message, global_audio, global_volume, "")

        else:

            if global_status == 1:

                notification("gift", message_data["status"],message_data["status_s"], message, global_audio, global_volume, "")

    def increase_subathon(gift_id, gifts_data, ammount, diamonds):
        
        config_data_subathon = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/config.json", "load")
        time_type = config_data_subathon['time_type']

        if config_data_subathon['status'] == 1:

            if gift_id in gifts_data:
                
                time = gifts_data[gift_id]['time']

                if time == "00:00:00":

                    time = config_data_subathon['global_minutes']

                else:

                    if time_type == "gift":
                        time = time_mult(time, int(ammount))

                    elif time_type == "diamond":
                        time = time_mult(time, int(diamonds))


                data = {
                    'type': 'clock',
                    'action' : 'add',
                    'time': time
                }
                
                if server.started:
                    server.broadcast_message(json.dumps(data))

                aliases = {
                    "{time}": time 
                }

                message_data = utils.messages_file_load("subathon_minutes_add")
                message = utils.replace_all(message_data['response'], aliases)
                
                notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

            else:

                time = config_data_subathon['global_minutes']

                if time_type == "gift":
                    time = time_mult(time, int(ammount))

                elif time_type == "diamond":
                    time = time_mult(time, int(diamonds))

                data = {
                    'type': 'clock',
                    'action' : 'add',
                    'time': time
                }
                
                if server.started:
                    server.broadcast_message(json.dumps(data))

                aliases = {
                    "{time}": time 
                }

                message_data = utils.messages_file_load("subathon_minutes_add")
                message = utils.replace_all(message_data['response'], aliases)
                
                notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

    def press_keys(gifts_data):

        try:

            keys = gifts_data[gift_id]["keys"]
            time_key = gifts_data[gift_id]["time_key"]

            keys_filter = [item for item in keys if item.lower() != 'none']

            string_resultante = '+'.join(keys_filter)
            
            if time_key > 0 or time_key != "":

                keyboard.press(string_resultante)

                time.sleep(time_key)

                keyboard.release(string_resultante)

            else:

                keyboard.press_and_release(string_resultante)

        except Exception as e:
            utils.error_log(e)


    if conected:
        
        event = utils.DictDot(event)

        ttk_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json","load")
        goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

        gifts_data = ttk_data["gifts"]
        
        userid = event.userid
        username = event.username
        display_name = event.nickname

        giftname_br = event.gift_name
        gift_id = str(event.giftId)
        gift_diamonds = event.gift_diamonds

        streakable = event.streakable
        streaking = event.streaking
        giftcount = event.giftcount
        follower = event.is_following
        moderator = event.is_moderator
        subscriber = event.is_subscriber  
        profilePictureUrl = event.profilePictureUrl

        global_audio = ttk_data["audio"]
        global_status = ttk_data["status"]
        global_volume = ttk_data["volume"]

        aliases = {
            "{nickname}" : display_name,
            "{username}": username,
            "{amount}": giftcount,
            "{giftname}": giftname_br,
            "{diamonds}": gift_diamonds,
            "{id}": gift_id,
        }

        try:

            if streakable and not streaking:

                if gift_id in gifts_data:
                    
                    if gifts_data[gift_id]["name_br"] != "":
                        giftname_br = gifts_data[gift_id]["name_br"]

                    data_discord = {
                        "type_id": "gift", 
                        "username" : display_name, 
                        "gifts_send" : giftcount, 
                        "gift_name" : giftname_br,
                        "diamonds": gift_diamonds
                    }

                    message_data = utils.messages_file_load("event_ttk_gift")
                    message = utils.replace_all(message_data['response'], aliases)

                    data_append = {
                        "type": "gift",
                        "message": message,
                        "user_input": "",
                        "profile_pic" : profilePictureUrl
                    }

                    if int(gift_id) == int(goal_data["gift"]["gift"]):
                        
                        return_gift = update_goal("total_gifts", giftcount)

                        if return_gift:

                            update_goal("gift", return_gift)

                    diamonds = int(gift_diamonds) * int(giftcount)
                    
                    return_diamonds = update_goal("total_diamonds", diamonds)

                    if return_diamonds:

                        update_goal("diamonds", return_diamonds)

                    data_user = {
                        "type_id": "gifts",
                        "userid": userid,
                        "username": username,
                        "display_name": display_name,
                        "follow": follower,
                        "moderator": moderator,
                        "subscriber": subscriber,
                        "profile_pic": profilePictureUrl,
                        "gifts": giftcount,
                        "gift_id" : gift_id,
                    }

                    userdatabase.add_user_database(data_user)

                    update_roles(data_user)
                    update_points(data_user)

                    send_discord_webhook(data_discord)
                    show_alert(data_append)

                    increase_subathon(gift_id, gifts_data, giftcount, diamonds)
                    send_gift_not(gift_id, gifts_data, global_status, global_audio, global_volume, aliases)

                    if gifts_data[gift_id]['key_status'] == 1:
                        
                        threading.Thread(target=press_keys, args=(gifts_data,), daemon=True).start()

                else:

                    diamonds = int(gift_diamonds) * int(giftcount)
                    
                    return_diamonds = update_goal("total_diamonds", diamonds)

                    if return_diamonds:

                        update_goal("diamonds", return_diamonds)

                    increase_subathon(gift_id, gifts_data, giftcount, diamonds)
                    send_gift_not(gift_id, gifts_data, global_status, global_audio, global_volume, aliases)

            elif not streakable:

                if gift_id in gifts_data:
                    
                    if gifts_data[gift_id]["name_br"] != "":
                        giftname_br = gifts_data[gift_id]["name_br"]
                
                    discord_data = {
                        "type_id": "gift", 
                        "username" : display_name, 
                        "gifts_send" : giftcount, 
                        "gift_name" : giftname_br,
                        "diamonds": gift_diamonds
                    }

                    message_data = utils.messages_file_load("event_ttk_gift")
                    message =  utils.replace_all(message_data['response'], aliases)

                    data_append = {
                        "type": "gift",
                        "message": message,
                        "user_input": "",
                        "profile_pic" : profilePictureUrl
                    }
                    
                    data_user = {
                        "type_id": "gifts",
                        "userid": userid,
                        "username": username,
                        "display_name": display_name,
                        "follow": follower,
                        "moderator": moderator,
                        "subscriber": subscriber,
                        "profile_pic": profilePictureUrl,
                        "gifts": giftcount,
                        "gift_id" : gift_id,
                    }

                    userdatabase.add_user_database(data_user)

                    if int(gift_id) == int(goal_data["gift"]["gift"]):
                        
                        return_gift = update_goal("total_gifts", giftcount)

                        if return_gift:

                            update_goal("gift", return_gift)

                    diamonds = int(gift_diamonds) * int(giftcount)
                    return_diamonds = update_goal("total_diamonds", diamonds)

                    if return_diamonds:
                        update_goal("diamonds", return_diamonds)

                    update_roles(data_user)
                    update_points(data_user)

                    send_discord_webhook(discord_data)
                    show_alert(data_append)

                    increase_subathon(gift_id, gifts_data, 1, gift_diamonds)

                    send_gift_not(gift_id, gifts_data, global_status, global_audio, global_volume, aliases)
                    
                    if gifts_data[gift_id]['key_status'] == 1:
                        
                        threading.Thread(target=press_keys, args=(gifts_data,), daemon=True).start()
                else:

                    diamonds = int(gift_diamonds) * int(giftcount)
                    return_diamonds = update_goal("total_diamonds", diamonds)

                    if return_diamonds:
                        update_goal("diamonds", return_diamonds)

                    increase_subathon(gift_id, gifts_data, 1, gift_diamonds)

                    send_gift_not(gift_id, gifts_data, global_status, global_audio, global_volume, aliases)

        except Exception as e:
            
            utils.error_log(e)


def on_follow(event):

    if conected:
        
        event = utils.DictDot(event)

        event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_not.json", "load")
        ttk_follows = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/follow.json","load")

        userid = event.userid
        username = event.username
        display_name = event.nickname
        follower = event.is_following
        moderator = event.is_moderator
        subscriber = event.is_subscriber  
        profilePictureUrl = event.profilePictureUrl

        try:
            
            if userid not in ttk_follows:

                data_user = {
                    "type_id": "follow",
                    "userid": userid,
                    "username": username,
                    "display_name": display_name,
                    "follow": follower,
                    "moderator": moderator,
                    "subscriber": subscriber,
                    "profile_pic": profilePictureUrl
                }

                userdatabase.add_user_database(data_user)

                ttk_follows.append(userid)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/follow.json","save",ttk_follows)

                aliases = {
                    "{nickname}" : display_name,
                    "{username}": username,
                }

                message_data = utils.messages_file_load("event_ttk_follow")
                message =  utils.replace_all(message_data['response'], aliases)
            
                data_append = {
                    "type": "follow",
                    "message": message,
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }

                update_roles(data_user)

                return_follow = update_goal("total_follow", int(1))

                if return_follow:
                    update_goal("follow", int(return_follow))

                show_alert(data_append)

                send_discord_webhook({"type_id": "follow", "username" : display_name})


                if event_config_data["ttk_follow"]["sound"] == 1:

                    audio_path = event_config_data["ttk_follow"]["sound_loc"]
                    audio_volume = event_config_data["ttk_follow"]["sound_volume"]

                    notification("follow", message_data["status"],message_data["status_s"], message, audio_path, audio_volume, "")

                else:
                    
                    notification("follow", message_data["status"],message_data["status_s"], message, "", "", "")

        except Exception as e:
            utils.error_log(e)


def on_share(event):

    if conected:
        
        event = utils.DictDot(event)

        try:
            
            userid = event.userid
            username = event.username
            display_name = event.nickname
            follower = event.is_following
            moderator = event.is_moderator
            subscriber = event.is_subscriber  
            profilePictureUrl = event.profilePictureUrl

            event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_not.json", "load")

            shares_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","load")
            shares_list = shares_data["shares"]

            aliases = {
                "{nickname}" : display_name,
                "{username}": username,
                "{user}" : userid
            }

            data_user = {
                "type_id": "shares",
                "userid": userid,
                "username": username,
                "display_name": display_name,
                "follow": follower,
                "moderator": moderator,
                "subscriber": subscriber,
                "profile_pic": profilePictureUrl,
            }

            userdatabase.add_user_database(data_user)

            def update_user_share(userid):

                data_roles = {
                    "type_id": "shares",
                    "username" : username, 
                    "userid": userid,
                    "profile_pic" : profilePictureUrl
                }

                update_roles(data_roles)
                update_points(data_roles)

                return_share = update_goal("total_share", 1)

                if return_share:
                    
                    update_goal("share", return_share)

            if userid not in shares_list:
                
                current_time = int(time.time())
                
                shares_list[userid] = current_time
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json", "save", shares_data)

                message_data = utils.messages_file_load("event_ttk_share")
                message =  utils.replace_all(message_data['response'], aliases)

                data_append = {
                    "type": "share",
                    "message": message,
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }
                
                show_alert(data_append)
                
                send_discord_webhook({"type_id": "share", "username" : username})

                if event_config_data["ttk_share"]["sound"] == 1:
                    
                    audio_path = event_config_data["ttk_share"]["sound_loc"]
                    audio_volume = event_config_data["ttk_share"]["sound_volume"]

                    notification("share", message_data["status"],message_data["status_s"], message, audio_path, audio_volume, "")

                else:
                    
                    notification("share", message_data["status"],message_data["status_s"], message, "", "", "")
                    
            
            else:

                message_delay, check_time, current = utils.check_delay(event_config_data["ttk_share"]["delay"], shares_list[userid])

                if check_time:
                    
                    shares_list[userid] = current
                    
                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","save", shares_data)

                    message_data = utils.messages_file_load("event_ttk_share")
                    message =  utils.replace_all(message_data['response'], aliases)

                    data_append = {
                        "type": "share",
                        "message":  message,
                        "user_input": "",
                        "profile_pic" : profilePictureUrl
                    }
                    
                    notification("share", message_data["status"],message_data["status_s"], message,  "", "", "")

                    show_alert(data_append)

                    send_discord_webhook({"type_id": "share", "username" : username})

            update_user_share(userid)
                    
        except Exception as e:
            utils.error_log(e)


def on_viewer_update(event):

    if conected:

        event = utils.DictDot(event)
        
        viewer_count = event.viewer_count
        user_info = event.top_viewer

        user_info = utils.DictDot(user_info)
        
        try:

            if viewer_count != None and int(viewer_count) > 1:
                    
                return_specs = update_goal("total_specs", int(viewer_count))

                if return_specs:

                    update_goal("max_viewer", return_specs)

                if user_info != None:

                    nickname = user_info.nickname
                    profilePictureUrl = user_info.profilePictureUrl
                    topGifterRank = user_info.topGifterRank
                    coinCount = user_info.coinCount

                    user_info = {
                        "rank": topGifterRank,
                        "user": nickname,
                        "avatar": profilePictureUrl,
                        "diamonds": coinCount,
                    }

                    data_dump = json.dumps(user_info, ensure_ascii=False)

                    if main_window_open:
                        main_window.evaluate_js(f"update_carousel_tiktok('update_topspecs',{data_dump})")

            if main_window_open:
                main_window.evaluate_js(f"update_specs_tiktok({int(viewer_count)})")

        except Exception as e:
            utils.error_log(e)


def on_envelope(event):

    if conected:

        try:  
            
            event = utils.DictDot(event)

            userid = event.userid
            coinCount = event.coinCount

            if userid != None or userid != "None":

                userinfo = userdatabase.get_user_data(userid)

                if userinfo:

                    username = userinfo['username']
                    nickname = userinfo['display_name']

                    aliases = {
                        "{nickname}" : nickname,
                        "{username}": username,
                        "{coins}" : coinCount
                    }

                    message_data = utils.messages_file_load("event_ttk_envelope")
                    message =  utils.replace_all(message_data['response'], aliases)

                    data_append = {
                        "type": "chest",
                        "message": message,
                        "user_input": "",
                    }

                    message = data_append["message"]

                    notification("chest", message_data["status"],message_data["status_s"], message,  "", "", "")
                    
                    send_discord_webhook({"type_id": "envelope", "username" : nickname})

        except Exception as e:
            utils.error_log(e)


def on_error(event):

    if conected:

        try: 
            event = utils.DictDot(event)

            message = f"Erro : {event.message}"

            notification("event", 1, 1, message, "", "", "")
            

        except Exception as e:
            utils.error_log(e)


def test_fun(data):

    data = json.loads(data)

    type_id = data["type_id"]

    if type_id == "comment":

        comment = data["comment"]

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'comment': comment,
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'badges_list': [],
            'is_top_gifter': False,
            'profilePictureUrl': './icon.ico'
        }

        on_comment(event)
    
    elif type_id == "goal":

        type_goal = data["type_goal"]

        if type_goal == "likes":

            total_likes = 15

            return_likes = update_goal("total_likes", total_likes)

            if return_likes:

                update_goal("likes", total_likes)

        elif type_goal == "share":
            
            return_share = update_goal("total_share", 1)

            if return_share:
                
                update_goal("share", return_share)

        elif type_goal == "follow":
                            
            return_follow = update_goal("total_follow", 1)

            if return_follow:
                update_goal("follow", int(return_follow))

        elif type_goal == "diamonds":
            
            gift_diamonds = 10
            giftcount = 5

            diamonds = int(gift_diamonds) * int(giftcount)
            
            return_diamonds = update_goal("total_diamonds", diamonds)

            if return_diamonds:

                update_goal("diamonds", return_diamonds)
                
        elif type_goal == "gift":

            gift_id = data["gift_id"]
            giftcount = 1

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")


            if int(gift_id) == int(goal_data["gift"]["gift"]):
                
                return_gift = update_goal("total_gifts", giftcount)

                if return_gift:

                    update_goal("gift", return_gift)

        elif type_goal == "max_viewer":

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            current = goal_data["max_viewer"]["current"]

            current += 1
        
            return_specs = update_goal("total_specs", int(current))

            if return_specs:

                update_goal("max_viewer", return_specs)


def start_webview(app_mode):
    
    global main_window, main_window_open, window_chat, window_events, window_chat_open

    debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")


    def set_window_chat_open():
        
        global window_chat_open

        window_chat_open = True

    def set_window_chat_close():
        
        global window_chat_open

        window_chat_open = False

    def set_window_events_open():
        
        global window_events_open

        window_events_open = True

    def set_window_events_close():
        
        global window_events_open

        window_events_open = False

    def set_main_window_open():

        global main_window_open

        main_window_open = True


    if app_mode == "main":
        
        main_window = webview.create_window("VibesBot",f"{utils.local_work('datadir')}/web/index.html",width=1200,height=680,min_size=(1200, 680))
    
        main_window.events.loaded += set_main_window_open
        main_window.events.closed += close
        main_window.events.resized += on_resize

        main_window.expose(
            test_fun,
            loaded,
            chat_config,
            points_config,
            roles_config,
            subathon,
            open_py,
            update_check,
            sr_config_py,
            playlist_py,
            get_video_info,
            disclosure_py,
            discord_config,
            responses_config,
            messages_config,
            not_config_py,
            queue,
            giveaway_py,
            commands_py,
            select_file_py,
            event_log,
            logout_auth,
            start_webview,
            tiktok_gift,
            tiktok_goal,
            tiktok_alerts,
            tiktok_logs,
            tiktok_auth,
            tts_command,
            userdata_py,
            balance_command,
            ranks_config,
            log_chat,
            camp_command,
            votes,
            highlighted
        )

        webview.start(storage_path=utils.local_work("datadir"),private_mode=True,debug=bool(debug_data["debug"]),http_server=True,http_port=7000)

    elif app_mode == "chat":
        
        window_chat = webview.create_window("VibesBot Chat", "")
        window_chat.load_url("http://localhost:7000/chat.html")
        window_chat.events.loaded += set_window_chat_open
        window_chat.events.closed += set_window_chat_close

        window_chat.expose(
            open_py,
            userdata_py
        )

    elif app_mode == "events":
        
        window_events = webview.create_window("VibesBot Eventos", "")
        window_events.load_url("http://localhost:7000/events.html")

        window_events.events.loaded += set_window_events_open
        window_events.events.closed += set_window_events_close

        window_events.expose(event_log)


def close():

    global loaded_status, server, conected
    
    loaded_status = False
    conected = False

    if window_chat_open:
        window_chat.destroy()

    if window_events_open:
        window_events.destroy()


    if wsclient:
        
        wsclient.send(json.dumps({'type': 'Close','message' : 'Close'}, ensure_ascii=False))

        wsclient.close()

    if server:
        
        server.close_servers()

    userdatabase.close()

    sys.exit(0)


def close_auth():

    global loaded_status
    
    loaded_status = False
    
    if window_chat_open:
        window_chat.destroy()

    if window_events_open:
        window_events.destroy()

    if main_window_open:
        main_window.destroy()
    
    sys.exit(0)


def logout_auth():
    
    data = {"USERNAME": "", "SESSIONID": ""}

    utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json","save",data)

    close_auth()


def start_websocket_CS():

    global wsclient, server
    
    listener_callbacks = {
        "comment_event": on_comment,
        "connect_event": on_connect,
        "like_event": on_like,
        "join_event": on_join,
        "gift_event": on_gift,
        "follow_event": on_follow,
        "share_event": on_share,
        "viewer_event": on_viewer_update,
        "envelope_event": on_envelope,
        "error_event" : on_error
    }

    server = WebSocketServer('localhost', 7688)
    server.run()

    wsclient = WebSocketClient(callback_list=listener_callbacks,server_url='ws://127.0.0.1:7788')
    wsclient.run()


def start_node():

    try:

        flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

        if utils.check_local_work():
            command = 'VibesJS\\vibes.exe'
        else:
            command = 'node dist\\VibesJS\\vibes.js'

        subprocess.Popen(command, creationflags=flags)

    except Exception as e:
        
        utils.error_log(e)


def start_main():

    global userdatabase, commanddatabase, eventlogdatabase

    def start_log():

        eventlogdatabase.clean_up_events()

        join_list = []
        like_data = {"likes": {}}

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save",join_list)
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)

        data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "load")

        if not "error_status" in data:
            data["error_status"] = True

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/auth/auth.json", "save", data)

    def check_state_user():

        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")

        if debug_data['version'] != curr_version and debug_data['updated'] == "False":

            username = authdata.USERNAME()
            send_discord_webhook_auth(F"Atualização {curr_version}", username)

            debug_data['version'] = curr_version
            debug_data['updated'] = "True"

            print(debug_data)
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json", "save", debug_data)

    if utils.compare_and_insert_keys():

        check_state_user()

        userdatabase = UserDatabaseManager()
        commanddatabase = CommandDatabaseManager()
        eventlogdatabase = EventLogManager()

        commands_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/commands/commands.json","load")

        commanddatabase.import_commands_from_json(commands_data)

        pygame.init()
        pygame.mixer.init()

        start_log()
        start_node()
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        username = authdata.USERNAME()

        if username != "":

            start_websocket_CS()

        if getattr(sys, "frozen", False):
            utils.splash_close()

        start_webview("main")


if lock_manager.already_running:

    error_message = "O programa já está em execução, aguarde."
    messagebox.showerror("Erro", error_message)

else:

    start_main()