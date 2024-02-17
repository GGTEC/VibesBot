# -*- coding: utf-8 -*-
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
import shutil

from datetime import datetime, timedelta

from database import CommandDatabaseManager, EventLogManager, UserDatabaseManager, ChatLogManager, GiftsManager, ResponsesManager, GoalManager
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

global caching, loaded_status, main_window, main_window_open, window_chat_open, window_chat, window_events, window_events_open, wsclient, server, conected, userdatabase, commanddatabase, eventlogdatabase, chatlogmanager, giftsdatabase, responsesdatabase, goaldatabase

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

giftsdatabase = None
userdatabase = None
commanddatabase = None
eventlogdatabase = None
chatlogmanager = None
responsesdatabase = None
goaldatabase = None

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
    
    if not not_data in data_list:

        data_list.append(not_data)


def play_audio(audio, volume):

    if os.path.exists(audio):

        playing = pygame.mixer.music.get_busy()

        convert_vol = int(volume) / 100

        while playing:
            playing = pygame.mixer.music.get_busy()
            time.sleep(2)
    
        pygame.mixer.music.load(audio)
        pygame.mixer.music.set_volume(convert_vol)
        pygame.mixer.music.play()

    else:

        utils.error_log(f"Diretorio não encontrado {audio}")


def loop_notification():

    while loaded_status == True:

        try:

            if data_list != None:
                
                if len(data_list) > 0:

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

                        if os.path.exists(audio):

                            if audio.endswith(".mp4") or audio.endswith('.gif'):

                                try:

                                    if audio.endswith(".mp4"):

                                        path_dest_tx = f"{utils.local_work('datadir')}/web/src/videofiles"
                                        path_dest = os.path.join(path_dest_tx, "video.mp4")
                                        path = f"../../videofiles/video.mp4"


                                    if audio.endswith('.gif'):

                                        path_dest_tx = f"{utils.local_work('datadir')}/web/src/videofiles"
                                        path_dest = os.path.join(path_dest_tx, "gif.gif")
                                        path = f"../../videofiles/gif.gif"

                                    shutil.copy2(audio, path_dest)

                                    data_send = {
                                        "type" : "command",
                                        "profile_pic" : path,
                                        "message" : message,
                                        "duration": volume
                                    }

                                    threading.Thread(target=show_alert, args=(data_send,), daemon=True).start()

                                except Exception as e:
                                    utils.error_log(e)


                            else:
                                
                                threading.Thread(target=play_audio, args=(audio, volume,), daemon=True).start()
                    
                        else:

                            utils.error_log(f"Diretorio não encontrado {audio}")

                            data_list.remove(data)

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
        
        
        threading.Thread(target=eventlogdatabase.add_event, args=(new_event,), daemon=True).start()

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
            ("gif files", "*.gif"),
            ("video files", "*.mp4"),
            ("All files", "*.*"),
        )

    elif type_id == "image":
        filetypes = (("png files", "*.png"))

    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)

    folder = fd.askopenfilename(
        initialdir=f"{utils.local_work('appdata_path')}",
        filetypes=filetypes,
    )

    root.destroy()

    return folder


def commands_default_py(data):

    if isinstance(data, str):
        data = json.loads(data)

    type_rec = data["type_id"]

    if type_rec == "get_command":

        type_command_table = data["type_command_table"]
        type_command = data["type_command"]

        command_data = commanddatabase.get_default_command(type_command, type_command_table)

        return command_data
    
    if type_rec == "save_command":

        type_command = data["type_command"]
        type_command_table = data["type_command_table"]

        if commanddatabase.save_default_command(data, type_command_table):

            toast("success")

        else:

            toast("error")


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

            command_data_giveaway = commanddatabase.get_default_command_info('giveaway')
            command_data_player = commanddatabase.get_default_command_info('player')
            command_data_queue = commanddatabase.get_default_command_info('queue')
            command_data_tts = commanddatabase.get_default_command_info('queue')
            command_data_balance = commanddatabase.get_default_command_info('balance')
            command_data_champ = commanddatabase.get_default_command_info('champ')
            command_data_votes = commanddatabase.get_default_command_info('votes')
            command_data_subathon = commanddatabase.get_default_command_info('subathon')

            commands = commanddatabase.get_all_command_data()

            data = {
                "commands": [commands],
                "commands_queue": [command_data_queue],
                "commands_giveaway": [command_data_giveaway],
                "commands_player": [command_data_player],
                "commands_tts": [command_data_tts],
                "commands_balance": [command_data_balance],
                "commands_champ": [command_data_champ],
                "commands_votes": [command_data_votes],
                "commands_subathon": [command_data_subathon]
            }
            
            return json.dumps(data, ensure_ascii=False)
            
        except Exception as e:
            utils.error_log(e)

    elif type_rec == "add_blacklist":
        
        try:

            commanddatabase.add_to_blacklist(data["command"], data['user'])
            
            toast("Nome adicionado na blacklist")
            
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao adicionar o nome na blacklist")

    elif type_rec == "add_whitelist":

        try:

            commanddatabase.add_to_whitelist(data["command"], data['user'])
            
            toast("Nome adicionado na whitelist")
            
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao adicionar o nome na whitelist")

    elif type_rec == "remove_blacklist":
    
        try:

            commanddatabase.remove_from_blacklist(data["command"], data['user'])

            response = commanddatabase.get_blacklist(data["command"])

            toast("Nome removido da blacklist")

            return response
        
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao remover o nome da blacklist")

    elif type_rec == "remove_whitelist":

        try:

            commanddatabase.remove_from_whitelist(data["command"], data['user'])
            
            response = commanddatabase.get_whitelist(data["command"])

            toast("Nome removido da whitelist")

            return response
        
        except Exception as e:
            
            utils.error_log(e)

            toast("Erro ao remover o nome da whitelist")

    elif type_rec == "get_blacklist":
            
        try:

            response = commanddatabase.get_blacklist(data["command"])

            return response
        
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao obter a blacklist")
        
    elif type_rec == "get_whitelist":

        try:

            response = commanddatabase.get_whitelist(data["command"])

            return response
        
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao obter a whitelist")

    elif type_rec == "add_blacklistDefault":
        
        try:

            commanddatabase.add_to_blacklistDefault(data["command_table"], data["command_type"], data['user'])
            
            toast("Nome adicionado na blacklist")
            
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao adicionar o nome na blacklist")

    elif type_rec == "add_whitelistDefault":

        try:

            commanddatabase.add_to_whitelistDefault(data["command_table"], data["command_type"], data['user'])
            
            toast("Nome adicionado na whitelist")
            
        except Exception as e:

            utils.error_log(e)
            toast("Erro ao adicionar o nome na whitelist")

    elif type_rec == "remove_blacklistDefault":
    
        try:

            commanddatabase.remove_from_blacklistDefault(data["command_table"], data["command_type"], data['user'])

            response = commanddatabase.get_blacklistDefault(data["command_table"], data["command_type"])

            toast("Nome removido da blacklist")

            return response
        
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao remover o nome da blacklist")

    elif type_rec == "remove_whitelistDefault":

        try:

            commanddatabase.remove_from_whitelistDefault(data["command_table"], data["command_type"], data['user'])
            
            response = commanddatabase.get_whitelistDefault(data["command_table"], data["command_type"])

            toast("Nome removido da whitelist")

            return response
        
        except Exception as e:
            
            utils.error_log(e)

            toast("Erro ao remover o nome da whitelist")

    elif type_rec == "get_blacklistDefault":
            
        try:

            response = commanddatabase.get_blacklistDefault(data["command_table"], data["command_type"])

            return response
        
        except Exception as e:

            utils.error_log(e)
            toast("Erro ao obter a blacklist")
        
    elif type_rec == "get_whitelistDefault":

        try:

            response = commanddatabase.get_whitelistDefault(data["command_table"], data["command_type"])

            return response
        
        except Exception as e:
            utils.error_log(e)
            toast("Erro ao obter a whitelist")


def tts_command(data_receive):
    
    data = json.loads(data_receive)

    type_id = data["type_id"]

    tts_json_path = (f"{utils.local_work('appdata_path')}/config/tts.json")

    if type_id == "get_config":
        
        tts_command_data = utils.manipulate_json(tts_json_path, "load")

        blacklist_filter = ', '.join(tts_command_data["blacklist_words"])

        data = {
            "prefix": tts_command_data["prefix"],
            "emojis_filter" : tts_command_data["emojis_filter"],
            "words_filter" : tts_command_data["words_filter"],
            "letters_filter" : tts_command_data["letters_filter"],
            "blacklist_filter" : blacklist_filter
        }

        return data

    elif type_id == "save_config":
        
        try:

            tts_command_data = utils.manipulate_json(tts_json_path, "load")

            blacklistFilter = data["blacklistFilter"]

            blacklistFilter = blacklistFilter.replace(" ", "")
            blacklistFilter = blacklistFilter.split(',')

            tts_command_data["prefix"] = data["prefix"]
            tts_command_data["emojis_filter"] = data["emojisFilter"]
            tts_command_data["words_filter"] = data["wordsFilter"]
            tts_command_data["letters_filter"] = data["lettersFilter"]
            tts_command_data["blacklist_words"] = blacklistFilter

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

                        endcamp_list = champ_data_part['end_camp'][0]

                        endcamp_list['third'] = winner_of_third_match
        
                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data_part)
                
                else:

                    winner = match['winner']

                    champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                    if winner not in champ_data['winners']:

                        champ_data['winners'].append(winner)

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data)
                        
                        aliases = {"{winner}": str(winner)}

                        message_data = messages_file_load("response_add_winner")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")
                
            else:

                winner = match['winner']

                champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")

                if winner not in champ_data['winners']:

                    champ_data['winners'].append(winner)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "save", champ_data)

                    aliases = {"{winner}": str(winner)}

                    message_data = messages_file_load("response_add_winner")
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

        if type_id == "get_matches":

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

            message_data = messages_file_load("response_end_champ")

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

            message_data = messages_file_load("response_end_champ")

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

                
                champ_data =  utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json", "load")
            
                part = champ_data['new_champ']

                data_dump = json.dumps(part, ensure_ascii=False)

                return data_dump
                    
            except Exception as e:
                utils.error_log(e)
                toast("Ocorreu um erro ao adicionar o usuário.")


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

    message_data = messages_file_load("giveaway_response_win")
    message = utils.replace_all(message_data['response'], aliases)

    notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

    toast(f"{nickname} Ganhou o sorteio!")


def giveaway_py(type_id, data_receive):

    giveaway_config_path = f"{utils.local_work('appdata_path')}/giveaway/config.json"
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

                message_data = messages_file_load("giveaway_status_disable")
                message = utils.replace_all(message_data['reponse'], aliases)

                toast(message)

                notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

            elif giveaway_data["enable"] == 0 and data["giveaway_enable"] == 1:

                aliases = {
                    "{giveaway_name}": giveaway_data["name"],
                }

                message_data = messages_file_load("giveaway_status_enable")
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

    elif type_id == "add_user":
        
        if isinstance(data_receive, dict):

            data = data_receive

        else:

            data = json.loads(data_receive)

        new_name = data["new_name"]

        if new_name == "":

            toast("Você deve inserir um nome para adicionar")

            return
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

                message_data = messages_file_load("giveaway_response_user_add")
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

                        message_data = messages_file_load("giveaway_response_mult_add")
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

                message_data = messages_file_load("giveaway_status_disabled")
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
            
            if len(giveaway_name_data) != 0:

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


                message_data = messages_file_load("giveaway_response_win")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

                toast(f"{nickname} Ganhou o sorteio!")

            else:

                message_data = messages_file_load("response_giveaway_nonames")

                notification("event", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

                toast(f"Nenhum nome na lista do sorteio")

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

    def check_name_queue(dict, name):

        for list_queue in dict.values():

            if name in list_queue:
                return True
            
        return False

    def add_name_queue(type_dict, name, limit):

        if len(list(type_dict.keys())) > 0:

            last_match_name = list(type_dict.keys())[-1]
            last_match_quant = len(type_dict[last_match_name])
            
            last_match_number = last_match_name.split()[1]

            if last_match_quant < int(limit):

                type_dict[last_match_name].append(name)

            else:

                new_match_number = int(last_match_number) + 1
                new_match = f"Partida {new_match_number}"

                type_dict[new_match] = [name]

        else:

            new_match = f"Partida 1"
            
            type_dict[new_match] = [name]
        
        return type_dict

    def find_queue(dict, name):
        
        for key, list in dict.items():

            if name in list:

                return list, key 
            
        return None

    def add_name_removed(temporary_names, limit_per_list):

        result_dict = {}

        for name_to_add in temporary_names:

            for key, current_list in result_dict.items():

                if len(current_list) < limit_per_list:

                    current_list.append(name_to_add)

                    break
            else:

                new_key = f'Partida {len(result_dict) + 1}'
                result_dict[new_key] = [name_to_add]

        return result_dict

    def remove_name(input_dict, name, limit):

        temporary_names = []

        for key, current_list in input_dict.items():

            if name in current_list:

                for name_in_list in current_list:

                    temporary_names.append(name_in_list)

                temporary_names.remove(name)

            else:
                for name_in_list in current_list:

                    temporary_names.append(name_in_list)

        dict_name_removed = add_name_removed(temporary_names, limit)

        return dict_name_removed

    def move_name(dictionary, source_match_name, destination_match_name, name_to_move):


        if source_match_name not in dictionary or destination_match_name not in dictionary:
            return

        source_list = dictionary[source_match_name]
        destination_list = dictionary[destination_match_name]

        if name_to_move not in source_list:
            return

        source_list.remove(name_to_move)
        destination_list.append(name_to_move)

        return dictionary

    json_path =f"{utils.local_work('appdata_path')}/queue/queue.json"

    if type_id == "get_config":
        
        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        data = {
            "roles_queue": queue_config_data["queue_prioriry_roles"],
            "roles_status": queue_config_data["queue_prioriry_role_status"],
            "roles_pri" : queue_config_data["queue_prioriry"],
            "spend_user": queue_config_data["spend_user"],
            "limit" : queue_config_data["limit"]
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save_config":

        try:

            queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

            queue_config_data["queue_prioriry_roles"] = data_receive["roles_queue"]
            queue_config_data["queue_prioriry_role_status"] = data_receive["role_status"]
            queue_config_data["queue_prioriry"] = data_receive["roles_pri"]
            queue_config_data["spend_user"] = data_receive["spend_user"]
            queue_config_data["limit"] = data_receive["limit"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "save", queue_config_data)

            toast('Salvo')

        except Exception as e:

            toast('error')
            utils.error_log(e)

    elif type_id == "get_queue":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "get_ended":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        data = {
            "queue_ended": queue_data['ended']
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "queue_add":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        if data_receive:

            if not check_name_queue(queue_data['normal'], data_receive):

                queue_data['normal'] = add_name_queue(queue_data['normal'], data_receive, queue_config_data['limit'])
                list_players, pos = find_queue(queue_data['normal'], data_receive)

                users_in_part = ",".join(list_players)

                utils.manipulate_json(json_path, "save", queue_data)

                aliases = {
                    "{value}": str(data_receive),
                    "{match}" : str(pos),
                    "{players}" : users_in_part
                }

                message_data = messages_file_load("response_add_queue")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            else:

                aliases = {"{value}": str(data_receive)}

                message_data = messages_file_load("response_namein_queue")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            queue_data = utils.manipulate_json(json_path, "load")

        else:
            toast("Você deve inserir um nome para adicionar")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "queue_rem":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        if check_name_queue(queue_data['normal'], data_receive):

            queue_data['normal'] = remove_name(queue_data['normal'], data_receive, int(queue_config_data['limit']))

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {
                "{value}": str(data_receive),
                "{queue_type}" : "Comum"
            }
            message_data = messages_file_load("response_rem_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {
                "{value}": str(data_receive),
                "{queue_type}" : "Comum"
            }

            message_data = messages_file_load("response_noname_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "queue_rem_priority":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        if check_name_queue(queue_data['priority'], data_receive):

            queue_data['priority'] = remove_name(queue_data['priority'], data_receive, int(queue_config_data['limit']))

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {
                "{value}": str(data_receive),
                "{queue_type}" : "Comum"
                }
            message_data = messages_file_load("response_rem_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {"{value}": str(data_receive)}
            message_data = messages_file_load("response_noname_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "clear_queue":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        queue_data['normal'] = {}

        utils.manipulate_json(json_path, "save", queue_data)

        aliases = {"{value}": str(data_receive)}
        message_data = messages_file_load("response_clear_queue")
        message = utils.replace_all(message_data['response'], aliases)

        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "clear_queue_pri":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        queue_data['priority'] = {}

        utils.manipulate_json(json_path, "save", queue_data)

        aliases = {"{value}": str(data_receive)}
        message_data = messages_file_load("response_clear_queue_pri")
        message = utils.replace_all(message_data['response'], aliases)

        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")
        
        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "queue_add_pri":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")
        
        if data_receive:

            if not check_name_queue(queue_data['priority'],data_receive):

                queue_data['priority'] = add_name_queue(queue_data['priority'], data_receive, queue_config_data['limit'])
                list_players, pos = find_queue(queue_data['priority'], data_receive)

                users_in_part = ",".join(list_players)

                utils.manipulate_json(json_path, "save", queue_data)

                aliases = {
                    "{value}": str(data_receive),
                    "{match}" : str(pos),
                    "{players}" : users_in_part
                }

                message_data = messages_file_load("response_add_queue")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            else:

                aliases = {"{value}": str(data_receive)}

                message_data = messages_file_load("response_namein_queue")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            
            queue_data = utils.manipulate_json(json_path, "load")

        else:

            toast("Você deve inserir um nome para adicionar")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "queue_rem_pri":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        if check_name_queue(queue_data['priority'], data_receive):

            queue_data['priority'] = remove_name(queue_data['priority'], data_receive, int(queue_config_data['limit']))

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {"{value}": str(data_receive)}
            message_data = messages_file_load("response_rem_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        else:

            aliases = {"{value}": str(data_receive)}
            message_data = messages_file_load("response_noname_queue")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "set_playing":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        match = list(data_receive.keys())
        
        if match[0] in queue_data['normal']:

            identic = all(a == b for a, b in zip(queue_data['normal'][match[0]], data_receive[match[0]]))

            if identic:

                del queue_data['normal'][match[0]]

                queue_data['playing'] = data_receive[match[0]]

            
        utils.manipulate_json(json_path, "save", queue_data)

        players = ', '.join(data_receive[match[0]])

        aliases = {
            "{players}" : str(players),
            "{queue_type}" : "Comum"
        }

        message_data = messages_file_load("response_queue_playing")
        message = utils.replace_all(message_data['response'], aliases)

        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "set_playing_pri":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        match = list(data_receive.keys())

        if match[0] in queue_data['priority']:

            identic = all(a == b for a, b in zip(queue_data['priority'][match[0]], data_receive[match[0]]))

            if identic:

                del queue_data['priority'][match[0]]

                queue_data['playing'] = data_receive[match[0]]

            
        utils.manipulate_json(json_path, "save", queue_data)

        players = ', '.join(data_receive[match[0]])

        aliases = {
            "{players}" : str(players),
            "{queue_type}" : "Prioritária"
        }

        message_data = messages_file_load("response_queue_playing")
        message = utils.replace_all(message_data['response'], aliases)

        notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "end_playing":

        queue_data = utils.manipulate_json(json_path, "load")
        
        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        queue_data['playing']
        
        date = datetime.now().strftime("%d_%m_%Y %H:%M")
        
        players = ', '.join(queue_data['playing'])

        data = {
            "time" : date,
            "match" : players
        }

        queue_data['ended'].append(data)

        if len(queue_data['ended']) > 100:
            queue_data['ended'].pop(0)

        queue_data['playing'] = []

        utils.manipulate_json(json_path, "save", queue_data)
        
        message_data = messages_file_load("response_queue_end_match")
        notification("event", message_data["status"], message_data["status_s"], message_data['response'], "", "", "")

        queue_data = utils.manipulate_json(json_path, "load")

        data = {
            "queue": queue_data['normal'],
            "queue_pri" : queue_data['priority'],
            "queue_playing" : queue_data['playing'], 
            "roles_status": queue_config_data["queue_prioriry_role_status"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "queue_move":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        if check_name_queue(queue_data['normal'], data_receive['user']):

            queue_data['normal'] = move_name(queue_data['normal'], data_receive['actual_match'], data_receive['move_to_match'], data_receive['user'])

            utils.manipulate_json(json_path, "save", queue_data)

            message_data = messages_file_load("response_queue_move")

            aliases = {
                "{user}" : str(data_receive['user']),
                "{match_actual}" : str(data_receive['actual_match']),
                "{match_move_to}" : str(data_receive['move_to_match']),
                "{queue_type}" : "Comum",
            }

            message = utils.replace_all(message_data['response'],aliases)

            notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

            queue_data = utils.manipulate_json(json_path, "load")

            data = {
                "queue": queue_data['normal'],
                "queue_pri" : queue_data['priority'],
                "queue_playing" : queue_data['playing'], 
                "roles_status": queue_config_data["queue_prioriry_role_status"],
            }

            return json.dumps(data, ensure_ascii=False)
    
    elif type_id == "queue_move_priority":

        queue_data = utils.manipulate_json(json_path, "load")

        queue_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json", "load")

        if check_name_queue(queue_data['priority'], data_receive['user']):

            queue_data['priority'] = move_name(queue_data['priority'], data_receive['actual_match'], data_receive['move_to_match'], data_receive['user'])

            utils.manipulate_json(json_path, "save", queue_data)

            message_data = messages_file_load("response_queue_move")

            aliases = {
                "{user}" : str(data_receive['user']),
                "{match_actual}" : str(data_receive['actual_match']),
                "{match_move_to}" : str(data_receive['move_to_match']),
                "{queue_type}" : "Prioritária",
            }

            message = utils.replace_all(message_data['response'],aliases)

            notification("event", message_data["status"], message_data["status_s"], message, "", "", "")

            queue_data = utils.manipulate_json(json_path, "load")

            data = {
                "queue": queue_data['normal'],
                "queue_pri" : queue_data['priority'],
                "queue_playing" : queue_data['playing'], 
                "roles_status": queue_config_data["queue_prioriry_role_status"],
            }

            return json.dumps(data, ensure_ascii=False)


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

    type_id = data['type_id']

    if type_id == "get_response":

        key = data['key']

        responses_data = responsesdatabase.get_response(key) 

        return responses_data

    elif type_id == "save-response":

        try:
            
            key = data['key']

            responses_data = responsesdatabase.update_response(key, data)

            if responses_data:

                toast("success")

        except Exception as e:

            toast("error")
            utils.error_log(e)


def messages_file_load(key):

    responses_data = responsesdatabase.get_response(key) 

    return responses_data


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

            message_data = messages_file_load("command_vote_ended")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event" ,message_data["status"], message_data["status_s"], message, "", "", "")

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

            message_data = messages_file_load("command_vote_started")
            message = utils.replace_all(message_data['response'], aliases)

            notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

            toast("Votação criada")

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:

            toast("error")
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
    style_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/style.json", "load")

    gifts_data = giftsdatabase.get_all_gift_data()
    gifts_data = json.loads(gifts_data)

    data_receive = json.loads(data)

    type_id = data_receive['type_id']

    if type_id == "get_gift_info":

        gift_data = giftsdatabase.get_gift_info(data_receive)
        gift_data = json.loads(gift_data)

        name = gift_data["name_br"]

        if name == "" or name == None:
            name = gift_data["name"]

        data = {
            "name" : name,
            "time" : gift_data["time"],
            "status_subathon" : gift_data["status_subathon"]
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save_gift_info":

        try:

            if giftsdatabase.save_subathon_gift(data_receive):

                toast('Salvo')

        except Exception as e:
            
            toast('Error')
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

        message_data = messages_file_load("subathon_minutes_add")
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

        message_data = messages_file_load("subathon_minutes_remove")
        message = utils.replace_all(message_data['response'], aliases)
        
        notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

    elif type_id == "reset":

        data_goal = {
            'type': 'clock',
            'action' : 'reset',
        }
            
        if server.started:
            server.broadcast_message(json.dumps(data_goal))


        message_data = messages_file_load("subathon_minutes_reset")
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
    alerts_config_json_path = f"{utils.local_work('appdata_path')}/config/alerts.json"

    event_config_data = utils.manipulate_json(event_config_json_path, "load")
    alerts_config_data = utils.manipulate_json(alerts_config_json_path, "load")

    if type_id == "get":


        data = {
            "like_delay": event_config_data["ttk_like"]["delay"],
            "share_delay": event_config_data["ttk_share"]["delay"],
            "follow_sound_status": event_config_data["ttk_follow"]["sound"],
            "follow_sound_loc": event_config_data["ttk_follow"]["sound_loc"],
            "follow_sound_volume": event_config_data["ttk_follow"]["sound_volume"],
            "follow_video" : event_config_data["ttk_follow"]["video"],
            "follow_video_status" : event_config_data["ttk_follow"]["video_status"],
            "follow_video_time" : event_config_data["ttk_follow"]["video_time"],
            "like_sound_status": event_config_data["ttk_like"]["sound"],
            "like_sound_loc": event_config_data["ttk_like"]["sound_loc"],
            "like_sound_volume": event_config_data["ttk_like"]["sound_volume"],
            "like_video" : event_config_data["ttk_like"]["video"],
            "like_video_status" : event_config_data["ttk_like"]["video_status"],
            "like_video_time" : event_config_data["ttk_like"]["video_time"],
            "share_sound_status": event_config_data["ttk_share"]["sound"],
            "share_sound_loc": event_config_data["ttk_share"]["sound_loc"],
            "share_sound_volume": event_config_data["ttk_share"]["sound_volume"],
            "share_video" : event_config_data["ttk_share"]["video"],
            "share_video_status" : event_config_data["ttk_share"]["video_status"],
            "share_video_time" : event_config_data["ttk_share"]["video_time"]
        }

        return  json.dumps(data, ensure_ascii=False)

    elif type_id == "get_overlay":
                
        data = {
            "font_alerts" : alerts_config_data['font_alerts'],
            "color_alerts" : alerts_config_data['color_alerts'],
            "background_alerts" : alerts_config_data['background_alerts'],
            "opacity_alerts" : alerts_config_data['opacity_alerts'],
            "delay_alerts" : alerts_config_data['delay_alerts'],
            "image_size" : alerts_config_data['image_size'],
            "font_alertsvideo" : alerts_config_data['font_alertsvideo'],
            "color_alertsvideo" : alerts_config_data['color_alertsvideo'],
            "background_alertsvideo" : alerts_config_data['background_alertsvideo'],
            "opacity_alertsvideo" : alerts_config_data['opacity_alertsvideo'],
            "image_sizevideo" : alerts_config_data['image_sizevideo']
        }

        return  json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save_overlay":

        try:
            alerts_config_data['font_alerts'] = data_receive['font_alerts']
            alerts_config_data['color_alerts'] = data_receive['color_alerts']
            alerts_config_data['background_alerts'] = data_receive['background_alerts']
            alerts_config_data['opacity_alerts'] = data_receive['opacity_alerts']
            alerts_config_data['delay_alerts'] = data_receive['delay_alerts']
            alerts_config_data['image_size'] = data_receive['image_size']
            alerts_config_data['font_alertsvideo'] = data_receive['font_alertsvideo']
            alerts_config_data['color_alertsvideo'] = data_receive['color_alertsvideo']
            alerts_config_data['background_alertsvideo'] = data_receive['background_alertsvideo']
            alerts_config_data['opacity_alertsvideo'] = data_receive['opacity_alertsvideo']
            alerts_config_data['image_sizevideo'] = data_receive['image_sizevideo']
            
            utils.manipulate_json(alerts_config_json_path, "save", alerts_config_data)
            
            toast("success")

        except Exception as e:
            utils.error_log(e)

    elif type_id in ("save_sound_follow", "save_sound_like", "save_sound_share"):

        try:
            event_type = type_id.split("_")[2]

            event_config_data[f"ttk_{event_type}"]["sound"] = data_receive["sound"]
            event_config_data[f"ttk_{event_type}"]["sound_loc"] = data_receive["sound_loc"]
            event_config_data[f"ttk_{event_type}"]["sound_volume"] = data_receive["sound_volume"]
            event_config_data[f"ttk_{event_type}"]["video"] = data_receive["video"]
            event_config_data[f"ttk_{event_type}"]["video_status"] = data_receive["video_status"]
            event_config_data[f"ttk_{event_type}"]["video_time"] = data_receive["video_time"]
            
            if event_type != "follow":
                event_config_data[f"ttk_{event_type}"]["delay"] = data_receive["delay"]

            utils.manipulate_json(event_config_json_path, "save", event_config_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def tiktok_gift(data_receive):

    try:

        ttk_data_gifts = json.loads(data_receive)

        type_id = ttk_data_gifts["type_id"]

        result = giftsdatabase.tiktok_gift(data_receive)

        if result:

            if type_id == "save_sound_gift":
                toast("success")
            elif type_id == "save_point_gift":
                toast("success")
            elif type_id == "global_gift_save":
                toast("success")

            return result

        else:

            toast("Ocorreu um erro, o desenvolvedor já foi notificado")

    except Exception as e:

        toast("error")
        utils.error_log(e)
        

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

            goal_data = goaldatabase.get_goal(goal_type)

            data = {
                "status": goal_data["status"],
                "goal": goal_data["goal"],
                "gift_list": gift_list,
                "event": goal_data["event"],
                "goal_add": goal_data["goal_after"],
                "status_sound": goal_data["sound_status"],
                "sound_file": goal_data["sound_file"],
                "sound_volume": goal_data["sound_volume"],
                "video_status": goal_data["video_status"],
                "video_file": goal_data["video_file"],
                "video_time": goal_data["video_time"],
            }

        else:

            goal_data = goaldatabase.get_goal(goal_type)

            data = {
                "status": goal_data["status"],
                "goal": goal_data["goal"],
                "event": goal_data["event"],
                "goal_add": goal_data["goal_after"],
                "status_sound": goal_data["sound_status"],
                "sound_file": goal_data["sound_file"],
                "sound_volume": goal_data["sound_volume"],
                "video_status": goal_data["video_status"],
                "video_file": goal_data["video_file"],
                "video_time": goal_data["video_time"],  
            }

        return json.dumps(data, ensure_ascii=False)

    if type_id == "save":
        
        try:

            goal_type = data["goal_type"]

            data_save = {}

            if goal_type == "gift":
                data_save["gift"] = data["gift"]

            data_save["status"] = data["status"]
            data_save["goal"] = data["goal"]
            data_save["goal_after"] = data["goal_add_value"]
            data_save["event"] = data["event"]
            data_save["sound_status"] = data["sound_status"]
            data_save["sound_file"] = data["sound_file"]
            data_save["sound_volume"] = data["sound_volume"]
            data_save["video_status"] = data["video_status"]
            data_save["video_file"] = data["video_file"]
            data_save["video_time"] = data["video_time"]

            goaldatabase.save_goal(data_save,goal_type)

            data_goal = {
                "type": "update_goal",
                "type_goal": goal_type,
                "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
            }

            server.broadcast_message(json.dumps(data_goal))
        
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

            toast('success')

            return update_goal
            
        except Exception as e:
            
            toast('erro')
            utils.error_log(e)

    if type_id == "get_html":
        
        html_info = utils.update_goal(data)

        data_dump = json.dumps(html_info, ensure_ascii=False)

        return data_dump

    if type_id == "reset":

        try:

            goal_type = data["goal_type"]

            goaldatabase.reset_goal(goal_type)

            data_goal = {
                "type": "update_goal",
                "type_goal": goal_type,
                "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
            }

            server.broadcast_message(json.dumps(data_goal))

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")


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


def get_version():

    version = utils.get_version('code')

    return version


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
    notfic_path = f"{utils.local_work('appdata_path')}/config/notfic.json"
    config_json_path = f"{config_path}config.json"

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

    elif type_id == "save":

        data = json.loads(data_receive)

        try:
            allow = data["allow_music_save"]
            max_duration = data["max_duration"]
            skip_votes = data["skip_votes"]
            skip_mod = data["skip_mod"]
        
            utils.manipulate_json(notfic_path, "save", not_music_data)

            status_music_data["STATUS_MUSIC_ENABLE"] = allow
            status_music_data["max_duration"] = max_duration
            status_music_data["skip_votes"] = skip_votes
            status_music_data["skip_mod"] = skip_mod

            utils.manipulate_json(config_json_path, "save", status_music_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

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

    def compare_versions(v1, v2):

        parts_v1 = list(map(int, v1.split('.')))
        parts_v2 = list(map(int, v2.split('.')))

        while len(parts_v1) < len(parts_v2):
            parts_v1.append(0)
        while len(parts_v2) < len(parts_v1):
            parts_v2.append(0)

        for p1, p2 in zip(parts_v1, parts_v2):
            if p1 < p2:
                return f"DEV"
            elif p1 > p2:
                return f"OUTDATED"

        return "UPDATED"

    if type_id == "check":
        
        try:

            online_version = utils.get_version('online')
            code_version = utils.get_version('code')

            debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")

            if compare_versions(online_version, code_version) == "OUTDATED":
                
                debug_data['updated'] = "False"
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json", "save", debug_data)

                return True

            elif compare_versions(online_version, code_version) == "UPDATED" and debug_data['updated'] == "False":

                authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
                
                username = authdata.USERNAME()

                send_discord_webhook_auth(F"Atualização {utils.get_version('code')}", username)

                debug_data['updated'] = "True"
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json", "save", debug_data)

                return False
            
            elif compare_versions(online_version, code_version) == "DEV":

                return "DEV"
            
        except Exception as e:

            utils.error_log(e)
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

                message_data = messages_file_load("music_playing")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")


                config_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

                config_data_player["skip_requests"] = 0

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)

                caching = False
                
            else:
                
                caching = False
                
                toast(f"Erro ao processar música {link} - {user}")

                message_data = messages_file_load("music_process_cache_error")
                message = utils.replace_all(message_data['response'], aliases)

                notification("event", message_data["status"],message_data["status_s"], message, "", "", "")

    except Exception as e:
        
        utils.error_log(e)

        toast(f"Erro ao processar música {link} - {user}")

        aliases = {
            "{username}": user,
            "{nickname}": user,
        }

        message_data = messages_file_load("music_process_cache_error")
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

    def start_process(converted_adress):
        
        try:

            toast(f"Processando pedido {converted_adress} - {nickname}")

            if not any(item in converted_adress for item in blacklist):

                response = get_video_info(converted_adress)

                if response == "404":

                    aliases = {
                        "{username}": username,
                        "{music}": converted_adress,
                        "{nickname}" : nickname
                    } 

                    message_data = messages_file_load("music_process_error")
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

                        message_data = messages_file_load("music_added_to_queue")
                        message = utils.replace_all(message_data['response'], aliases)
                    
                        notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

                    else:

                        music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                        aliases = {
                            "{max_duration}": str(max_duration), 
                            "{username}": str(username),
                            "{nickname}": str(nickname),
                            "{user_input}": str(converted_adress),
                            "{music}": str(music_name),
                            "{music_short}": str(music_name_short)
                        }

                        message_data = messages_file_load("music_length_error")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

            else:

                music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                aliases = {
                    "{max_duration}": str(max_duration), 
                    "{username}": str(username),
                    "{nickname}": str(nickname),
                    "{user_input}": str(converted_adress),
                    "{music}": str(music_name),
                    "{music_short}": str(music_name_short)
                }

                message_data = messages_file_load("music_blacklist")
                message = utils.replace_all(message_data['response'], aliases)

                notification("music", message_data["status"],message_data["status_s"], message, "", "", "")

        except Exception as e:

            utils.error_log(e)

            aliases = {
                "{username}": str(username),
                "{nickname}": str(nickname),
                "{user_input}": str(converted_adress)
            }

            message_data = messages_file_load("music_add_error")
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

            message_data = messages_file_load("music_link_youtube")
            
            notification("music", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")
    
    else:

        start_process(user_input)


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

        recent_logs = utils.get_recent_logs()

        return recent_logs

    elif type_id == "errolog_clear":
        
        utils.clear_logs()

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

            toast("Nome removido")

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


def show_alert(data):

    try:

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

            if "duration" in data.keys():
                duration = data['duration']
            else:
                duration = 10

            imgdir = data['profile_pic']
                
            data_update = {
                "img" : imgdir,
                "message" : data['message'],
                "duration" : duration
            }

            if imgdir.endswith('.mp4') or imgdir.endswith('.gif'):

                html_type = "alertvideo"
            else:
                html_type = "alert"

            data_goal = {
                "type": html_type,
                "html": utils.update_alert(data_update)
            }

            server.broadcast_message(json.dumps(data_goal))

    except Exception as e:
        utils.error_log(e)


def check_delay(delay_command, last_use):
    
    message_error = messages_file_load("response_delay_error")

    if last_use == "":
        last_command_time = 0
    else:
        last_command_time = last_use

    delay_compare = int(delay_command)

    current_time = int(time.time())

    if current_time >= int(last_command_time) + int(delay_compare):

        message = 'OK'
        value = True

        return message, value, current_time

    else:

        remaining_time = last_command_time + delay_compare - current_time

        message = utils.replace_all(message_error['response'],{'{seconds}' : str(remaining_time)})

        message_error['response'] = message

        value = False
        current_time = ''

        return message_error, value, current_time
   
        
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

    def remove_emojis(text):
        
        emoji_pattern = re.compile("["
                                "\U0001F600-\U0001F64F"  # Emoticons
                                "\U0001F300-\U0001F5FF"  # Símbolos e pictogramas
                                "\U0001F680-\U0001F6FF"  # Transporte e mapa de caracteres
                                "\U0001F700-\U0001F77F"  # Símbolos de alquimia
                                "\U0001F780-\U0001F7FF"  # Símbolos de alquimia suplementares
                                "\U0001F800-\U0001F8FF"  # Símbolos de alguimia estendidos
                                "\U0001F900-\U0001F9FF"  # Símbolos suplementares ideográficos e pictográficos
                                "\U0001FA00-\U0001FA6F"  # Símbolos de alquimia suplementares
                                "\U0001FA70-\U0001FAFF"  # Símbolos de alquimia suplementares
                                "\U00002702-\U000027B0"  # Dingbats
                                "\U000024C2-\U0001F251" 
                                "]+", flags=re.UNICODE)
        
        return emoji_pattern.sub(r'', text)
    
    def check_name_queue(name, input_dict):

        for key, current_list in input_dict.items():
            
            if name in current_list:

                return True
            
        return False

    def add_name_queue(type_dict, name, limit):

        if len(list(type_dict.keys())) > 0:

            last_match_name = list(type_dict.keys())[-1]
            last_match_quant = len(type_dict[last_match_name])
            
            last_match_number = last_match_name.split()[1]

            if last_match_quant < int(limit):

                type_dict[last_match_name].append(name)

            else:

                new_match_number = int(last_match_number) + 1
                new_match = f"Partida {new_match_number}"

                type_dict[new_match] = [name]

        else:

            new_match = f"Partida 1"
            
            type_dict[new_match] = [name]
        
        return type_dict

    def add_name_queue_pry(type_dict, name):

        if len(list(type_dict.keys())) > 0:

            frist_match_name = list(type_dict.keys())[0]

            type_dict[frist_match_name].append(name)

        else:

            new_match = f"Partida 1"
            
            type_dict[new_match] = [name]
        
        return type_dict
    
    def find_queue(dict, name):
        
        for key, list in dict.items():

            if name in list:

                return list, key 
            
        return None

    def add_name_removed(temporary_names, limit_per_list):

        result_dict = {}

        for name_to_add in temporary_names:

            for key, current_list in result_dict.items():

                if len(current_list) < limit_per_list:

                    current_list.append(name_to_add)

                    break
            else:

                new_key = f'Partida {len(result_dict) + 1}'
                result_dict[new_key] = [name_to_add]

        return result_dict
    
    def remove_name(input_dict, name, limit):

        temporary_names = []

        for key, current_list in input_dict.items():

            if name in current_list:

                for name_in_list in current_list:

                    temporary_names.append(name_in_list)

                temporary_names.remove(name)

            else:
                for name_in_list in current_list:

                    temporary_names.append(name_in_list)

        dict_name_removed = add_name_removed(temporary_names, limit)

        return dict_name_removed
    
    command_data_prefix = utils.manipulate_json(f"{utils.local_work('appdata_path')}/commands/commands_config.json","load")
    
    command_data_giveaway = commanddatabase.get_default_command_info('giveaway')
    command_data_player = commanddatabase.get_default_command_info('player')
    command_data_queue = commanddatabase.get_default_command_info('queue')
    command_data_tts = commanddatabase.get_default_command_info('tts')
    command_data_balance = commanddatabase.get_default_command_info('balance')
    command_data_champ = commanddatabase.get_default_command_info('champ')
    command_data_votes = commanddatabase.get_default_command_info('votes')
    command_data_subathon = commanddatabase.get_default_command_info('subathon')

    command_data_votes = command_data_votes['voting']
    command_data_tts = command_data_tts['tts']

    user = data["userid"]
    message_text = data["message"]
    username = data["username"]
    display_name = data["display_name"]
     
    user_data_load_db = userdatabase.get_user_data(user)

    if user_data_load_db != None:

        user_roles = user_data_load_db["roles"]
    
    else:
        user_roles = ['spec']
    
    command_string = message_text.lower()

    if len(re.split(r'\s+', command_string, maxsplit=1)) > 1:

        command, sufix = re.split(r'\s+', command_string, maxsplit=1)
        
    else:

        sufix = None
        command = command_string.strip()

    if len(command) > 0:
        prefix = command[0]
    else:
        prefix = ""

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

    def check_whitelist(whitelist_status, whitelist, blacklist, user_data_load_db):

        username = user_data_load_db['username']
        display_name = user_data_load_db['display_name']
        userid = user_data_load_db['userid']

        if username in blacklist or display_name in blacklist or userid in blacklist:

            return False
        
        elif whitelist_status == 1:

            if username in whitelist or display_name in whitelist or userid in whitelist:

                return True
            else:
                return False
            
        else:
            return True
            
    def extract_top_n_from_string(input_string):
        
        match = re.search(r'{top-(\d+)}', input_string)
        if match:
            return int(match.group(1))
        else:
            return None
    
    def generate_top_users_string(names_and_points, format_string, type_top):

        try:
            
            if not names_and_points or not format_string:

                message_data = messages_file_load("balance_top_error_response")

                notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                return False

            match = re.match(r"{top-(\d+)}", format_string)

            if match:

                num_names = int(match.group(1))

            else:

                message_data = messages_file_load("balance_top_error_response")

                
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

    def send_error_level(message_data):

        message = message_data['response']

        matches = re.search(r"\[([^\]]+)\]", message)

        if matches:

            permission_list = matches.group(1).split(', ')

            follow_role_name = messages_file_load('follow_role_name')
            gifts_role_name = messages_file_load('gifts_role_name')
            Likes_role_name = messages_file_load('Likes_role_name')
            shares_role_name = messages_file_load('shares_role_name')
            subscriber_role_name = messages_file_load('subscriber_role_name')
            subscriber_custom_role_name = messages_file_load('subscriber_custom_role_name')
            moderator_role_name = messages_file_load('moderator_role_name')

            aliases_roles = {
                "follow" : follow_role_name['response'],
                "gifts" : gifts_role_name['response'],
                "Likes" : Likes_role_name['response'],
                "shares" :shares_role_name['response'],
                "subscriber" : subscriber_role_name['response'],
                "subscriber_custom" : subscriber_custom_role_name['response'],
                "moderator" : moderator_role_name['response']
            }

            roles_string = ""

            for perm in permission_list:

                perm_clear = perm.strip("'")

                if perm_clear in aliases_roles.keys():

                    permm = f"{aliases_roles[perm_clear]}, "
                    
                    roles_string += permm

            roles_string = roles_string[:-2]

            message = message.replace(matches.group(0), roles_string)

        notification("command", message_data["status"],message_data["status_s"], message, "", "", "")


    def check_status(command_info, aliases):

        message_data = messages_file_load("event_command")
        message = utils.replace_all(message_data['response'], aliases)

        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
        
        status = command_info["status"]
        user_level = command_info["user_level"]
        delay = int(command_info["delay"])
        last_use = command_info["last_use"]
        cost = command_info["cost"]
        cost_status = command_info["cost_status"]

        whitelist = command_info["whitelist"]
        blacklist = command_info["blacklist"]
        whitelist_status = command_info["whitelist_status"]

        message_delay, check_time, current = check_delay(delay, last_use)
        
        if status:
        
            if check_perm(user_roles, user_level):
                
                if check_whitelist(whitelist_status, whitelist, blacklist, user_data_load_db):

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

                                message_data = messages_file_load("command_cost")
                                message = utils.replace_all(message_data['response'], aliases)

                                message_data['response'] = message

                                return current, message_data, False, 'cost'
                            
                    else:

                        message_data = messages_file_load("command_sufix")

                        return current, message_data, False, 'delay'

                else:

                    aliases = {
                        "{nickname}" : display_name,
                        "{username}": username,
                        "{user_level}": str(user_level),
                        "{command}": str(command),
                    }

                    message_data = messages_file_load("user_in_blacklist")
                    message_error = utils.replace_all(message_data['response'], aliases)
                    message_data['response'] = message_error

                    return current, message_data, False, 'whitelist'
            
            else:

                aliases = {
                    "{nickname}" : display_name,
                    "{username}": username,
                    "{user_level}": str(user_level),
                    "{command}": str(command),
                }

                message_data = messages_file_load("error_user_level")
                message_error = utils.replace_all(message_data['response'], aliases)
                message_data['response'] = message_error

                return current, message_data, False, 'level'

        else:
            
            message_data = messages_file_load("command_disabled")
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

                elif command_info["type"] == "video":
                    
                    notification("command", 0, 0, response, command_info["video"], command_info["video_time"], sufix)

                elif command_info["type"] == "videotext":

                    notification("command", 1, 1, response, command_info["video"], command_info["time_video"], sufix)

                elif command_info["type"] == "tts":

                    if not response == None:

                        response = remove_emojis(response)

                        user_input_short = textwrap.shorten(response, width=300, placeholder=" ")
                        tts = gTTS(text=user_input_short, lang="pt", slow=False)

                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)

                        rando = random.randint(1, 10)

                        audio_path = f"{utils.local_work('appdata_path')}/player/cache/tts{rando}.mp3"

                        with open(audio_path, "wb") as f:
                            f.write(mp3_fp.read())

                        notification("command",  1, 1, response, audio_path, 50, sufix)

                    else:

                        message_data = messages_file_load("error_tts_no_text_command")

                        notification("command", message_data["status"],message_data["status_s"], message_data['response'], "", "", sufix)

                elif command_info["type"] == "text":

                    notification("command", 1, 1, response, "", "", sufix)

                if command_info["keys_status"] == 1:

                    threading.Thread(target=press_keys, args=(command_info,), daemon=True).start()

                commanddatabase.update_delay(command, current)

            else:

                if type_error == "level":

                    send_error_level(message_error)
                    
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

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)
                    
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "add_user", "giveaway")

            else:

                if type_error == "level":
                    
                    send_error_level(message_error)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["enter"]["command"]):

            command_info = command_data_giveaway["enter"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                giveaway_py("add_user", {"new_name": display_name,})

                commanddatabase.update_last_use(current,"enter","giveaway")

            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["execute_giveaway"]["command"]):

            command_info = command_data_giveaway["execute_giveaway"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                giveaway_py("execute", 'Null')

                commanddatabase.update_last_use(current, "execute_giveaway", "giveaway")

            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_giveaway["clear_giveaway"]["command"]):

            command_info = command_data_giveaway["clear_giveaway"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                reset_data = []
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/names.json", "save", reset_data)

                message_data = messages_file_load("giveaway_clear")
                message = utils.replace_all(message_data['response'], aliases)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
        
                commanddatabase.update_last_use(current, "clear_giveaway", "giveaway")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                        message_data = messages_file_load("response_user_giveaway")
                        message = utils.replace_all(message_data['response'], aliases)
                        message = utils.replace_all(message, aliases_command)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("response_no_user_giveaway")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "check_name", "giveaway")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                    message_data = messages_file_load("response_user_giveaway")
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

                    message_data = messages_file_load("response_no_user_giveaway")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message, aliases_command)
                
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "check_self_name", "giveaway")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                            message_data = messages_file_load("command_volume_confirm")
                            message = utils.replace_all(message_data['response'], aliases)

                            message = utils.replace_all(message, aliases_commands)
                            
                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                        else:
                            
                            aliases_commands = {
                                "{volume}": str(volume_value_int),
                            }

                            message_data = messages_file_load("command_volume_error")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_commands)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("command_volume_number")
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

                    message_data = messages_file_load("command_volume_response")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message,aliases_commands)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "volume", "player")

            else:
                
                if type_error == "level":

                    send_error_level(message_error)

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

                        message_data = messages_file_load("command_skip_confirm")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                        config_data_player["skip_requests"] = 0

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player)

                    else:

                        if not user in skip_users:

                            skip_requests = int(skip_requests) + 1

                            aliases_commands = {
                                "{votes}": str(skip_requests),
                                "{minimum}": str(skip_votes),
                            }

                            message_data = messages_file_load("skip_votes")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_commands)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            if int(skip_requests) == skip_votes:

                                if main_window_open:
                                    main_window.evaluate_js(f"player('stop', 'none', 'none')")

                                message_data = messages_file_load("command_skip_confirm")
                                message = utils.replace_all(message_data['response'], aliases)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                                config_data_player["skip_requests"] = 0
                                config_data_player["skip_users"] = []

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player)

                            else:

                                skip_users.append(display_name)

                                config_data_player["skip_users"] = skip_users
                                config_data_player["skip_requests"] = int(skip_requests)

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player,)

                        else:

                            message_data = messages_file_load("command_skip_inlist")
                            message = utils.replace_all(message_data['response'], aliases)
                        
                else:
                    
                    message_data = messages_file_load("command_skip_noplaying")
                    message = utils.replace_all(message_data['response'], aliases)
                    
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "skip", "player")
            
            else:

                if type_error == "level":

                    send_error_level(message_error)

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
                        
                        message_data = messages_file_load("music_disabled")
                        message = utils.replace_all(message_data['response'], aliases)
                    
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    

                else:

                    message_data = messages_file_load("command_value")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                commanddatabase.update_last_use(current, "request", "player")

            else:
                
                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status"], message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_player['atual']['command']):

            command_info = command_data_player['atual']

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                           
                f = open(f"{utils.local_work('appdata_path')}/player/list_files/currentsong.txt", "r+", encoding="utf-8")
                current_song = f.read()

                aliases_commands = {'{music}': str(current_song)}

                message_data = messages_file_load("command_current_confirm")
                message = utils.replace_all(message_data['response'], aliases)
                message = utils.replace_all(message,aliases_commands)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                commanddatabase.update_last_use(current, "atual", "player")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                    message_data = messages_file_load("command_next_confirm")
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

                    message_data = messages_file_load("command_next_confirm")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message,aliases_commands)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = messages_file_load("command_next_no_music")
                    message = utils.replace_all(message_data['response'], aliases)
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                            
                commanddatabase.update_last_use(current, "next", "player")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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
                        
                        in_normal = check_name_queue(user_add, queue_data['normal'])
                        in_priority = check_name_queue(user_add, queue_data['priority'])
                        
                        if in_normal == False and in_priority == False and not user_add in queue_data['playing']:

                            if queue_config['spend_user_balance'] == 1:

                                cost = command_data_queue["self_add_queue"]["cost"]

                                check = userdatabase.check_cost(usercheck_userid, cost, 1)

                                if check:

                                    if queue_config['queue_prioriry_role_status']:

                                        priority_roles = queue_config['queue_prioriry_roles']

                                        priority_check = check_perm(user_roles,priority_roles)

                                        if priority_check:

                                            if queue_config['queue_prioriry']:
                                                
                                                queue_data['priority'] = add_name_queue(queue_data['priority'], user_add, queue_config['limit'])
                                                list_players, pos = find_queue(queue_data['priority'], user_add)

                                            else:

                                                queue_data['normal'] = add_name_queue_pry(queue_data['normal'], user_add)
                                                list_players, pos = find_queue(queue_data['normal'], user_add)

                                        else:

                                            queue_data['normal'] = add_name_queue(queue_data['normal'], user_add,queue_config['limit'])
                                            list_players, pos = find_queue(queue_data['normal'], user_add)

                                    else:

                                        queue_data['normal'] = add_name_queue(queue_data['normal'], user_add,queue_config['limit'])
                                        list_players, pos = find_queue(queue_data['normal'], user_add)


                                    users_in_part = ",".join(list_players)

                                    aliases_commands = {
                                        "{value}" : user_add,
                                        "{match}": str(pos),
                                        "{players}" : users_in_part
                                    }
                
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                                    message_data = messages_file_load("response_queue")
                                    message = utils.replace_all(message_data['response'], aliases)
                                    message = utils.replace_all(message,aliases_commands)

                                    notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                                    if main_window_open:
                                        
                                        main_window.evaluate_js(f"queue_js('get_queue','null')")
                                    
                                else:

                                    message_data = messages_file_load("balance_user_insuficient")
                                    message = utils.replace_all(message_data['response'], aliases)

                                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            else:

                                if queue_config['queue_prioriry_role_status']:

                                    priority_roles = queue_config['queue_prioriry_roles']

                                    priority_check = check_perm(user_roles,priority_roles)

                                    if priority_check:

                                        if queue_config['queue_prioriry']:

                                            queue_data['priority'] = add_name_queue(queue_data['priority'], user_add, queue_config['limit'])
                                            list_players, pos = find_queue(queue_data['priority'], user_add)

                                        else:

                                            queue_data['normal'] = add_name_queue_pry(queue_data['normal'], user_add)
                                            list_players, pos = find_queue(queue_data['normal'], user_add)
                                    else:

                                        queue_data['normal'] = add_name_queue(queue_data['normal'], user_add,queue_config['limit'])
                                        list_players, pos = find_queue(queue_data['normal'], user_add)

                                else:

                                    queue_data['normal'] = add_name_queue(queue_data['normal'], user_add,queue_config['limit'])
                                    list_players, pos = find_queue(queue_data['normal'], user_add)

                                users_in_part = ",".join(list_players)

                                aliases_commands = {
                                    "{value}" : user_add,
                                    "{match}": str(pos),
                                    "{players}" : users_in_part
                                }
            
                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                                message_data = messages_file_load("response_add_queue")
                                message = utils.replace_all(message_data['response'], aliases)
                                message = utils.replace_all(message, aliases_commands)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                                
                                if main_window_open:
                                    
                                    main_window.evaluate_js(f"queue_js('get_queue','null')")

                        else:
                            
                            if user_add not in queue_data['playing']:

                                if check_name_queue(user_add, queue_data['normal']):

                                    list_players, pos = find_queue(queue_data['normal'], user_add)

                                elif check_name_queue(user_add, queue_data['priority']):

                                    list_players, pos = find_queue(queue_data['priority'], user_add)

                                users_in_part = ",".join(list_players)

                                aliases_commands = {
                                    "{value}" : user_add,
                                    "{match}": str(pos),
                                    "{players}" : users_in_part
                                }

                                message_data = messages_file_load("response_namein_queue")
                                message = utils.replace_all(message_data['response'], aliases)
                                message = utils.replace_all(message, aliases_commands)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", "")
                                
                                if main_window_open:
                                    
                                    main_window.evaluate_js(f"queue_js('get_queue','null')")

                            else:

                                message_data = messages_file_load("response_namein_playing")
                                message = utils.replace_all(message_data['response'], aliases)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

                                if main_window_open:
                                    
                                    main_window.evaluate_js(f"queue_js('get_queue','null')")

                    else:

                        message_data = messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                        
                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "add_queue", "queue")

            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_queue["self_add_queue"]["command"]):
            
            command_info = command_data_queue["self_add_queue"]
            
            queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

            queue_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json","load")

            user_add = f"{display_name} | {username}"
            
            in_normal = check_name_queue(user_add, queue_data['normal'])
            in_priority = check_name_queue(user_add, queue_data['priority'])
            
            if in_normal == False and in_priority == False and not user_add in queue_data['playing']:

                current, message_error, status, type_error = check_status(command_info, aliases)

                if status:
                    
                    if queue_config['queue_prioriry_role_status']:

                        priority_roles = queue_config['queue_prioriry_roles']

                        priority_check = check_perm(user_roles,priority_roles)

                        if priority_check:

                            if queue_config['queue_prioriry']:

                                queue_data['priority'] = add_name_queue(queue_data['priority'], user_add, queue_config['limit'])
                                list_players, pos = find_queue(queue_data['priority'], user_add)

                            else:

                                queue_data['normal'] = add_name_queue_pry(queue_data['normal'], user_add)
                                list_players, pos = find_queue(queue_data['normal'], user_add)
                        else:

                            queue_data['normal'] = add_name_queue(queue_data['normal'], user_add,queue_config['limit'])
                            list_players, pos = find_queue(queue_data['normal'], user_add)

                    else:

                        queue_data['normal'] = add_name_queue(queue_data['normal'], user_add,queue_config['limit'])
                        list_players, pos = find_queue(queue_data['normal'], user_add)


                    users_in_part = ",".join(list_players)

                    aliases_commands = {
                        "{value}" : user_add,
                        "{match}": str(pos),
                        "{players}" : users_in_part
                    }

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                    message_data = messages_file_load("response_add_queue")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message, aliases_commands)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                    if main_window_open:
                        
                        main_window.evaluate_js(f"queue_js('get_queue','null')")

                else:

                    if type_error == "level":

                        send_error_level(message_error)

                    else:

                        notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)
                
                commanddatabase.update_last_use(current, "self_add_queue", "queue")

            else:
               
                if user_add not in queue_data['playing']:

                    if check_name_queue(user_add, queue_data['normal']):

                        list_players, pos = find_queue(queue_data['normal'], user_add)

                    elif check_name_queue(user_add, queue_data['priority']):

                        list_players, pos = find_queue(queue_data['priority'], user_add)

                    users_in_part = ",".join(list_players)

                    aliases_commands = {
                        "{value}" : user_add,
                        "{match}": str(pos),
                        "{players}" : users_in_part
                    }

                    message_data = messages_file_load("response_namein_queue")
                    message = utils.replace_all(message_data['response'], aliases)
                    message = utils.replace_all(message, aliases_commands)

                    notification("command", message_data["status"], message_data["status_s"], message, "", "", "")

                    if main_window_open:
                        
                        main_window.evaluate_js(f"queue_js('get_queue','null')")

                else:

                    message_data = messages_file_load("response_namein_playing")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", "")

                    if main_window_open:
                        
                        main_window.evaluate_js(f"queue_js('get_queue','null')")

        elif compare_strings(command, command_data_queue["check_queue"]["command"]):

            command_info = command_data_queue["check_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)
                    
            if status:
            
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

                message_data = messages_file_load("response_get_queue")
                message = utils.replace_all(message_data['response'], aliases)


                if queue_data['normal'] and len(queue_data['normal']) > 0:

                    match = list(queue_data['normal'].values())[0]
                    match = ', '.join(match)

                else:

                    match = "Lista vazia"

                aliases_commands = {
                    "{players}" : match
                }

                message = utils.replace_all(message, aliases_commands)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                commanddatabase.update_last_use(current, "check_queue", "queue")

            else:
                
                if type_error == "level":

                    send_error_level(message_error)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_queue["check_queue_p"]["command"]):

            command_info = command_data_queue["check_queue_p"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
            
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

                message_data = messages_file_load("response_get_queue")
                message = utils.replace_all(message_data['response'], aliases)

                match = re.search(r'\{queue-(\d*)\}', message)

                if match:

                    number = int(match.group(1))

                    queue_pry = [item.split(' | ')[0] for item in queue_data['priority']]

                    replacement = ', '.join(queue_pry[:number])

                    message = message.replace(match.group(0), replacement)


                if queue_data['priority'] and len(queue_data['priority']) > 0:

                    match = list(queue_data['priority'].values())[0]
                    match = ', '.join(match)

                else:

                    match = "Lista vazia"

                aliases_commands = {
                    "{players}" : match
                }

                message = utils.replace_all(message, aliases_commands)


                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                commanddatabase.update_last_use(current, "check_queue_p", "queue")

            else:
                
                if type_error == "level":

                    send_error_level(message_error)

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

                        queue_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json","load")
                        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")
                        
                        usercheck_display_name = user_found["display_name"]
                        usercheck_username = user_found["username"]

                        user_add = f"{usercheck_display_name} | {usercheck_username}"

                        if user_add in  queue_data['normal'] or user_add in queue_data['priority']:

                            if user_add in queue_data['normal']:
                                
                                queue_data['normal'] = remove_name(queue_data['normal'], user_add, int(queue_config['limit']))

                            elif user_add in queue_data['priority']:

                                queue_data['priority'] = remove_name(queue_data['priority'], user_add, int(queue_config['limit']))

                            utils.manipulate_json( f"{utils.local_work('appdata_path')}/queue/queue.json","save", queue_data)

                            message_data = messages_file_load("response_rem_queue")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            queue('update_queue', "")

                        else:

                            message_data = messages_file_load("response_noname_queue")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "rem_queue", "queue")

            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_tts["command"]):

            def remove_repetitions(text):

                words = text.split()  # Transforma a string em uma lista de palavras
                words_no_repeat = []
                
                for word in words:
                    if word not in words_no_repeat:
                        words_no_repeat.append(word)
                
                text_no_repeat = ' '.join(words_no_repeat)  # Reconstrói a string
                return text_no_repeat
            
            def remove_repetitions_letters(string):
                
                result = ""

                max_repeticoes = 4

                for char in string:

                    if result.endswith(char * (max_repeticoes - 1)):
                        continue

                    result += char

                return result

            def blacklist_filter(text, blacklist_words):

                words = text.split()
                
                filtered_words = [word for word in words if word.lower() not in blacklist_words]

                filtered_words_string = ' '.join(filtered_words)

                return filtered_words_string

            command_info = command_data_tts

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    try:

                        tts_json_path = (f"{utils.local_work('appdata_path')}/config/tts.json")

                        tts_config_data = utils.manipulate_json(tts_json_path, "load")
                        
                        message_data = messages_file_load("tts_prefix")
                        message_prefix = utils.replace_all(message_data['response'], aliases)

                        if tts_config_data['prefix']:
                            sufix = f"{message_prefix} {sufix}"
                        
                        if tts_config_data['emojis_filter']:
                            sufix = remove_emojis(sufix)

                        if tts_config_data['words_filter']:
                            sufix = remove_repetitions(sufix)

                        if tts_config_data['letters_filter']:
                            sufix = remove_repetitions_letters(sufix)

                        sufix = blacklist_filter(sufix,tts_config_data['blacklist_words'])

                        if len(sufix) > 0:

                            user_input_short = textwrap.shorten(sufix, width=300, placeholder=" ")

                            tts = gTTS(text=user_input_short, lang="pt", slow=False)

                            mp3_fp = BytesIO()
                            tts.write_to_fp(mp3_fp)
                            mp3_fp.seek(0)

                            rando = random.randint(1, 100)

                            audio_path = f"{utils.local_work('datadir')}/web/src/player/cache/tts{rando}.mp3"

                            with open(audio_path, "wb") as f:
                                f.write(mp3_fp.read())

                            notification("tts",  0, 0, "", audio_path, 50, sufix)

                    except Exception as e:
                        utils.error_log(e)

                else:

                    message_data = messages_file_load("error_tts_no_text")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "tts", "tts")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                    message_data = messages_file_load("response_add_champ")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)

                    if main_window_open:
                        main_window.evaluate_js(f"getMatchesLoad()")

                else:

                    message_data = messages_file_load("response_in_champ")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                commanddatabase.update_last_use(current, "enter_camp", "champ")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                            message_data = messages_file_load("response_add_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)

                            if main_window_open:
                                main_window.evaluate_js(f"getMatchesLoad()")

                        else:

                            message_data = messages_file_load("response_in_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "add_camp", "champ")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                            message_data = messages_file_load("response_remove_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                            champ_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/champ/champ.json","save", champ_data)

                            if main_window_open:
                                main_window.evaluate_js(f"getMatchesLoad()")

                        else:

                            message_data = messages_file_load("response_not_in_champ")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                            
                    else:

                        message_data = messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "remove_camp", "champ")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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
                                
                                message_data = messages_file_load("command_vote_voted")
                                message = utils.replace_all(message_data['response'], aliases)
                                message = utils.replace_all(message, aliases_commands)

                                notification("command", message_data["status"], message_data["status_s"], message, "", "", sufix)

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/voting/votes.json","save",options)


                                update_votes = utils.update_votes({"type_id" : "update_votes"})

                                data_goal = {
                                    'type': 'votes',
                                    'html': update_votes
                                }
                                    
                                if server.started:
                                    server.broadcast_message(json.dumps(data_goal))

                                if main_window_open:
                                    main_window.evaluate_js(f"votes('get_options')")

                            else:

                                message_data = messages_file_load("command_vote_notfound")
                                message = utils.replace_all(message_data['response'], aliases)

                                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                        else:

                            message_data = messages_file_load("command_sufix")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                    
                    else:

                        message_data = messages_file_load("command_vote_norun")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = messages_file_load("command_vote_arvoted")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "votes", "voting") 
  
            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                message_data = messages_file_load("balance")
                message = utils.replace_all(message_data['response'], aliases)
                message = utils.replace_all(message, aliases_balance)

                notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "user_balance", "balance")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                        message_data = messages_file_load("balance_moderator")
                        message = utils.replace_all(message_data['response'], aliases)
                        message = utils.replace_all(message, aliases_balance)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "mod_balance", "balance")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                        message_data = messages_file_load("balance_user_gived")
                        message = utils.replace_all(message_data['response'], aliases)
                        message = utils.replace_all(message, aliases_balance)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)

                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = messages_file_load("command_root_sufix_number")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "mod_balance_give", "balance")
                                    
            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                            message_data = messages_file_load("balance_user_spended")
                            message = utils.replace_all(message_data['response'], aliases)
                            message = utils.replace_all(message, aliases_balance)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                        else:

                            message_data = messages_file_load("balance_user_insuficient")
                            message = utils.replace_all(message_data['response'], aliases)

                            notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    else:

                        message_data = messages_file_load("balance_user_not_found")
                        message = utils.replace_all(message_data['response'], aliases)
                     
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    
                else:

                    message_data = messages_file_load("command_root_sufix_number")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                commanddatabase.update_last_use(current, "mod_balance_take", "balance")
  
            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_points"]["command"]):

            command_info = command_data_balance["top_points"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('points',10)

                names_and_points = [(user['display_name'], user['points']) for user in users]

                message_data = messages_file_load("balance_top_points")

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

                commanddatabase.update_last_use(current, "top_points", "balance")
      
            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_likes"]["command"]):

            command_info = command_data_balance["top_likes"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('likes',10)

                names_and_points = [(user['display_name'], user['likes']) for user in users]

                message_data = messages_file_load("balance_top_likes")

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

                commanddatabase.update_last_use(current, "top_likes", "balance")
      
            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_shares"]["command"]):

            command_info = command_data_balance["top_shares"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('shares',10)

                names_and_points = [(user['display_name'], user['shares']) for user in users]

                message_data = messages_file_load("balance_top_shares")

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
                        
                commanddatabase.update_last_use(current, "top_shares", "balance")
      
            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:
                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

        elif compare_strings(command, command_data_balance["top_gifts"]["command"]):

            command_info = command_data_balance["top_gifts"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                users = userdatabase.get_users_ranking('gifts',10)

                names_and_points = [(user['display_name'], user['gifts']) for user in users]

                message_data = messages_file_load("balance_top_gifts")

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

                commanddatabase.update_last_use(current, "top_gifts", "balance")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                        message_data = messages_file_load("subathon_minutes_add")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("command_volume_number")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                

                commanddatabase.update_last_use(current, "add_minutes", "subathon")

            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                        message_data = messages_file_load("subathon_minutes_remove")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                    else:

                        message_data = messages_file_load("command_volume_number")
                        message = utils.replace_all(message_data['response'], aliases)
                        
                        notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)

                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                    
                
                commanddatabase.update_last_use(current, "remove_minutes", "subathon")
  
            else:

                if type_error == "level":

                    send_error_level(message_error)

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

                    message_data = messages_file_load("subathon_minutes_reset")
                    message = utils.replace_all(message_data['response'], aliases)
                    
                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)


                else:

                    message_data = messages_file_load("command_sufix")
                    message = utils.replace_all(message_data['response'], aliases)

                    notification("command", message_data["status"],message_data["status_s"], message, "", "", sufix)
                
                commanddatabase.update_last_use(current, "clear_minutes", "subathon") 
  
            else:

                if type_error == "level":

                    send_error_level(message_error)

                else:

                    notification("command", message_error["status_s"],message_error["status_s"], message_error['response'], "", "", sufix)

    else:


        message_data = messages_file_load("commands_disabled")
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

        loop = threading.Thread(target=loopcheck, args=(), daemon=True)
        loop.start()

        loop_r = threading.Thread(target=looprank, args=(), daemon=True)
        loop_r.start()

        loop_nt = threading.Thread(target=loop_notification, args=(), daemon=True)
        loop_nt.start()

        loop_ct = threading.Thread(target=loop_chat_slow, args=(), daemon=True)
        loop_ct.start()

        log_chat('start', None)

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

        total_list = ["total_follow", "total_share", "total_likes", "total_gifts", "total_diamonds", "total_specs"]

        if goal_type in total_list:

            total_dict = {
                "total_follow": "follow",
                "total_share": "share",
                "total_likes": "likes",
                "total_gifts": "gifts",
                "total_diamonds": "diamonds",
                "total_specs": "max_viewer"
            }

            goal_data = goaldatabase.get_goal(total_dict[goal_type])

            if goal_type == "total_follow":

                follows = goaldatabase.get_current('follow')
                total_follow = int(ammount) + follows
                goaldatabase.update_current(total_follow, "follow")

                return total_follow

            elif goal_type == "total_likes":

                goaldatabase.update_current(ammount, "likes")

                return True

            elif goal_type == "total_share":

                total_shares = goaldatabase.get_current("share") + int(ammount)
                goaldatabase.update_current(total_shares, "share")

                return total_shares
            
            elif goal_type == "total_diamonds":  

                total_diamonds = goaldatabase.get_current("diamonds") + int(ammount)
                goaldatabase.update_current(total_diamonds, "diamonds")

                return total_diamonds

            elif goal_type == "total_gifts":           

                total_gifts = goaldatabase.get_current("gifts") + int(ammount)
                goaldatabase.update_current(total_gifts, "gifts")

                return total_gifts
            
            elif goal_type == "total_specs":      

                current_specs = goaldatabase.get_current("max_viewer")

                if int(ammount) >= int(current_specs):

                    goaldatabase.update_current(int(ammount), "max_viewer")

                    return int(ammount)
                
                else:

                    current_specs = goaldatabase.get_current("max_viewer")

                    return current_specs

        else:

            goal_data = goaldatabase.get_goal(goal_type)

            if goal_data["status"] == 1:

                if int(ammount) >= int(goal_data["goal"]):

                    if goal_data["event"] == "double":
                        
                        goal = int(goal_data["goal"])

                        while not goal > ammount:
                            goal = int(goal_data["goal"]) * 2

                        goal_data["goal"] = goal

                    elif goal_data["event"] == "add":
                        
                        goal = int(goal_data["goal"])

                        while not goal > ammount:
                            goal += int(goal_data["goal_after"])

                        goal_data["goal"] = goal

                    elif goal_data["event"] == "Multiply": 

                        goal = int(goal_data["goal"])

                        while not goal > ammount:
                            goal = int(goal_data["goal"]) * int(goal_data["goal_after"])

                        goal_data["goal"] = goal

                    else:
                        
                        if int(ammount) >= int(goal_data["goal"]):
                            goal = int(goal_data["goal_after"])

                    goaldatabase.update_goal(goal,goal_type)

                    message_data = messages_file_load("goal_end")

                    data_goal = {
                        "type": "update_goal",
                        "type_goal": goal_type,
                        "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
                    }
                                    
                    send_discord_webhook({'type_id' : 'goal_end', 'target':f'{goal}' ,'current' : f'{ammount}', 'goal_type' : {goal_type}})

                    aliases = {
                        "{current}" : ammount,
                        "{target}" : goal_data["goal"],
                        "{type}" : goal_type,
                    }

                    message = utils.replace_all(message_data['response'], aliases)

                    if "video_file" in goal_data:

                        video_status = goal_data["video_status"]
                        video = goal_data["video_file"]
                        video_time = goal_data["video_time"]

                        if video_status == 1:

                            notification("goal_end", message_data["status"], message_data["status_s"], message, video, video_time, "")

                        else:
                            
                            audio = goal_data["sound_file"]
                            volume = goal_data["sound_volume"]

                            notification("goal_end", message_data["status"], message_data["status_s"], message, audio, volume, "")

                    else:

                        audio = goal_data["sound_file"]
                        volume = goal_data["sound_volume"]

                        notification("goal_end", message_data["status"], message_data["status_s"], message, audio, volume, "")
                    

                        
                else:

                    goal = int(goal_data["goal"])

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


def animation(type,status):

    debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")

    if type == 'get':

        return debug_data['animation']

    elif type == 'save':

        if status == True:

            debug_data['animation'] = "True"
        
        else:

            debug_data['animation'] = "False"

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","save", debug_data)


def log_chat(type_id, data):

    global chatlogmanager

    if type_id == "save":

        chat_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        if chat_config_data['chat-log-status'] == 1:

            date = datetime.now().strftime("%d_%m_%Y")

            chatlogmanager.add_chat(date, data)

    elif type_id == "start":

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/chat/chat_config.json","load")

        if chatlogmanager and chat_data['chat-log-status'] == 1:

            max_days = chat_data['chat-log-days']

            chatlogmanager = ChatLogManager()
            chatlogmanager.remove_old_tables(int(max_days))

            if chat_data['chat-log-status'] == 1:

                total_items = 0

                if total_items < 20:

                    for days_ago in range(int(max_days)):

                        date_to_query = (datetime.now() - timedelta(days=days_ago)).strftime("%d_%m_%Y")

                        recent_events = chatlogmanager.get_messages(date_to_query, limit=20)
    
                        for data_message in reversed(recent_events):

                            if main_window_open:
                                main_window.evaluate_js(f"append_message({json.dumps(data_message, ensure_ascii=False)})")

                            if window_chat_open:
                                window_chat.evaluate_js(f"append_message_out({json.dumps(data_message, ensure_ascii=False)})")

                            total_items += 1

                            if total_items >= 20:
                                break

                        if total_items >= 20:
                            break

    elif type_id == "get":

        date = datetime.now().strftime("%d_%m_%Y")

        chatlogdata = chatlogmanager.get_message(date, data)

        return  json.dumps(chatlogdata, ensure_ascii=False)


def ttk_alert(type_id, message):

    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/events/event_not.json", "load")

    if type_id == "follow":

        if event_config_data["ttk_follow"]["video_status"] == 1:

            video_path = event_config_data["ttk_follow"]["video"]  
            video_time = event_config_data["ttk_follow"]["video_time"]

            notification("follow", 1, 1, message, video_path, video_time, "")

        elif event_config_data["ttk_follow"]["sound"] == 1:

            audio_path = event_config_data["ttk_follow"]["sound_loc"]
            audio_volume = event_config_data["ttk_follow"]["sound_volume"]

            notification("follow", 1, 1, message, audio_path, audio_volume, "")

        else:
        
            notification("follow", 1, 1, message, "", "", "")


    elif type_id == "like":
        
        if event_config_data["ttk_like"]["video_status"] == 1:

            video_path = event_config_data["ttk_like"]["video"]  
            video_time = event_config_data["ttk_like"]["video_time"]

            notification("like", 1, 1, message, video_path, video_time, "")

        elif event_config_data["ttk_like"]["sound"] == 1:

            audio_path = event_config_data["ttk_like"]["sound_loc"]
            audio_volume = event_config_data["ttk_like"]["sound_volume"]

            notification("like", 1, 1, message, audio_path, audio_volume, "")

        else:
        
            notification("like", 1, 1, message, "", "", "")
    

    elif type_id == "share":
        
        if event_config_data["ttk_share"]["video_status"] == 1:

            video_path = event_config_data["ttk_share"]["video"]  
            video_time = event_config_data["ttk_share"]["video_time"]

            notification("share", 1, 1, message, video_path, video_time, "")

        elif event_config_data["ttk_share"]["sound"] == 1:

            audio_path = event_config_data["ttk_share"]["sound_loc"]
            audio_volume = event_config_data["ttk_share"]["sound_volume"]

            notification("share", 1, 1, message, audio_path, audio_volume, "")

        else:
        
            notification("share", 1, 1, message, "", "", "")


def on_connect(event):

    global conected

    event = utils.DictDot(event)

    new_room = event.room_id
    total_follows = event.followers
    new_gift_info = event.giftdata

    gift_data = json.loads(new_gift_info)

    debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")

    room_id_store = debug_data['room_id']

    try:
        
        giftsdatabase.update_or_insert_gifts(gift_data)

        if room_id_store != new_room:

            debug_data['room_id'] = new_room

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","save",debug_data)

            goaldatabase.reset_goal("diamonds")
            goaldatabase.reset_goal("gift")
            goaldatabase.reset_goal("share")
            goaldatabase.reset_goal("max_viewer")
            goaldatabase.reset_goal("likes")
            goaldatabase.update_current(int(total_follows),"follow")

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json", "save", {"likes" : {}})
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json", "save", {"shares" : {}})
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json", "save", [])

            message_data = messages_file_load("event_ttk_connect")

            notification("event", message_data["status"], message_data["status_s"], message_data['response'], "", "", "")

            send_discord_webhook({"type_id": "live_start"})

            conected = True

        else:

            message_data = messages_file_load(f"event_ttk_connect")

            notification("event", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

            conected = True

    except Exception as e:

        utils.error_log(e)


def on_disconnect(event):

    event = utils.DictDot(event)

    message_data = messages_file_load("event_ttk_disconected")
    
    notification("live_end", message_data["status"],message_data["status_s"], message_data['response'], "", "", "")

    if main_window_open:
        main_window.evaluate_js(f"update_specs_tiktok('disconect')")

    goaldatabase.reset_goal("diamonds")
    goaldatabase.reset_goal("gift")
    goaldatabase.reset_goal("share")
    goaldatabase.reset_goal("max_viewer")
    goaldatabase.reset_goal("likes")

    send_discord_webhook({"type_id": "live_end"})


def on_comment(event):

    event = utils.DictDot(event)

    username = event.username

    def time_type(format, show, type_data):

        now = datetime.now()

        if show == 1:
            
            if type_data  == "passed":
                
                chat_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                
            elif type_data == "current":
                
                chat_time = now.strftime(format)
        else:

            chat_time = ""

        return chat_time

    def ger_badges():

        badges = []

        if len(badges_list) > 0:

            for badge in badges_list:

                first_url = None
                
                if badge['type'] == "image":

                    if "url" in badge:

                        first_url = badge['url']

                        badge_dict = {
                            "label": "image",
                            "name": "image",
                            "first_url": f"{first_url}",
                        }

                        badges.append(badge_dict)
                
                elif "name" in badge:
                    
                    if badge['name'] == "Moderator":

                        badge_dict = {
                            "label": "Moderator",
                            "name": "Moderator",
                            "first_url": "https://p16-webcast.tiktokcdn.com/webcast-va/moderater_badge_icon.png~tplv-obj.image",
                        }

                        badges.append(badge_dict)
                        
                    if badge['name'] == "New gifter":

                        if "url" in badge:
                        
                            first_url = badge['url']

                            badge_dict = {
                                "label": "New gifter",
                                "name": "New gifter",
                                "first_url": f"{first_url}",
                            }

                            badges.append(badge_dict)


        return badges
            
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

                chat_time = time_type(chat_data["time-format"], chat_data["data-show"], chat_data["type-data"])
                badges = ger_badges()

                
                if top_gifter == None:
                    top_gifter = 0

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
            
            message_data = messages_file_load("event_ttk_like")
            message = utils.replace_all(message_data['response'], { "{nickname}" : display_name, "{username}": username, "{likes}" : likes_send, "{total_likes}" :total_likes })

            show_alert({"type": "like", "message": message, "user_input": "", "profile_pic": profilePictureUrl })

            send_discord_webhook({"type_id": "like", "username" : display_name, "likes_send" : likes_send, "total_likes" : total_likes})

            ttk_alert('like', message)
            
        else:
            
            delay = event_config_data["ttk_like"]["delay"]

            last_like = like_list[userid]

            message_delay, check_time, current = check_delay(delay, last_like)

            if check_time:
                
                if username != "usuarioexemplo":

                    like_list[userid] = current
                    
                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)

                message_data = messages_file_load("event_ttk_like")
                message = utils.replace_all(message_data['response'], { "{nickname}" : display_name, "{username}": username, "{likes}" : likes_send })

                show_alert({"type": "like", "message": message, "user_input": "", "profile_pic": profilePictureUrl })
                
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

                message_data = messages_file_load("event_ttk_join")
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

    def send_gift_not(gift_info, aliases):
        
        message_data = messages_file_load("event_ttk_gift")
        message = utils.replace_all(message_data['response'], aliases)

        global_data = giftsdatabase.get_global_gift()

        global_audio = global_data["audio"]
        global_status = global_data["status"]
        global_volume = global_data["volume"]
        global_video = global_data["video"]
        global_video_status = global_data["video_status"]
        global_video_time = global_data["video_time"]

        if gift_info:

            audio = gift_info["audio"]
            volume = gift_info["volume"]
            status = gift_info["status"]

            video_status = gift_info["video_status"]
            video = gift_info["video"]
            video_time = gift_info["video_time"]

            if int(status) == 1 or int(video_status) == 1:

                if int(status) == 1:

                    notification("gift", message_data["status"],message_data["status_s"], message, audio, volume, "")
                
                if int(video_status) == 1:

                    notification("gift", message_data["status"],message_data["status_s"], message, video, video_time, "")

            elif int(global_status) == 1 or int(global_video_status) == 1:

                if int(global_status) == 1:

                    notification("gift", message_data["status"],message_data["status_s"], message, global_audio, global_volume, "")

                if int(global_video_status) == 1:

                    notification("gift", message_data["status"],message_data["status_s"], message, global_video, global_video_time, "")

        else:

            if global_status == 1:

                notification("gift", message_data["status"],message_data["status_s"], message, global_audio, global_volume, "")
   
            if global_video_status == 1:

                notification("gift", message_data["status"],message_data["status_s"], message, global_video, global_video_time, "")

    def increase_subathon(gift_info, ammount, diamonds):
        
        config_data_subathon = utils.manipulate_json(f"{utils.local_work('appdata_path')}/subathon/config.json", "load")
        time_type = config_data_subathon['time_type']

        if config_data_subathon['status'] == 1:

            if gift_info:
                
                time = gift_info['time']

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

                message_data = messages_file_load("subathon_minutes_add")
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

                message_data = messages_file_load("subathon_minutes_add")
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
      
    event = utils.DictDot(event)

    try:

        goal_data = goaldatabase.get_goal('gift')

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

        gift_info = giftsdatabase.get_gift_data(gift_id)

        aliases = {
            "{nickname}" : display_name,
            "{username}": username,
            "{amount}": giftcount,
            "{giftname}": giftname_br,
            "{diamonds}": gift_diamonds,
            "{id}": gift_id,
        }


        if streakable and not streaking:

            if gift_info:
                
                if gift_info["name_br"] != "":
                    giftname_br = gift_info["name_br"]

                data_discord = {
                    "type_id": "gift", 
                    "username" : display_name, 
                    "gifts_send" : giftcount, 
                    "gift_name" : giftname_br,
                    "diamonds": gift_diamonds
                }

                message_data = messages_file_load("event_ttk_gift")
                message = utils.replace_all(message_data['response'], aliases)

                data_append = {
                    "type": "gift",
                    "message": message,
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }

                if int(gift_id) == int(goal_data["gift"]):
                    
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

                increase_subathon(gift_info, giftcount, diamonds)
                send_gift_not(gift_info, aliases)

                if gift_info['key_status'] == 1:
                    
                    threading.Thread(target=press_keys, args=(gift_info,), daemon=True).start()

            else:

                diamonds = int(gift_diamonds) * int(giftcount)
                
                return_diamonds = update_goal("total_diamonds", diamonds)

                if return_diamonds:

                    update_goal("diamonds", return_diamonds)

                increase_subathon({}, giftcount, diamonds)
                send_gift_not({}, aliases)

        elif not streakable:

            if gift_info:
                
                if gift_info["name_br"] != "":
                    giftname_br = gift_info["name_br"]
            
                discord_data = {
                    "type_id": "gift", 
                    "username" : display_name, 
                    "gifts_send" : giftcount, 
                    "gift_name" : giftname_br,
                    "diamonds": gift_diamonds
                }

                message_data = messages_file_load("event_ttk_gift")
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

                if int(gift_id) == int(goal_data["gift"]):
                    
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

                increase_subathon(gift_info, 1, gift_diamonds)

                send_gift_not(gift_info, aliases)
                
                if gift_info['key_status'] == 1:
                    threading.Thread(target=press_keys, args=(gift_info,), daemon=True).start()

            else:

                diamonds = int(gift_diamonds) * int(giftcount)
                return_diamonds = update_goal("total_diamonds", diamonds)

                if return_diamonds:
                    update_goal("diamonds", return_diamonds)

                increase_subathon({}, 1, gift_diamonds)

                send_gift_not({}, aliases)

    except Exception as e:
        
        utils.error_log(e)


def on_follow(event):
        
    event = utils.DictDot(event)

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

            if username != "usuarioexemplo":

                ttk_follows.append(userid)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/follow.json","save",ttk_follows)

            message_data = messages_file_load("event_ttk_follow")
            message =  utils.replace_all(message_data['response'], { "{nickname}" : display_name, "{username}": username })
        
            update_roles(data_user)

            return_follow = update_goal("total_follow", int(1))

            if return_follow:
                update_goal("follow", int(return_follow))

            show_alert({"type": "follow","message": message,"user_input": "","profile_pic" : profilePictureUrl})

            ttk_alert('follow', message)

            send_discord_webhook({"type_id": "follow", "username" : display_name})

    except Exception as e:
        utils.error_log(e)


def on_share(event):

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
            
            if username != "usuarioexemplo":

                shares_list[userid] = current_time
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json", "save", shares_data)

            message_data = messages_file_load("event_ttk_share")
            message =  utils.replace_all(message_data['response'], aliases)

            data_append = {
                "type": "share",
                "message": message,
                "user_input": "",
                "profile_pic" : profilePictureUrl
            }
            
            show_alert(data_append)
            
            send_discord_webhook({"type_id": "share", "username" : username})

            ttk_alert('share', message)
                
        
        else:

            message_delay, check_time, current = check_delay(event_config_data["ttk_share"]["delay"], shares_list[userid])

            if check_time:
                
                shares_list[userid] = current
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","save", shares_data)

                message_data = messages_file_load("event_ttk_share")
                message =  utils.replace_all(message_data['response'], aliases)

                data_append = {
                    "type": "share",
                    "message":  message,
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }
                
                notification("share", message_data["status"], message_data["status_s"], message,  "", "", "")

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

                    message_data = messages_file_load("event_ttk_envelope")
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

            goal_data = goaldatabase.get_goal('gift')


            if int(gift_id) == int(goal_data["gift"]):
                
                return_gift = update_goal("total_gifts", giftcount)

                if return_gift:

                    update_goal("gift", return_gift)

        elif type_goal == "max_viewer":

            current = goaldatabase.get_current('max_viewer')

            current += 1
        
            return_specs = update_goal("total_specs", int(current))

            if return_specs:

                update_goal("max_viewer", return_specs)

    elif type_id == "like_alert":

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'likes': 1,
            'total_likes': 15,
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'profilePictureUrl': './icon.ico'
        }
            
        on_like(event)

    elif type_id == "follow_alert": 

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'profilePictureUrl': './icon.ico'
        }
            
        on_follow(event)

    elif type_id == "share_alert":

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'profilePictureUrl': './icon.ico'
        }

        on_share(event)

    elif type_id == "test_sound_gift":

        gift_id = data["gift_id"]

        gift_data = json.loads(giftsdatabase.get_gift_info({"id": gift_id}))

        giftname = gift_data["name"]
        gift_diamonds = gift_data["value"]

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'giftId' : gift_id,
            'gift_name': giftname,
            'gift_diamonds' : gift_diamonds,
            'streakable' : False,
            'streaking' : False,
            'giftcount' : 1,
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'profilePictureUrl': './icon.ico'
        }

        on_gift(event)

    elif type_id == "alerts_overlay":


        ttk_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json","load")

        gifts_data = ttk_data["gifts"]

        giftname = gifts_data['5655']["name"]
        gift_diamonds = gifts_data['5655']["value"]

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'giftId' : '5655',
            'gift_name': giftname,
            'gift_diamonds' : gift_diamonds,
            'streakable' : False,
            'streaking' : False,
            'giftcount' : 1,
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'profilePictureUrl': './icon.ico'
        }

        on_gift(event)

    elif type_id == "alerts_video_overlay":

        ttk_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/gifts/gifts.json","load")

        gifts_data = ttk_data["gifts"]

        giftname = gifts_data['5655']["name"]
        gift_diamonds = gifts_data['5655']["value"]

        event = {
            'nickname': 'Usuário de testes',
            'userid': 1234567891011121314,
            'username': 'usuarioexemplo',
            'giftId' : '5655',
            'gift_name': giftname,
            'gift_diamonds' : gift_diamonds,
            'streakable' : False,
            'streaking' : False,
            'giftcount' : 1,
            'is_following': 1,
            'is_moderator': True,
            'is_subscriber': False,
            'profilePictureUrl': './icon.ico'
        }

        on_gift(event)


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
            get_version,
            animation,
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
            ranks_config,
            log_chat,
            camp_command,
            votes,
            highlighted,
            commands_default_py
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
    
    data = {"USERNAME": "", "SESSIONID": "", "error_status": 1}

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

    global userdatabase, commanddatabase, eventlogdatabase, chatlogmanager, giftsdatabase, responsesdatabase, goaldatabase

    def start_log():

        eventlogdatabase.clean_up_events()

        join_list = []
        like_data = {"likes": {}}

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save",join_list)
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)

    if utils.compare_and_insert_keys():

        giftsdatabase = GiftsManager()
        userdatabase = UserDatabaseManager()
        commanddatabase = CommandDatabaseManager()
        eventlogdatabase = EventLogManager()
        chatlogmanager = ChatLogManager()
        goaldatabase = GoalManager()
        responsesdatabase = ResponsesManager()

        responses_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/messages/messages_file.json", "load")
        responsesdatabase.import_responses(responses_data)
        userdatabase.clear_database_without_activity()

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