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
import shutil

from WsClient import WebSocketClient
from sk import WebSocketServer
from lockfile import LockManager
from yt_dlp import DownloadError
from io import BytesIO
from collections import namedtuple
from auth import auth_data
from io import BytesIO
from gtts import gTTS
from tkinter import messagebox
from tkinter import filedialog as fd
from random import randint
from discord_webhook import DiscordWebhook, DiscordEmbed
import pygame

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

global caching, loaded_status, main_window, main_window_open, window_chat_open, window_chat, window_events, window_events_open, server, vibesjsClose

caching = False
loaded_status = False
main_window_open = False
window_chat_open = False
window_events_open = False
vibesjsClose = False

lock_manager = LockManager()
lock_manager.check()

def play_sound(audio, volume):

    convert_vol = int(volume) / 100

    pygame.mixer.music.load(audio)
    pygame.mixer.music.set_volume(convert_vol)
    pygame.mixer.music.play()


def toast(message):

    if main_window_open:
        main_window.evaluate_js(f"toast_notifc('{message}')")


def append_notice(data_receive):

    try:

        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json","load")
        
        now = datetime.datetime.now()

        new_event = {
            "timestamp": str(now),
            "type": data_receive['type'],
            "message": data_receive['message'],
            "user_input": data_receive['user_input']
        }

        event_log_data["event-list"].append(new_event)

        if len(event_log_data["event-list"]) > 100:
            event_log_data["event-list"] = event_log_data["event-list"][-100:]
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json","save",event_log_data)
        

        event_log_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","load")

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json","load")

        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json","load")

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
            "event_list" : event_log_data["event-list"],
        }

        if loaded_status:

            if main_window_open:
                main_window.evaluate_js(f"append_notice({json.dumps(data, ensure_ascii=False)})")
            
            if window_events_open:
                window_events.evaluate_js(f"append_notice_out({json.dumps(data, ensure_ascii=False)})")

            if window_chat_open:
                window_chat.evaluate_js(f"append_notice_chat({json.dumps(data, ensure_ascii=False)})")

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
                
                aliases = {"{url}": f"https://tiktok.com/@{authdata.USERNAME()}/live"}

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


def event_log(data_save):
    
    data_save = json.loads(data_save)
    type_id = data_save['type_id']
    
    if type_id == "get":
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json","load")
        event_log_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","load")

        if event_log_data is not None:

            data = {
                "slider-font-events" : event_log_config_data["slider-font-events"],
                "color-events" : event_log_config_data["color-events"],
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
                "event-list" : event_log_data["event-list"],
            }
            
            return  json.dumps(data, ensure_ascii=False)

    elif type_id == "save":
        
        try:
            
            event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","load")

            event_log_data["slider-font-events"] = data_save["slider-font-events"]
            event_log_data["color-events"] = data_save["color-events"]
            event_log_data["data-show-events"] = data_save["data-show-events"] 

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","save",event_log_data)
            
            toast("Salvo")

        except Exception as e:
            
            utils.error_log(e)
            toast("error")

    elif type_id == "get_state":
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","load")

        event_type =  data_save['type']

        data = {
            "show-event" : event_log_data[f"show-{event_type}"],
            "show-event-html" : event_log_data[f"show-{event_type}-html"],
            "show-event-chat" : event_log_data[f"show-{event_type}-chat"],
            "show-event-alert" : event_log_data[f"show-{event_type}-alert"]
        }

        return  json.dumps(data, ensure_ascii=False)
    
    elif type_id == "save_state":
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","load")

        try:
            event_type = data_save['type']

            event_log_data[f"show-{event_type}"] = data_save["show-event"]
            event_log_data[f"show-{event_type}-html"] = data_save["show-event-html"]
            event_log_data[f"show-{event_type}-chat"] = data_save["show-event-chat"]
            event_log_data[f"show-{event_type}-alert"] = data_save["show-event-alert"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","save",event_log_data)

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

    command_json_path = (f"{utils.local_work('appdata_path')}/config/commands.json")

    if type_rec == "create":
        
        try:
            command = data["command"]
            command_type = data["type"]
            delay = data["delay"]
            user_level = data["user_level"]
            sound = data["sound"]
            cost = data["cost"]
            cost_status = data["cost_status"]

            command_data = utils.manipulate_json(command_json_path, "load")

            if command_data is not None:
                
                command_data[command.lower().strip()] = {
                    "status": 1,
                    "type": command_type,
                    "user_level": user_level,
                    "delay": delay,
                    "sound": sound,
                    "cost" : cost,
                    "cost_status" : cost_status,
                    "last_use": 0,
                }

                utils.manipulate_json(command_json_path, "save", command_data)
                toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_rec == "edit":

        try:
            command = data["command"]
            new_command = data["new_command"]
            status = data["status_command"]
            delay = data["delay"]
            sound = data["sound"]
            user_level = data["user_level"]
            cost = data["cost"]
            cost_status = data["cost_status"]
            command_type = "sound"

            command_data = utils.manipulate_json(command_json_path, "load", None)

            if command_data is not None:

                del command_data[command]

                command_data[new_command] = {
                    "status": status,
                    "type": command_type,
                    "user_level": user_level,
                    "delay": delay,
                    "cost" : cost, 
                    "cost_status" : cost_status, 
                    "last_use": 0,
                    "sound": sound,
                }

                utils.manipulate_json(command_json_path, "save", command_data)
                toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_rec == "delete":
        
        try:
            
            command_data = utils.manipulate_json(command_json_path, "load", None)

            if command_data is not None:
                del command_data[data["command"]]
                
                utils.manipulate_json(command_json_path, "save", command_data)
                
                toast("Comando excluido")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_rec == "get_info":

        try:
            command = data["command"]
            command_data = utils.manipulate_json(command_json_path, "load", None)

            if command_data is not None:

                user_level = command_data[command]["user_level"]
                delay = command_data[command]["delay"]
                status = command_data[command]["status"]
                sound = command_data[command]["sound"]
                type_cmd = command_data[command]["type"]
                cost = command_data[command]["cost"]
                cost_status = command_data[command]["cost_status"]

                data = {
                    "status": status,
                    "type": type_cmd,
                    "edit_command": command,
                    "edit_level": user_level,
                    "edit_delay": delay,
                    "edit_cost" : cost, 
                    "edit_cost_Status" : cost_status, 
                    "sound": sound,
                }

                data_dump = json.dumps(data, ensure_ascii=False)

                return data_dump

        except Exception as e:
            utils.error_log(e)

    elif type_rec == "get_list":

        try:
            command_data = utils.manipulate_json(command_json_path, "load", None)

            if command_data is not None:
                return json.dumps(list(command_data.keys()), ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)

    elif type_rec == "command-list":

        try:

            commands = utils.manipulate_json(command_json_path, "load", None)

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
                f"{utils.local_work('appdata_path')}/config/balance.json",
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


def balance_command(data_receive):
    
    data = json.loads(data_receive)
    type_id = data["type_id"]
    balance_json_path = (f"{utils.local_work('appdata_path')}/config/balance.json")

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
                "giveaway_level": giveaway_data["user_level"],
                "giveaway_clear": giveaway_data["clear"],
                "giveaway_enable": giveaway_data["enable"],
                "giveaway_redeem": giveaway_data["redeem"],
                "giveaway_mult": giveaway_data["allow_mult_entry"],
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

    elif type_id == "save_config":

        try:
            data = json.loads(data_receive)

            giveaway_data_new = {
                "name": data["giveaway_name"],
                "redeem": data["giveaway_redeem"],
                "user_level": data["giveaway_user_level"],
                "clear": data["giveaway_clear_check"],
                "enable": data["giveaway_enable"],
                "allow_mult_entry": data["giveaway_mult"],
            }

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)

            if giveaway_data["enable"] == 1 and data["giveaway_enable"] == 0:

                aliases = {
                    "{giveaway_name}": giveaway_data["name"],
                }

                response = utils.replace_all(utils.messages_file_load("giveaway_status_disable"), aliases)

                toast(response)

            utils.manipulate_json(giveaway_config_path, "save", giveaway_data_new)

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)

            if giveaway_data["enable"] == 1:

                aliases = {
                    "{giveaway_name}": giveaway_data["name"],
                    "{redeem}": giveaway_data["redeem"],
                }

                response = utils.replace_all(utils.messages_file_load("giveaway_status_enable"), aliases)

                toast(response)

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

        data = json.loads(data_receive)

        new_name = data["new_name"]
        user_level = data["user_level"]

        def check_perm(user_level, command_level):

            levels = [
                "spec",
                "regular",
                "top_chatter",
                "vip",
                "subs",
                "mod",
                "streamer",
            ]

            return levels.index(user_level) >= levels.index(command_level)

        try:

            def append_name(new_name):

                giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)
                giveaway_name_data.append(new_name)

                utils.manipulate_json(giveaway_names_path, "save", giveaway_name_data)

                back_giveaway_name_data = utils.manipulate_json(giveaway_backup_path, "load", None)
                back_giveaway_name_data.append(new_name)

                utils.manipulate_json(giveaway_backup_path,"save",back_giveaway_name_data)

                aliases = {"{username}": new_name}

                data_append = {
                    "type": "event",
                    "message": utils.replace_all(utils.messages_file_load("giveaway_response_user_add"), aliases),
                    "user_input": "",
                }

                append_notice(data_append)

                toast(f"O usuário {new_name} foi adicionado na lista")

            giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)
            giveaway_config_data = utils.manipulate_json(giveaway_config_path, "load", None)

            if giveaway_config_data["enable"] == 1:

                giveaway_perm = giveaway_config_data["user_level"]
                giveaway_mult_config = giveaway_config_data["allow_mult_entry"]

                aliases = {"{username}": str(new_name), "{perm}": str(giveaway_perm)}

                if giveaway_mult_config == 0:

                    if new_name in giveaway_name_data:

                        toast(utils.replace_all(utils.messages_file_load("giveaway_response_mult_add"),aliases))

                    else:
                        if check_perm(user_level, giveaway_perm):

                            append_name(new_name)

                        else:
                            toast(utils.replace_all(utils.messages_file_load("giveaway_response_perm"),aliases))
                else:
                    if check_perm(user_level, giveaway_perm):

                        append_name(new_name)

                    else:
                        toast(utils.replace_all(utils.messages_file_load("giveaway_response_perm"),aliases))
            else:

                giveaway_perm = giveaway_config_data["user_level"]

                aliases = {"{username}": str(new_name), "{perm}": str(giveaway_perm)}

                data_append = {
                    "type": "event",
                    "message": utils.replace_all(utils.messages_file_load("giveaway_status_disabled"), aliases),
                    "user_input": "",
                }

                append_notice(data_append)

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "execute":
        
        try:

            giveaway_data = utils.manipulate_json(giveaway_config_path, "load", None)
            giveaway_name_data = utils.manipulate_json(giveaway_names_path, "load", None)

            reset_give = giveaway_data["clear"]
            name = random.choice(giveaway_name_data)

            utils.manipulate_json(giveaway_backup_path, "save", giveaway_name_data)
            utils.manipulate_json(giveaway_result_path, "save", [name])

            if reset_give == 1:

                reset_data = []

                utils.manipulate_json(giveaway_names_path, "save", reset_data)

            toast(f"{name} Ganhou o sorteio!")

        except Exception as e:
            utils.error_log(e)
            toast("Erro ao executar o sorteio")

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

        data = {"queue": queue_data}

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "queue_add":

        queue_data = utils.manipulate_json(json_path, "load")
        
        if data_receive not in queue_data:

            queue_data.append(data_receive)

            utils.manipulate_json(json_path, "save", queue_data)

            toast("Nome adicionado")

            aliases = {"{value}": str(data_receive)}

            data_append = {
                "type": "event", 
                "message": utils.replace_all(str(utils.messages_file_load("response_add_queue")), aliases), 
                "user_input": ""
            }

            append_notice(data_append)

        else:

            aliases = {"{value}": str(data_receive)}

            data_append = {
                "type": "event", 
                "message": utils.replace_all(str(utils.messages_file_load("response_namein_queue")), aliases), 
                "user_input": ""
            }

        queue_data = utils.manipulate_json(json_path, "load")

        return json.dumps(queue_data, ensure_ascii=False)

    elif type_id == "queue_rem":

        queue_data = utils.manipulate_json(json_path, "load")
        
        if data_receive in queue_data:

            queue_data.remove(data_receive)

            utils.manipulate_json(json_path, "save", queue_data)

            aliases = {"{value}": str(data_receive)}

            data_append = {
                "type": "event", 
                "message": utils.replace_all(str(utils.messages_file_load("response_rem_queue")), aliases), 
                "user_input": ""
            }

            append_notice(data_append)

        else:

            aliases = {"{value}": str(data_receive)}

            data_append = {
                "type": "event", 
                "message": utils.replace_all(str(utils.messages_file_load("response_noname_queue")), aliases), 
                "user_input": ""
            }

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


def not_config_py(data_receive, type_id, type_not):

    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")

    if type_id == "get":

        file_data = event_config_data[type_not]

        data = {"not": file_data["status"], "response_chat": file_data["response_chat"]}

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save":

        try:
            data = json.loads(data_receive)

            event_config_data[type_not]["status"] = data["not"]
            event_config_data[type_not]["response_chat"] = data["response_chat"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "save", event_config_data)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")


def messages_config(type_id, data_receive):

    json_path = f"{utils.local_work('appdata_path')}/config/commands_config.json"
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


def responses_config(type_id, response_key, message):

    json_path = f"{utils.local_work('appdata_path')}/messages/messages_file.json"
    
    if type_id == "get_response":

        responses_data = utils.manipulate_json(json_path, "load")
        return responses_data.get(response_key, "")

    elif type_id == "save_response":
        try:
            responses_data = utils.manipulate_json(json_path, "load")
            responses_data[response_key] = message

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
            "likes_bg": config_data["likes_bg"],
            "likes_op": config_data["likes_op"],
            "gifts_bg": config_data["gifts_bg"],
            "gifts_op": config_data["gifts_op"],
            "shares_bg": config_data["shares_bg"],
            "shares_op": config_data["shares_op"],
            "points_bg": config_data["points_bg"],
            "points_op": config_data["points_op"]
        }

        return  json.dumps(data, ensure_ascii=False)

    elif type_id == "save":

        try:

            config_data["status"] = data_receive['status']
            config_data["interval"] = data_receive['interval']
            config_data["likes_bg"] = data_receive['likes_bg']
            config_data["likes_op"] = data_receive['likes_op']
            config_data["gifts_bg"] = data_receive['gifts_bg']
            config_data["gifts_op"] = data_receive['gifts_op']
            config_data["shares_bg"] = data_receive['shares_bg']
            config_data["shares_op"] = data_receive['shares_op']
            config_data["points_bg"] = data_receive['points_bg']
            config_data["points_op"] = data_receive['points_op']

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "save",config_data)

            toast("success")

        except Exception as e:

            toast("error")
            utils.error_log(e)


def tiktok_auth(data_receive):

    data_receive = json.loads(data_receive)
    auth_json_path = f"{utils.local_work('appdata_path')}/auth/auth.json"

    data = utils.manipulate_json(auth_json_path, "load")

    data["USERNAME"] = data_receive["username"]
    data["SESSIONID"] = data_receive["sessionid"]

    utils.manipulate_json(auth_json_path, "save", data)

    WEBHOOKURL = os.getenv('WEBHOOKURL')
    webhook_login = DiscordWebhook(url=WEBHOOKURL)

    embed_login = DiscordEmbed(
        title='Nova autenticação - TikTok',
        description= F'https://www.tiktok.com/@{data_receive["username"]}' ,
        color= '03b2f8'
    )

    embed_login.set_author(name=data_receive["username"], url=f'https://www.twitch.tv/{data_receive["username"]}')
    
    webhook_login.add_embed(embed_login)
    webhook_login.execute() 

    start_websocket_CS()
        
    return True


def tiktok_alerts(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    event_config_json_path = f"{utils.local_work('appdata_path')}/config/event_not.json"

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

    ttk_data_gifts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json", "load")

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

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json", "save", ttk_data_gifts)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")

    elif type_id == "save_point_gift":

        try:

            gift_id = data_receive["id"]

            ttk_data_gifts["gifts"][gift_id]["points-global"] = data_receive["status"]
            ttk_data_gifts["gifts"][gift_id]["points"] = data_receive["points"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json", "save", ttk_data_gifts)

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
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "global_gift_save":

        try:

            ttk_data_gifts["status"] = data_receive["status"]
            ttk_data_gifts["audio"] = data_receive["sound"]
            ttk_data_gifts["volume"] = data_receive["volume"]

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json", "save", ttk_data_gifts)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def tiktok_logs(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    event_config_path = f"{utils.local_work('appdata_path')}/config/event_not.json"

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

            ttk_data_gifts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json", "load")

            gift_list = []

            for key, value in ttk_data_gifts["gifts"].items():
                gift_list.append({"id": value["id"], "name": value["name_br"]})

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

            if goal_type == "max_viewer":
                current = goal_data[goal_type][f"total_viewer"]
            else:
                current = goal_data[goal_type][f"total_{goal_type}"]

            data_goal = {
                "type": "update_goal",
                "type_goal": goal_type,
                "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
                "current": int(current),
                "goal": int(data["goal"]), 
            }

            server.broadcast_message(json.dumps(data_goal))
        

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    if type_id == "save_html":
        
        try:
            
            toast('Salvo')
            
            return utils.update_goal(data)
            
        except Exception as e:
            
            toast('erro')
            utils.error_log(e)

    if type_id == "get_html":
        
        html_info = utils.update_goal(data)
        data_dump = json.dumps(html_info, ensure_ascii=False)
        return data_dump


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

            if version != "1.3.0":
                
                return True

            else:
                return False
        except:
            
            return False

    elif type_id == "open":

        url = "https://github.com/GGTEC/VibesBot/releases"
        webbrowser.open(url, new=0, autoraise=True)


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

            data_append = {
                "type": "music",
                "message": utils.replace_all(utils.messages_file_load("music_process_error"), aliases),
                "user_input": "",
            }

            append_notice(data_append)

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
                }
                if main_window_open:
                    main_window.evaluate_js(f"player('play', 'http://localhost:7000/src/player/cache/music.webm', '1')")

                toast(f"Reproduzindo {music_name_short} - {music_artist}")

                data_append = {
                    "type": "music",
                    "message": utils.replace_all(utils.messages_file_load("music_playing"), aliases),
                    "user_input": "",
                }

                append_notice(data_append)


                config_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "load")

                config_data_player["skip_requests"] = 0

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json", "save", config_data_player)

                caching = False
                
            else:
                
                caching = False
                
                toast(f"Erro ao processar música {link} - {user}")

                data_append = {
                    "type": "music",
                    "message": utils.replace_all(utils.messages_file_load("music_process_cache_error"), aliases),
                    "user_input": "",
                }

                append_notice(data_append)

    except Exception as e:
        
        utils.error_log(e)

        toast(f"Erro ao processar música {link} - {user}")

        data_append = {
            "type": "music",
            "message": utils.replace_all(utils.messages_file_load("music_process_cache_error"), {"{username}": user}),
            "user_input": "",
        }

        append_notice(data_append)

        caching = False


def loopcheck():
    
    while True:

        try:

            playlist_path = f"{utils.local_work('appdata_path')}/player/list_files/playlist.json"
            queue_path = f"{utils.local_work('appdata_path')}/player/list_files/queue.json"
            config_path = f"{utils.local_work('appdata_path')}/player/config/config.json"
            
            if loaded_status and main_window_open:
                
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


def music_process(user_input, redem_by_user):
    
    user_input = user_input.strip()
    
    config_music_path = F"{utils.local_work('appdata_path')}/player/config/config.json"
    queue_json_path = F"{utils.local_work('appdata_path')}/player/list_files/queue.json"

    config_music_data = utils.manipulate_json(config_music_path, 'load')
    queue_data = utils.manipulate_json(queue_json_path, 'load')
    
    blacklist = config_music_data["blacklist"]
    max_duration = int(config_music_data["max_duration"])

    last_key = str(max(map(int, queue_data.keys()), default=0) + 1) if queue_data else "1"

    def start_process(user_input):
        
        try:
            toast(f"Processando pedido {user_input} - {redem_by_user}")

            if not any(item in user_input for item in blacklist):

                response = get_video_info(user_input)

                if response == "404":

                    data_append = {
                        "type": "music",
                        "message": utils.replace_all(utils.messages_file_load("music_process_error"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)
                
                else:

                    music_name, video_url, music_length = response.title, response.url, response.length

                    if music_length < max_duration:

                        queue_data[last_key] = {
                            "MUSIC": video_url,
                            "USER": redem_by_user, 
                            "MUSIC_NAME": music_name
                        }

                        utils.manipulate_json(queue_json_path, 'save', queue_data)

                        aliases = {
                            "{username}": redem_by_user, 
                            "{user_input}": video_url, 
                            "{music}": music_name
                        }
                        
                        data_append = {
                            "type": "music", 
                            "message": utils.replace_all(utils.messages_file_load("music_added_to_queue"), aliases), 
                            "user_input": ""
                        }

                        append_notice(data_append)

                    else:

                        music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")

                        aliases = {
                            "{max_duration}": str(max_duration), 
                            "{username}": str(redem_by_user),
                            "{user_input}": str(user_input),
                            "{music}": str(music_name),
                            "{music_short}": str(music_name_short)
                        }
                        
                        data_append = {
                            "type": "music", 
                            "message": utils.replace_all(utils.messages_file_load("music_length_error"), aliases), 
                            "user_input": ""
                        }
                        append_notice(data_append)

            else:

                music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")
                aliases = {
                    "{username}": str(redem_by_user),
                    "{user_input}": str(user_input),
                    "{music}": str(music_name),
                    "{music_short}": str(music_name_short)
                }
                
                data_append = {
                    "type": "music",
                    "message": utils.replace_all(utils.messages_file_load("music_blacklist"), aliases), 
                    "user_input": ""
                }
                append_notice(data_append)

        except Exception as e:

            utils.error_log(e)

            aliases = {
                "{username}": str(redem_by_user), 
                "{user_input}": str(user_input)
            }

            data_append = {
                "type": "music", 
                "message": utils.replace_all(utils.messages_file_load("music_add_error"), aliases), 
                "user_input": ""
            }

            append_notice(data_append)

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
            data_append = {
                "type": "music", 
                "message": utils.messages_file_load("music_link_youtube"),
                "user_input": ""
            }
            append_notice(data_append)
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
        
        file = f"{utils.local_work('appdata_path')}/error_log.txt"

        with open(file, "r", encoding="utf-8") as error_file:
            error_data = error_file.read()

        return error_data

    elif type_id == "errolog_clear":
        
        file = f"{utils.local_work('appdata_path')}/error_log.txt"

        with open(file, "w", encoding="utf-8") as error_file:
            error_file.write("")

        toast("Relatório de erros limpo")

    elif type_id == "discord":
        webbrowser.open("https://discord.gg/utm5NZq", new=0, autoraise=True)

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


def chat_config(data_save, type_config):

    chat_file_path = f"{utils.local_work('appdata_path')}/config/chat_config.json"

    points_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/points.json","load")

    if type_config == "save":

        try:

            chat_data = utils.manipulate_json(chat_file_path, "load")

            data_received = json.loads(data_save)

            chat_data.update({
                "chat-color-name": data_received["chat_color_name"],
                "chat-color-border": data_received["chat_color_border"],
                "chat-name-select": data_received["chat_name_select"],
                "chat-border-select": data_received["chat_border_select"],
                "data-show": data_received["data_show"],
                "type-data": data_received["type_data"],
                "time-format": data_received["time_format"],
                "font-size": data_received["font_size"],
                "gift-role": data_received["gift_role"],
                "like-role": data_received["like_role"],
                "share-role": data_received["share_role"],
                "gift-points": data_received["gift_points"],
                "like-points": data_received["like_points"],
                "share-points": data_received["share_points"],
                "follow-points": data_received["follow_points"],
                "show-user-picture": data_received["show_profile_pic"]
            })

            points_data_load.update({
                "gifts": float(data_received["gift_points"]),
                "likes": float(data_received["like_points"]),
                "shares": float(data_received["share_points"]),
                "follow": float(data_received["follow_points"])
            })

            utils.manipulate_json(chat_file_path, "save", chat_data)
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/points.json", "save", points_data_load)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_config == "get":

        chat_data = utils.manipulate_json(chat_file_path, "load")
        points_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/points.json","load")
        
        chat_data_return = {
            "chat_color_name": chat_data.get("chat-color-name"),
            "chat_color_border": chat_data.get("chat-color-border"),
            "chat_name_select": chat_data.get("chat-name-select"),
            "chat_border_select": chat_data.get("chat-border-select"),
            "time_format": chat_data.get("time-format"),
            "type_data": chat_data.get("type-data"),
            "data_show": chat_data.get("data-show"),
            "font_size": chat_data.get("font-size"),
            "wrapp_message": chat_data.get("wrapp-message"),
            "gift_role": chat_data.get("gift-role"),
            "like_role": chat_data.get("like-role"),
            "share_role": chat_data.get("share-role"),
            "show_profile_pic" : chat_data.get("show-user-picture"), 
            "gift_points": points_data_load.get("gifts"),
            "like_points": points_data_load.get("likes"),
            "share_points": points_data_load.get("shares"),
            "follow_points": points_data_load.get("follow")
        }
        
        return json.dumps(chat_data_return, ensure_ascii=False)


def userdata_py(type_id, username):

    user_data_file_path = f"{utils.local_work('appdata_path')}/user_info/users_database.json"

    if type_id == "get":

        return json.dumps(utils.manipulate_json(user_data_file_path, "load"), ensure_ascii=False)

    elif type_id == "load":

        user_data_load = utils.manipulate_json(user_data_file_path, "load")

        if username in user_data_load:

            user_info = user_data_load[username]

            username = user_info["display_name"]

            roles = user_info.get("roles", "Null")
            likes = user_info.get("likes", "Null")
            shares = user_info.get("shares", "Null")
            gifts = user_info.get("gifts", "Null")

        else:

            roles = likes = shares = gifts = "Null"

        data = {
            "username": username,
            "roles": roles,
            "likes": likes,
            "shares": shares,
            "gifts": gifts,
        }

        result = namedtuple("result", data.keys())(*data.values())

        return result

    elif type_id == "remove":

        try:

            user_data_load = utils.manipulate_json(user_data_file_path, "load")

            if username in user_data_load:

                del user_data_load[username]
                
                utils.manipulate_json(user_data_file_path, "save", user_data_load)

                toast("Nome removido")

                return True
            
        except Exception as e:

            toast("erro")
            utils.error_log(e)
        
            return True

    elif type_id == "save":

        try:
            userdata = utils.manipulate_json(user_data_file_path, "load")

            data_received = json.loads(username)
            
            userdata[data_received["userid"]] = {
                "display_name": data_received["username"],
                "roles": data_received["roles"],
                "likes": data_received["likes"],
                "shares": data_received["shares"],
                "gifts": data_received["gifts"],
                "points" : data_received["points"],
                "profile_pic" : user_data_file_path[data_received["userid"]]["profile_pic"],
            }

            utils.manipulate_json(user_data_file_path, "save",userdata)

            toast("success")

        except Exception as e:

            toast("erro")
            utils.error_log(e)

    elif type_id == "backup":
         
        try:

            user_data_load = utils.manipulate_json(user_data_file_path, "load")

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database_backup.json", "save", user_data_load)


        except Exception as e:
            utils.error_log(e)

    elif type_id == "restore_backup":

        try:
            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database_backup.json",'load')
            
            with open(user_data_file_path, 'w', encoding='utf-8') as or_file:
                json.dump(user_data_load, or_file, indent=4)

        except Exception as e:
            utils.error_log(e)


def commands_module(data) -> None:

    def check_cost(user, cost, status):

        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")

        if status:

            value_user = float(user_data_load[user]["points"])

            if float(value_user) >= float(cost):

                value_user = float(value_user) - float(cost)
                user_data_load[user]["points"] = value_user

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","save",user_data_load)

                return True
            else:
                return False
        else:
            return True

    def give_balance(user, cost):

        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")

        value_user = float(user_data_load[user]["points"])

        value_user = float(value_user) + float(cost)
        user_data_load[user]["points"] = value_user

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","save",user_data_load)

        return True

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

    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")
    command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json","load")
    command_data_prefix = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands_config.json","load")
    command_data_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","load")
    command_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","load")
    command_data_queue = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","load")
    command_data_tts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/tts.json","load")
    command_data_balance = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/balance.json","load")

    user = data["user_id"]
    message_text = data["message"]
    username = data["user_name"]

    user_roles = user_data_load[user]["roles"]

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
        "{user_id}" : str(user),
        "{command}": str(command),
        "{prefix}": str(prefix),
        "{sufix}": str(sufix),
        "{random}": str(random_value),
        "{value}": str(sufix),
    }

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
            '{username}': str(user),
            '{user_level}' : str(user_level_string),
            '{command}' : str(command)
        }

        message_error = utils.replace_all(utils.messages_file_load('error_user_level'),aliases)
        
        data_append = {
            "type": "command",
            "message": message_error,
            "user_input": sufix,
        }

        append_notice(data_append)

    def check_status(command_info, aliases):

        user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")

        data_append = {
            "type": "command",
            "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
            "user_input": sufix,
        }

        append_notice(data_append)
    
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
                        
                        if check_cost(user, cost, cost_status):
                            
                            return current, 'None', True,  'ok'
                        
                        else:
                            value_user = int(user_data_load[user]["points"])

                            aliases = {
                                "{cost}" : str(cost),
                                "{username}" : str(username),
                                "{balance}" : str(value_user)
                            }
                                                        
                            message_error = utils.replace_all(utils.messages_file_load("command_cost"), aliases)

                            return current, message_error, False, 'cost'
                else:

                    message_error = message_delay

                    return current, message_error, False, 'delay'
                
            else:

                aliases = {
                    "{username}": str(user),
                    "{user_level}": str(user_level),
                    "{command}": str(command),
                }


                message_error = utils.replace_all(utils.messages_file_load("error_user_level"), aliases)

                return current, message_error, False, 'level'

        else:
            
            message_error = utils.replace_all(utils.messages_file_load("command_disabled"), aliases)

            return current, message_error, False, 'disabled'

    def play_sound():
        
        audio_path = command_data[command]["sound"]
        audio_volume = "50"

        convert_vol = int(audio_volume) / 100

        tts_playing = pygame.mixer.music.get_busy()

        while tts_playing:
            tts_playing = pygame.mixer.music.get_busy()
            time.sleep(2)

        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.set_volume(convert_vol)
        pygame.mixer.music.play()
    
    if status_commands == 1:

        if command in command_data:

            command_info = command_data[command]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                    
                if command_info["type"] == "sound":
                    play_sound()

                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/commands.json","save",command_data)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)
                
        elif compare_strings(command, command_data_giveaway["add_user"]["command"]):

            command_info = command_data_giveaway["add_user"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix != "":

                    user_input = sufix

                    data = {"new_name": user_input.strip(), "user_level": "mod"}
                    giveaway_py("add_user", data)

                else:

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)

                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/giveaway/commands.json","save",command_data_giveaway)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

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
                                "{username}": str(user),
                                "{volume}": str(volume_value_int),
                            }

                            data_append = {
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("command_volume_confirm"),aliases_commands),
                                "user_input": "",
                            }

                            append_notice(data_append)

                        else:
                            
                            aliases_commands = {
                                "{username}": user,
                                "{volume}": str(volume_value_int),
                            }

                            data_append = {
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("command_volume_error"),aliases_commands),
                                "user_input": "",
                            }

                            append_notice(data_append)

                    else:

                        data_append = {
                            "type": "command",
                            "message": utils.messages_file_load("command_volume_number"),
                            "user_input": "",
                        }

                        append_notice(data_append)

                else:

                    if main_window_open:
                        volume_atual = main_window.evaluate_js(
                            f"player('get_volume', 'none', 'none')"
                        )

                    aliases_commands = {
                        "{username}": str(user),
                        "{volume}": str(volume_atual),
                    }

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_volume_response"),aliases_commands),
                        "user_input": "",
                    }

                    append_notice(data_append)

                command_info["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

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

                        aliases_commands = {
                            "{username}": str(user),
                        }

                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(utils.messages_file_load("command_skip_confirm"),aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)

                        command_data_player["skip"]["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)

                        config_data_player["skip_requests"] = 0

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player)

                    else:
                        if not user in skip_users:

                            skip_requests = int(skip_requests) + 1

                            aliases_commands = {
                                "{username}": str(user),
                                "{votes}": str(skip_requests),
                                "{minimum}": str(skip_votes),
                            }

                            data_append = {
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("skip_votes"),aliases_commands),
                                "user_input": "",
                            }

                            append_notice(data_append)

                            if int(skip_requests) == skip_votes:

                                if main_window_open:
                                    main_window.evaluate_js(f"player('stop', 'none', 'none')")

                                aliases_commands = {
                                    "{username}": str(user),
                                }

                                data_append = {
                                    "type": "command",
                                    "message": utils.replace_all(utils.messages_file_load("command_skip_confirm"),aliases_commands),
                                    "user_input": "",
                                }

                                append_notice(data_append)

                                command_data_player["skip"]["last_use"] = current

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player,)

                                config_data_player["skip_requests"] = 0
                                config_data_player["skip_users"] = []

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player)

                            else:

                                skip_users.append(user)

                                config_data_player["skip_users"] = skip_users
                                config_data_player["skip_requests"] = int(skip_requests)

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/config.json","save",config_data_player,)

                        else:
                            aliases_commands = {
                                "{username}": str(user),
                            }

                            data_append = {
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("command_skip_inlist"),aliases_commands),
                                "user_input": "",
                            }

                            append_notice(data_append)

                            command_data_player["skip"]["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player,)

                else:
                    
                    aliases_commands = {
                        "{username}": str(user),
                    }

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_skip_noplaying"),aliases_commands),
                        "user_input": "",
                    }

                    append_notice(data_append)

                    command_data_player["skip"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)
            
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)
        
        elif compare_strings(command, command_data_player['request']['command']):

            command_info = command_data_player['request']

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                prefix_sr = command_data_player['request']['command']
                user_input = command_string.split(prefix_sr)

                if len(user_input) > 1 and user_input[1] != "":
                    
                    user_input = user_input[1]
                    
                    if sr_config_py('get-status','null') == 1:

                        threading.Thread(target=music_process, args=(user_input, username,), daemon=True).start()
                        
                    else:
                        
                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(utils.messages_file_load('music_disabled'), aliases),
                            "user_input": sufix,
                        }
                        
                        append_notice(data_append)
                    
                        command_data_player['request']['last_use'] = current
                        
                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json","save",command_data_player)
                        

                else:

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(str(utils.messages_file_load("command_value")), aliases),
                        "user_input": sufix,
                    }
                    
                    append_notice(data_append)

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_player['atual']['command']):

            command_info = command_data_player['atual']

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
                           
                f = open(f"{utils.local_work('appdata_path')}/player/list_files/currentsong.txt", "r+", encoding="utf-8")
                current_song = f.read()

                aliases_commands = {'{username}': str(user), '{music}': str(current_song)}

                data_append = {
                    "type": "command",
                    "message": utils.replace_all(utils.messages_file_load('command_current_confirm'),aliases_commands),
                    "user_input": sufix,
                }

                append_notice(data_append)
                    
                command_data_player['atual']['last_use'] = current
        
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

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
                        '{username}': str(user),
                        '{music}': str(next_song),
                        '{request_by}': str(resquest_by)
                    }

                    data_append = {
                        "type": "command",
                        "message":  utils.replace_all(utils.messages_file_load('command_next_confirm'), aliases_commands),
                        "user_input": sufix,
                    }

                    append_notice(data_append)

                elif check_playlist:

                    playlist_keys = [int(x) for x in playlist_data.keys()]
                    min_key_playlist = min(playlist_keys)
                    min_key_playlist_str = str(min_key_playlist)

                    next_song = playlist_data[min_key_playlist_str]['MUSIC_NAME']
                    resquest_by = playlist_data[min_key_playlist_str]['USER']

                    aliases_commands = {
                        '{username}': str(user),
                        '{music}': str(next_song),
                        '{request_by}': str(resquest_by)
                    }

                    data_append = {
                        "type": "command",
                        "message":  utils.replace_all(utils.messages_file_load('command_next_confirm'), aliases_commands),
                        "user_input": sufix,
                    }

                    append_notice(data_append)

                else:

                    aliases_commands = {
                        '{username}': str(user),
                    }

                    data_append = {
                        "type": "command",
                        "message":  utils.replace_all(utils.messages_file_load('command_next_no_music'), aliases_commands),
                        "user_input": sufix,
                    }

                    append_notice(data_append)
                            
                command_data_player['next']['last_use'] = current
        
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/player/config/commands.json", "save", command_data_player)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_queue["add_queue"]["command"]):
            
            command_info = command_data_queue["add_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    command, username = re.split(r'\s+', message_text, maxsplit=1)
            
                    queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")
                    
                    queue_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/config.json","load")
                    
                    user_found = next((user for user, data in user_data_load.items() if data["display_name"] == username), None)
                    
                    if user_found:

                        usercheck_username = user_data_load[user_found]["display_name"]

                        if usercheck_username not in queue_data:

                            if queue_config['spend_user_balance'] == 1:

                                cost = command_data_queue["self_add_queue"]["cost"]

                                check = check_cost(user_found, cost, 1)

                                if check:
                                        
                                        queue_data.append(usercheck_username)

                                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                                        toast("Nome adicionado")

                                        data_append = {
                                            "type": "command",
                                            "message": utils.replace_all(utils.messages_file_load("response_add_queue"),aliases),
                                            "user_input": "",
                                        }

                                        append_notice(data_append)
                                else:

                                    data_append = {
                                        "type": "command",
                                        "message": utils.replace_all(utils.messages_file_load("balance_user_insuficient"),aliases),
                                        "user_input": "",
                                    }

                                    append_notice(data_append)


                            else:

                                queue_data.append(usercheck_username)

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                                toast("Nome adicionado")

                                data_append = {
                                    "type": "command",
                                    "message": utils.replace_all(utils.messages_file_load("response_add_queue"),aliases),
                                    "user_input": "",
                                }

                                append_notice(data_append)

                        else:

                            toast("O nome já está na lista")

                            data_append = {
                                "type": "command",
                                "message": utils.messages_file_load("response_namein_queue"),
                                "user_input": "",
                            }

                            append_notice(data_append)
                    else:

                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(utils.messages_file_load("balance_user_not_found"),aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)
                        
                    command_data_queue["add_queue"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

                else:

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_queue["self_add_queue"]["command"]):
            
            command_info = command_data_queue["self_add_queue"]
            
            queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")
            
            if username not in queue_data:

                current, message_error, status, type_error = check_status(command_info, aliases)

                if status:

                    queue_data.append(username)

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","save",queue_data)

                    toast("Nome adicionado")

                    if main_window_open:
                        main_window.evaluate_js(f"queue_js('get',Null)")

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("response_queue"),aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)

                    command_data_queue["self_add_queue"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

                else:

                    if type_error == "level":

                        send_error_level(command_info)

                    else:

                        data_append = {
                            "type": "command",
                            "message": message_error,
                            "user_input": sufix,
                        }

                        append_notice(data_append)

            else:

                toast("O nome já está na lista")
                
                data_append = {
                    "type": "command",
                    "message": utils.replace_all(utils.messages_file_load("response_namein_queue"),aliases),
                    "user_input": "",
                }

                append_notice(data_append)

        elif compare_strings(command, command_data_queue["check_queue"]["command"]):

            command_info = command_data_queue["check_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
            
                queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")

                response = utils.replace_all(str(utils.messages_file_load("response_get_queue")), aliases)

                match = re.search(r'\{queue-(\d*)\}', response)

                if match:

                    number = match.group(1)

                    response = response.replace(match.group(0), ', '.join(queue_data[:int(number)]))


                data_append = {
                    "type": "command",
                    "message": response,
                    "user_input": "",
                }

                append_notice(data_append)

                command_data_queue["check_queue"]["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}queue/commands.json","save",command_data_queue)

            else:
                
                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_queue["rem_queue"]["command"]):

            command_info = command_data_queue["rem_queue"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:
         
                if sufix:

                    command, username = re.split(r'\s+', message_text, maxsplit=1)

                    user_found = next((user for user, data in user_data_load.items() if data["display_name"] == username), None)

                    if user_found:

                        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/queue.json","load")
                        
                        usercheck_username = user_data_load[user_found]["display_name"]

                        if usercheck_username in queue_data:

                            queue_data.remove(usercheck_username)

                            utils.manipulate_json( f"{utils.local_work('appdata_path')}/queue/queue.json","save", queue_data)

                            data_append = {
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("response_rem_queue"), aliases),
                                "user_input": "",
                            }

                            append_notice(data_append)

                        else:
                            toast("O nome não está na lista")

                            data_append = {
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("response_noname_queue"), aliases),
                                "user_input": "",
                            }

                            append_notice(data_append)

                    command_data_queue["rem_queue"]["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/queue/commands.json","save",command_data_queue)

                else:

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_tts["command"]):

            command_info = command_data_tts

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix != None:
                    
                    message_prefix = utils.replace_all(utils.messages_file_load("tts_prefix"), aliases)

                    if command_info['prefix']:
                        sufix = sufix + message_prefix

                    user_input_short = textwrap.shorten(sufix, width=300, placeholder=" ")
                    tts = gTTS(text=user_input_short, lang="pt", slow=False)

                    mp3_fp = BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)

                    tts_playing = pygame.mixer.music.get_busy()

                    while tts_playing:
                        tts_playing = pygame.mixer.music.get_busy()
                        time.sleep(2)

                    pygame.mixer.music.load(mp3_fp, "mp3")
                    pygame.mixer.music.play()

                    command_data_tts["last_use"] = current

                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/tts.json", command_data_tts, "save")

                else:

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("error_tts_no_text"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)

            
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_balance["user_balance"]["command"]):

            command_info = command_data_balance["user_balance"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                likes = user_data_load[user]["likes"]
                gifts = user_data_load[user]["gifts"]
                shares = user_data_load[user]["shares"]
                points = user_data_load[user]["points"]

                aliases_balance = {
                    "{likes}" : likes,
                    "{gifts}" : gifts,
                    "{shares}" : shares,
                    "{points}" : points
                }

                response = utils.replace_all(utils.messages_file_load("balance"), aliases)
                response = utils.replace_all(response, aliases_balance)

                data_append = {
                    "type": "command",
                    "message": response,
                    "user_input": "",
                }

                append_notice(data_append)

                command_data_tts["last_use"] = current

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/balance.json", command_data_balance, "save")

        
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_balance["mod_balance"]["command"]):

            command_info = command_data_balance["mod_balance"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                if sufix:

                    command, username = re.split(r'\s+', message_text, maxsplit=1)

                    user_found = next((user for user, data in user_data_load.items() if data["display_name"] == username), None)

                    if user_found:

                        usercheck_username = user_data_load[user_found]["display_name"]
                        likes = user_data_load[user_found]["likes"]
                        gifts = user_data_load[user_found]["gifts"]
                        shares = user_data_load[user_found]["shares"]
                        points = user_data_load[user_found]["points"]

                        aliases_balance = {
                            "{usercheck}" : usercheck_username,
                            "{likes}" : likes,
                            "{gifts}" : gifts,
                            "{shares}" : shares,
                            "{points}" : points
                        }

                        response = utils.replace_all(utils.messages_file_load("balance_moderator"), aliases)
                        response = utils.replace_all(response, aliases_balance)

                        data_append = {
                            "type": "command",
                            "message": response,
                            "user_input": "",
                        }

                        append_notice(data_append)

                        command_data_tts["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/balance.json", command_data_balance, "save")

                    else:

                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(utils.messages_file_load("balance_user_not_found"), aliases),
                            "user_input": sufix,
                        }

                        append_notice(data_append)

                else:

                    data_append = {
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append)

            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_balance["mod_balance_give"]["command"]):

            command_info = command_data_balance["mod_balance_give"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                command, username, value = re.split(r'\s+', message_text, maxsplit=2)

                print(command , username, value)

                if value.isdigit():
                    
                    user_found = next((user for user, data in user_data_load.items() if data["display_name"] == username), None)
                    
                    print(user_found)

                    if user_found:

                        usercheck_username = user_data_load[user_found]["display_name"]
                        likes = user_data_load[user_found]["likes"]
                        gifts = user_data_load[user_found]["gifts"]
                        shares = user_data_load[user_found]["shares"]
                        points = user_data_load[user_found]["points"]

                        give_balance(user_found, value)

                        aliases_balance = {
                            "{usercheck}" : usercheck_username,
                            "{likes}" : likes,
                            "{gifts}" : gifts,
                            "{shares}" : shares,
                            "{points}" : points
                        }

                        response = utils.replace_all(utils.messages_file_load("balance_user_gived"), aliases)
                        response = utils.replace_all(response, aliases_balance)

                        data_append = {
                            "type": "command",
                            "message": response,
                            "user_input": "",
                        }

                        append_notice(data_append)

                        command_data_tts["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/balance.json", command_data_balance, "save")

                    else:

                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(utils.messages_file_load("balance_user_not_found"), aliases),
                            "user_input": sufix,
                        }

                        append_notice(data_append)

                else:

                    data_append = {
                        
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_root_sufix_number"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append) 
            
                        
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

        elif compare_strings(command, command_data_balance["mod_balance_take"]["command"]):

            command_info = command_data_balance["mod_balance_take"]

            current, message_error, status, type_error = check_status(command_info, aliases)

            if status:

                command, username, value = re.split(r'\s+', message_text, maxsplit=2)

                if value.isdigit():
                    
                    user_found = next((user for user, data in user_data_load.items() if data["display_name"] == username), None)

                    if user_found:

                        usercheck_username = user_data_load[user_found]["display_name"]
                        likes = user_data_load[user_found]["likes"]
                        gifts = user_data_load[user_found]["gifts"]
                        shares = user_data_load[user_found]["shares"]
                        points = user_data_load[user_found]["points"]

                        check = check_cost(username, value, 1)

                        if check:

                            aliases_balance = {
                                "{usercheck}" : usercheck_username,
                                "{likes}" : likes,
                                "{gifts}" : gifts,
                                "{shares}" : shares,
                                "{points}" : points
                            }

                            response = utils.replace_all(utils.messages_file_load("balance_user_spended"), aliases)
                            response = utils.replace_all(response, aliases_balance)

                            data_append = {
                                "type": "command",
                                "message": response,
                                "user_input": "",
                            }

                            append_notice(data_append)

                            command_data_tts["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/balance.json", command_data_balance, "save")

                        else:

                            data_append = {
                    
                                "type": "command",
                                "message": utils.replace_all(utils.messages_file_load("balance_user_insuficient"), aliases),
                                "user_input": "",
                            }

                            append_notice(data_append)
                
                    else:

                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(utils.messages_file_load("balance_user_not_found"), aliases),
                            "user_input": sufix,
                        }

                        append_notice(data_append)

                else:

                    data_append = {
                        
                        "type": "command",
                        "message": utils.replace_all(utils.messages_file_load("command_root_sufix_number"), aliases),
                        "user_input": "",
                    }

                    append_notice(data_append) 
  
            else:

                if type_error == "level":

                    send_error_level(command_info)

                else:

                    data_append = {
                        "type": "command",
                        "message": message_error,
                        "user_input": sufix,
                    }

                    append_notice(data_append)

    else:

        data_append = {
            "type": "command",
            "message": utils.replace_all(utils.messages_file_load("commands_disabled"), aliases),
            "user_input": sufix,
        }

        append_notice(data_append)


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

    return json.dumps(data, ensure_ascii=False)


def looprank():

    rank_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "load")

    status_rank = rank_config['status']

    while status_rank == 1:

        rank_config = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/rank.json", "load")

        status_rank = rank_config['status']

        userdata = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json", "load")

        rank_likes = sorted(userdata.items(), key=lambda x:  int(x[1]["likes"]), reverse=True)[:10]

        data = {
            "type_id" : "likes",
            "info" : rank_likes,
        }

        data_goal = {
            "type": "rank_likes",
            "html": utils.update_ranks(data),
        }

        server.broadcast_message(json.dumps(data_goal))
        

        rank_shares = sorted(userdata.items(), key=lambda x: int(x[1]["shares"]), reverse=True)[:10]

        data = {
            "type_id" : "shares",
            "info" : rank_shares,
        }

        data_goal = {
            "type": "rank_shares",
            "html": utils.update_ranks(data),
        }

        server.broadcast_message(json.dumps(data_goal))

        rank_gifts = sorted(userdata.items(), key=lambda x: int(x[1]["gifts"]), reverse=True)[:10]

        data = {
            "type_id" : "gifts",
            "info" : rank_gifts,
        }

        data_goal = {
            "type": "rank_gifts",
            "html": utils.update_ranks(data),
        }

        server.broadcast_message(json.dumps(data_goal))

        rank_points = sorted(userdata.items(), key=lambda x: int(x[1]["points"]), reverse=True)[:10]

        data = {
            "type_id" : "points",
            "info" : rank_points,
        }

        data_goal = {
            "type": "rank_points",
            "html": utils.update_ranks(data),
        }

        server.broadcast_message(json.dumps(data_goal))

        interval = int(rank_config['interval'])

        if interval < 10:
            
            interval = 10

        time.sleep(interval)


def update_goal(goal_type, ammount):
    
    try:

        goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

        if goal_type == "total_follow" or goal_type == "total_share" or goal_type == "total_likes" or goal_type == "total_gifts" or goal_type == "total_diamonds":

            if goal_type == "total_follow":

                follows = int(goal_data["follow"]["total_follow"])
                total_follow = int(ammount) + follows
                goal_data["follow"]["total_follow"] = int(ammount) + total_follow

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_follow

            elif goal_type == "total_likes":

                goal_data["likes"]["total_likes"] = int(ammount)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return True

            elif goal_type == "total_share":

                total_shares = int(goal_data["share"]["total_share"]) + int(ammount)
                goal_data["share"]["total_share"] = total_shares

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_shares
            
            elif goal_type == "total_diamonds":  

                total_diamonds = int(goal_data["diamonds"]["total_diamonds"]) + int(ammount)
                goal_data["diamonds"]["total_diamonds"] = int(total_diamonds)

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_diamonds

            elif goal_type == "total_gifts":           

                total_gifts = int(goal_data["gift"]["total_gifts"]) + int(ammount)
                goal_data["gift"]["total_gifts"] = total_gifts

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json", "save", goal_data)

                return total_shares

        elif goal_data[goal_type]["status"] == 1:

            if int(ammount) >= int(goal_data[goal_type]["goal"]):
                
                if goal_data[goal_type]["event"] == "double":
                    
                    goal = int(goal_data[goal_type]["goal"]) * 2
                    goal_data[goal_type]["goal"] = goal

                elif goal_data[goal_type]["event"] == "add":
                    
                    goal = int(goal_data[goal_type]["goal"]) + int(goal_data[goal_type]["goal_after"])
                    goal_data[goal_type]["goal"] = goal

                elif goal_data[goal_type]["event"] == "multiply": 

                    goal = int(goal_data[goal_type]["goal"]) * int(goal_data[goal_type]["goal_after"])
                    goal_data[goal_type]["goal"] = goal

                else:
                    
                    if int(ammount) >= int(goal_data[goal_type]["goal"]):
                        goal = int(goal_data[goal_type]["goal_after"])


                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","save",goal_data)

                if goal_data[goal_type]["sound_status"] == 1 and goal_data[goal_type]["sound_file"] != "":
                    
                    play_sound(goal_data[goal_type]["sound_file"],goal_data[goal_type]["sound_volume"])
                    
                data_goal = {
                    "type": "update_goal",
                    "type_goal": goal_type,
                    "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
                    "current": int(ammount),
                    "goal": goal,
                }
                                
                send_discord_webhook({'type_id' : 'goal_end', 'target':f'{goal}' ,'current' : f'{ammount}', 'goal_type' : {goal_type}})

            else:

                goal = int(goal_data[goal_type]["goal"])

                data_goal = {
                    "type": "update_goal",
                    "type_goal": goal_type,
                    "html": utils.update_goal({"type_id": "update_goal", "type_goal": goal_type}),
                    "current": int(ammount),
                    "goal": goal, 
                }

            server.broadcast_message(json.dumps(data_goal))
        
    except Exception as e:

        utils.error_log(e)


def update_roles(data):
       
    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")
    chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json","load")

    type_id = data["type_id"]
    user = data["user_id"]

    if user in user_data_load:
        
        roles = user_data_load[user]["roles"]

        if type_id == "likes":

            likes = int(data["likes"])

            if user in user_data_load:
                
                if user_data_load[user]["likes"] != "":
                    user_likes = int(user_data_load[user]["likes"])
                    user_data_load[user]["likes"] = user_likes + likes
                else:
                    user_data_load[user]["likes"] = likes

                if not "likes" in roles and int(user_data_load[user]["likes"]) > int(chat_data["like-role"]):
                    roles.append("likes")

        elif type_id == "shares":
            
            user = data["user_id"]

            if user in user_data_load:
                if user_data_load[user]["shares"] != "":
                    if user_data_load[user]["shares"] == 0:

                        user_data_load[user]["shares"] = 1

                    else:

                        user_shares = int(user_data_load[user]["shares"])
                        user_data_load[user]["shares"] = user_shares + 1
                else:

                    user_data_load[user]["shares"] = 1

                if not "shares" in roles and int(user_data_load[user]["shares"]) > int(chat_data["share-role"]):
                    roles.append("shares")

        elif type_id == "follow":

            user = data["user_id"]

            if user in user_data_load and not "follow" in roles:
                roles.append("follow")

        elif type_id == "gifts":
            
            user = data["user_id"]
            gifts = data["gifts"]

            if user in user_data_load:
                if user_data_load[user]["gifts"] != "":
                    user_gifts = int(user_data_load[user]["gifts"])
                    user_data_load[user]["gifts"] = user_gifts + int(gifts)
                else:
                    user_data_load[user]["gifts"] = gifts

                if not "gifts" in roles and int(user_data_load[user]["gifts"]) > int( chat_data["gift-role"]):
                    roles.append("gifts")

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","save",user_data_load)
        

def update_points(data):

    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")
    points_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/points.json","load")
    ttk_data_gifts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json", "load")

    type_id = data["type_id"]
    user = data["user_id"]

    if user in user_data_load:

        if type_id == "likes":
            
            likes = int(data["likes"])

            config_points = float(points_data_load["likes"])
            user_points = float(user_data_load[user]["points"])

            received_points = config_points * likes

            user_data_load[user]["points"] = received_points + user_points

        elif type_id == "shares":
            
            config_points = float(points_data_load["shares"])
            user_points = float(user_data_load[user]["points"])

            user_data_load[user]["points"] = config_points + user_points

        elif type_id == "follow":

            user = data["user"]

            config_points = float(points_data_load["follow"])
            user_points = float(user_data_load[user]["points"]) + config_points
            user_data_load[user]["points"] = float(user_points)

        elif type_id == "gifts":
            
            user = data["user"]
            gifts = data["gifts"]
            gift_id = data["gift_id"]

            gits_data = ttk_data_gifts['gifts']

            gift_global_status = gits_data[gift_id]['points-global']

            if int(gift_global_status) == 1:

                config_points = float(points_data_load["gifts"])
                user_points = float(user_data_load[user]["points"])
                
            else:

                config_points = float(gits_data[gift_id]['points'])
                user_points = float(user_data_load[user]["points"])

            received_points = config_points * gifts

            user_data_load[user]["points"] = float(received_points + user_points)

    utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","save", user_data_load)


def show_alert(data):

    config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log_config.json","load")

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


def add_user_database(data):
    
    try:
        role_mapping = {
            "follow": "follow",
            "moderator": "moderator",
            "subscriber": "subscriber",
        }


        if utils.check_file(f"{utils.local_work('appdata_path')}/user_info/users_database.json"):
            
            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","load")

            if data["user_id"] not in user_data_load:
                
                roles = ["spec"]

                for role_key, role_var in role_mapping.items():
                    
                    if data[role_key] == True:
                        roles.append(role_var)

                    user_data_load[data["user_id"]] = {
                        "display_name": data["display_name"],
                        "roles": roles,
                        "likes": 0,
                        "shares": 0,
                        "gifts": 0,
                        "points" : 0,
                        "profile_pic" : data["profile_pic"]
                    }
            else:
                
                roles = user_data_load[data["user_id"]]["roles"]

                for role_key, role_var in role_mapping.items():

                    if role_var not in roles and data[role_key] == True:
                        roles.append(role_var)
                        
                    elif role_var in roles and data[role_key] == False:
                        roles.remove(role_var)

                user_data_load[data["user_id"]] = {
                    "display_name": data["display_name"],
                    "roles": roles,
                    "likes": user_data_load[data["user_id"]]["likes"],
                    "shares": user_data_load[data["user_id"]]["shares"],
                    "gifts": user_data_load[data["user_id"]]["gifts"],
                    "points" : user_data_load[data["user_id"]]["points"],
                    "profile_pic" : user_data_load[data["user_id"]]["profile_pic"]
                }
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/user_info/users_database.json","save",user_data_load)

            userdata_py('backup',"null")

        else:
            userdata_py('restore_backup',"null") 

    except Exception as e:
        utils.error_log(e)


def on_connect(event):

    event = utils.DictDot(event)

    new_room = event.room_id
    total_follows = event.followers
    new_gift_info = event.giftdata

    gift_data = json.loads(new_gift_info)

    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")
    room_id_store = goal_data['room']

    try:
        if room_id_store != new_room:

            utils.update_dict_gifts(gift_data)

            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            goal_data["follow"]["total_follow"] = int(total_follows)

            goal_data['room'] = new_room

            goal_data["diamonds"]["total_diamonds"] = 0
            goal_data["gift"]["total_gifts"] = 0
            goal_data["share"]["total_share"] = 0
            goal_data["max_viewer"]["total_viewer"] = 0
            goal_data["likes"]["total_likes"] = 0

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","save",goal_data)

            like_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","load")
            
            like_list = {
                "likes" : {
                    
                }
            }
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_list)

            share_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","load")
            
            share_list = {
                "shares" : {
                    
                }
            }
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","save",share_list)
            
            join_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","load")
            
            join_list = [] 
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save",join_list)

            data_append = {
                "type": "event",
                "message": utils.messages_file_load(f"event_ttk_connect"),
                "user_input": "",
            }
            
            append_notice(data_append)
            
            send_discord_webhook({"type_id": "live_start"})

        else:
            
            data_append = {
                "type": "event",
                "message": utils.messages_file_load(f"event_ttk_connect"),
                "user_input": "",
            }
            
            append_notice(data_append)

    except Exception as e:
        utils.error_log(e)


def on_disconnect(event):

    event = utils.DictDot(event)

    message_event = utils.messages_file_load("event_ttk_disconected")

    data_append = {
        "type": "live_end",
        "message": message_event,
        "user_input": "",
    }

    append_notice(data_append)

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

    username = event.nickname
    userid = event.unique_id
    comment = event.comment
    follower = event.is_following
    moderator = event.is_moderator
    subscriber = event.is_subscriber     
    badges_list = event.badges_list
    top_gifter = event.is_top_gifter
    profilepic = event.profilePictureUrl

    try:

        if comment != None and username != None and userid != None:
            
            chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/chat_config.json","load")
            
            now = datetime.datetime.now()
            
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
                "type": "PRIVMSG",
                "display_name": username,
                "user_id": userid,
                "user_name": username,
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
                "wrapp_message": chat_data["wrapp-message"],
                "data_show": chat_data["data-show"],
                "chat_time": chat_time,
                "type_data": chat_data["type-data"],
            }

            add_user_database(data_res)

            if main_window_open:

                main_window.evaluate_js(f"append_message({json.dumps(data_res, ensure_ascii=False)})")

            if window_chat_open:
                
                window_chat.evaluate_js(f"append_message_out({json.dumps(data_res, ensure_ascii=False)})")

            commands_module(data_res)

    except Exception as e:
        
        utils.error_log(e)


def on_like(event):
    
    event = utils.DictDot(event)

    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")
    like_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","load")

    try:

        username = event.nickname
        userid = event.uniqueId
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
                "{username}": username,
                "{user}" : userid,
                "{likes}" : likes_send,
                "{total_likes}" :total_likes
            }
            
            data_append = {
                "type": "like",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_like"), aliases),
                "user_input": "",
                "profile_pic": profilePictureUrl
            }

            show_alert(data_append)
            append_notice(data_append)

            send_discord_webhook({"type_id": "like", "username" : username, "likes_send" : likes_send, "total_likes" : total_likes})

            if event_config_data["ttk_like"]["sound"] == 1:
                
                audio_path = event_config_data["ttk_like"]["sound_loc"]
                audio_volume = event_config_data["ttk_like"]["sound_volume"]

                threading.Thread(target=play_sound,args=(audio_path,audio_volume),daemon=True).start()
            
        else:
            
            delay = event_config_data["ttk_like"]["delay"]

            last_like = like_list[userid]

            message_delay, check_time, current = utils.check_delay(delay, last_like)

            if check_time:
                
                like_list[userid] = current
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)

                aliases = {
                    "{username}": username,
                    "{amount}" : likes_send
                }
                
                data_append = {
                    "type": "like",
                    "message": utils.replace_all(utils.messages_file_load("event_ttk_like"),aliases),
                    "user_input": "",
                    "profile_pic": profilePictureUrl
                }

                append_notice(data_append)
                show_alert(data_append)
                send_discord_webhook({"type_id": "like", "username" : username, "likes_send" : likes_send, "total_likes" : total_likes})

        data_user = {
            "type_id": "likes",
            "display_name": username,
            "user_id": userid,
            "user_name": username,
            "follow": follower,
            "moderator": moderator,
            "subscriber": subscriber,
            "profile_pic": profilePictureUrl,
            "likes": likes_send
        }

        add_user_database(data_user)
        update_roles(data_user)
        update_points(data_user)

        return_likes = update_goal("total_likes", total_likes)

        if return_likes:

            update_goal("likes", total_likes)

    except Exception as e:
        utils.error_log(e)


def on_join(event):
    
    event = utils.DictDot(event)

    username = event.nickname
    user_id = event.uniqueId
    profilePictureUrl = event.profilePictureUrl

    join_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","load")

    if user_id != None:

        if user_id not in join_list:
            
            join_list.append(user_id)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save",join_list)
            
            aliases = {"{username}": username}

            data_append = {
                "type": "join",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_join"), aliases),
                "user_input": "",
                "img" : profilePictureUrl
            }
            
            show_alert(data_append)
            append_notice(data_append)


def on_gift(event):

    event = utils.DictDot(event)

    ttk_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/gifts.json","load")
    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

    gifts_data = ttk_data["gifts"]
    
    giftname_br = event.gift_name
    gift_id = str(event.giftId)
    gift_diamonds = event.gift_diamonds
    userid = event.unique_id
    username = event.nickname
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
    

    try:

        if streakable and not streaking:

            if gift_id in gifts_data:

                if gifts_data[gift_id]["name_br"] != "":
                    giftname_br = gifts_data[gift_id]["name_br"]

                aliases = {
                    "{username}": username,
                    "{amount}": giftcount,
                    "{giftname}": giftname_br,
                    "{diamonds}": gift_diamonds,
                    "{id}": gift_id,
                }
                
                data_discord = {
                    "type_id": "gift", 
                    "username" : username, 
                    "gifts_send" : giftcount, 
                    "gift_name" : giftname_br,
                    "diamonds": gift_diamonds
                }
                

                data_append = {
                    "type": "gift",
                    "message": utils.replace_all(utils.messages_file_load("event_ttk_gift"), aliases),
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
                    "display_name": username,
                    "user_id": userid,
                    "user_name": username,
                    "follow": follower,
                    "moderator": moderator,
                    "subscriber": subscriber,
                    "profile_pic": profilePictureUrl,
                    "gifts": giftcount,
                    "gift_id" : gift_id,
                }

                add_user_database(data_user)

                update_roles(data_user)
                update_points(data_user)

                send_discord_webhook(data_discord)
                append_notice(data_append)
                show_alert(data_append)

                audio = gifts_data[gift_id]["audio"]
                volume = gifts_data[gift_id]["volume"]
                status = gifts_data[gift_id]["status"]
                
                if status == 1 and audio != "":
                    threading.Thread(target=play_sound,args=(audio,volume,),daemon=True,).start()

                elif global_status == 1 and global_audio != "":
                    threading.Thread(target=play_sound,args=(global_audio,global_volume,),daemon=True,).start()
            else:

                if global_status == 1 and global_audio != "":
                    threading.Thread(target=play_sound,args=(global_audio,global_volume,),daemon=True,).start()

        elif not streakable:

            if gift_id in gifts_data:

                if gifts_data[gift_id]["name_br"] != "":
                    giftname_br = gifts_data[gift_id]["name_br"]

                aliases = {
                    "{username}": username,
                    "{amount}": giftcount,
                    "{giftname}": giftname_br,
                    "{diamonds}": gift_diamonds,
                    "{id}": gift_id,
                }
                
                discord_data = {
                    "type_id": "gift", 
                    "username" : username, 
                    "gifts_send" : giftcount, 
                    "gift_name" : giftname_br,
                    "diamonds": gift_diamonds
                }
                
                data_append = {
                    "type": "gift",
                    "message": utils.replace_all(utils.messages_file_load("event_ttk_gift"), aliases),
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }
                
                data_user = {
                    "type_id": "gifts",
                    "display_name": username,
                    "user_id": userid,
                    "user_name": username,
                    "follow": follower,
                    "moderator": moderator,
                    "subscriber": subscriber,
                    "profile_pic": profilePictureUrl,
                    "gifts": giftcount,
                    "gift_id" : gift_id,
                }

                add_user_database(data_user)

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
                append_notice(data_append)
                show_alert(data_append)

                audio = gifts_data[gift_id]["audio"]
                volume = gifts_data[gift_id]["volume"]
                status = gifts_data[gift_id]["status"]
                
                if status == 1 and audio != "":
                    threading.Thread(target=play_sound,args=(audio,volume,),daemon=True,).start()

                elif global_status == 1 and global_audio != "":
                    threading.Thread(target=play_sound,args=(global_audio,global_volume,),daemon=True,).start()
            else:

                if global_status == 1 and global_audio != "":
                    threading.Thread(target=play_sound,args=(global_audio,global_volume,),daemon=True,).start()

    except Exception as e:
        
        utils.error_log(e)


def on_follow(event):

    event = utils.DictDot(event)

    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")
    ttk_follows = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/follow.json","load")

    username = event.nickname
    userid = event.uniqueId
    follower = event.is_following
    moderator = event.is_moderator
    subscriber = event.is_subscriber  
    profilePictureUrl = event.profilePictureUrl

    try:
        
        if userid not in ttk_follows:

            data_user = {
                "type_id": "follow",
                "display_name": username,
                "user_id": userid,
                "user_name": username,
                "follow": follower,
                "moderator": moderator,
                "subscriber": subscriber,
                "profile_pic": profilePictureUrl
            }

            add_user_database(data_user)

            ttk_follows.append(userid)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/follow.json","save",ttk_follows)

            aliases = {
                "{username}": username
            }

            data_append = {
                "type": "follow",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_follow"), aliases),
                "user_input": "",
                "profile_pic" : profilePictureUrl
            }

            update_roles(data_user)

            return_follow = update_goal("total_follow", int(1))
            if return_follow:
                update_goal("follow", int(return_follow))

            append_notice(data_append)
            show_alert(data_append)

            send_discord_webhook({"type_id": "follow", "username" : username})

            if event_config_data["ttk_follow"]["sound"] == 1:

                audio_path = event_config_data["ttk_follow"]["sound_loc"]
                audio_volume = event_config_data["ttk_follow"]["sound_volume"]

                threading.Thread(target=play_sound,args=(audio_path,audio_volume,),daemon=True).start()

    except Exception as e:
        utils.error_log(e)


def on_share(event):
    
    event = utils.DictDot(event)

    try:
        
        userid = event.uniqueId
        username = event.nickname
        follower = event.is_following
        moderator = event.is_moderator
        subscriber = event.is_subscriber  
        profilePictureUrl = event.profilePictureUrl


        event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_not.json", "load")

        shares_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","load")
        shares_list = shares_data["shares"]

        aliases = {
            "{username}": username,
            "{user}" : userid
        }

        data_user = {
            "type_id": "shares",
            "display_name": username,
            "user_id": userid,
            "user_name": username,
            "follow": follower,
            "moderator": moderator,
            "subscriber": subscriber,
            "profile_pic": profilePictureUrl,
        }

        add_user_database(data_user)

        def update_user_share(userid):

            data_roles = {
                "type_id": "shares",
                "username" : username, 
                "user_id": userid,
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

            data_append = {
                "type": "share",
                "message":  utils.replace_all(utils.messages_file_load("event_ttk_share"), aliases),
                "user_input": "",
                "profile_pic" : profilePictureUrl
            }
            
            append_notice(data_append)
            show_alert(data_append)
            
            send_discord_webhook({"type_id": "share", "username" : username})

        
            if event_config_data["ttk_share"]["sound"] == 1:
                
                audio_path = event_config_data["ttk_share"]["sound_loc"]
                audio_volume = event_config_data["ttk_share"]["sound_volume"]

                threading.Thread(target=play_sound,args=(audio_path,audio_volume),daemon=True).start()
        
        else:

            message_delay, check_time, current = utils.check_delay(event_config_data["ttk_share"]["delay"], shares_list[userid])

            if check_time:
                
                shares_list[userid] = current
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/shares.json","save", shares_data)

                data_append = {
                    "type": "share",
                    "message":  utils.replace_all(utils.messages_file_load("event_ttk_share"), aliases),
                    "user_input": "",
                    "profile_pic" : profilePictureUrl
                }

                append_notice(data_append)
                show_alert(data_append)

                send_discord_webhook({"type_id": "share", "username" : username})

        update_user_share(userid)
                
    except Exception as e:
        utils.error_log(e)


def on_viewer_update(event):

    event = utils.DictDot(event)
    
    viewer_count = event.viewer_count
    user_info = event.top_viewer

    user_info = utils.DictDot(user_info)
    
    try:
        if viewer_count != None and int(viewer_count) > int(1):
                
            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","load")

            max_specs = int(goal_data["max_viewer"]["total_viewer"])

            if int(viewer_count) > max_specs:

                goal_data["max_viewer"]["total_viewer"] = int(viewer_count)

                update_goal("max_viewer", int(viewer_count))

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/goal.json","save",goal_data)

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
    
    event = utils.DictDot(event)

    userId = event.userId
    secUid = event.secUid
    uniqueId = event.uniqueId
    username = event.nickname
    profilePictureUrl = event.profilePictureUrl
    followRole = event.followRole
    userBadges = event.userBadges
    userDetails = event.userDetails
    isModerator = event.isModerator
    isNewGifter = event.isNewGifter
    isSubscriber = event.isSubscriber
    topGifterRank = event.topGifterRank
    coinCount = event.coinCount

    aliases = {
        "{username}": username,
        "{coins}" : coinCount
    }

    data_append = {
        "type": "chest",
        "message": utils.replace_all(utils.messages_file_load("event_ttk_envelope"), aliases),
        "user_input": "",
    }

    append_notice(data_append)
    
    send_discord_webhook({"type_id": "envelope", "username" : username})


def on_error(event):

    event = utils.DictDot(event)

    data_append = {
        "type": "event",
        "message": f"Erro : {event.message}",
        "user_input": "",
    }

    append_notice(data_append)


def webview_start_app(app_mode):
    
    global main_window, main_window_open, window_chat, window_events, window_chat_open

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

    debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/debug.json","load")

    debug_status = debug_data["debug"]

    if debug_status == 0:
        debug_status = False
        
    elif debug_status == 1:
        debug_status = True

    if app_mode == "normal":
        
        main_window = webview.create_window("VibesBot",f"{utils.local_work('datadir')}/web/index.html",width=1200,height=680,min_size=(1200, 680))
    
        main_window.events.loaded += set_main_window_open
        main_window.events.closed += close
        main_window.events.resized += on_resize

        main_window.expose(
            loaded,
            chat_config,
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
            webview_start_app,
            tiktok_gift,
            tiktok_goal,
            tiktok_alerts,
            tiktok_logs,
            tiktok_auth,
            tts_command,
            userdata_py,
            balance_command,
            ranks_config
        )

        webview.start(storage_path=utils.local_work("datadir"),private_mode=True,debug=debug_status,http_server=True,http_port=7000)

    elif app_mode == "chat":
        
        window_chat = webview.create_window("VibesBot Chat", "")
        window_chat.load_url("http://localhost:7000/chat.html")
        window_chat.events.loaded += set_window_chat_open
        window_chat.events.closed += set_window_chat_close

        window_chat.expose(open_py)

    elif app_mode == "events":
        
        window_events = webview.create_window("VibesBot Eventos", "")
        window_events.load_url("http://localhost:7000/events.html")

        window_events.events.loaded += set_window_events_open
        window_events.events.closed += set_window_events_close

        window_events.expose(event_log)


def close():

    global loaded_status
    
    loaded_status = False
    
    if utils.check_file(f"{utils.local_work('appdata_path')}/user_info/users_database.json"):
        userdata_py('backup',"null")
    
    if window_chat_open:
        window_chat.destroy()

    if window_events_open:
        window_events.destroy()

    wsclient.send(json.dumps({'type': 'Close','message' : 'Close'}, ensure_ascii=False))

    wsclient.close()

    server.close_servers()

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

    wsclient.send("close")
    
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

        subprocess.Popen('run.bat', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    except Exception as e:
        utils.error_log(e)


def start_app():

    def start_log_files():

        MAX_LOG_SIZE = 1024 * 1024 * 10  

        log_file_path = f"{utils.local_work('appdata_path')}/error_log.txt"

        logging.basicConfig(
            filename=log_file_path,
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(name)s  - %(message)s",
            encoding="utf-8",
        )

        if os.path.exists(log_file_path):

            log_file_size = os.path.getsize(log_file_path)

            if log_file_size > MAX_LOG_SIZE:

                with open(log_file_path, "r", encoding="UTF-8") as f:
                    lines = f.readlines()

                with open(log_file_path, "w", encoding="UTF-8") as f:
                    f.writelines(lines[-1000:])

        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json","load")

        if len(event_log_data["event-list"]) > 100:
            event_log_data["event-list"] = event_log_data["event-list"][-100:]

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/event_log.json","save",event_log_data)

        join_list = []

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/joins.json","save",join_list)

        like_data = {"likes": {}}

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/config/likes.json","save",like_data)
        
        if utils.check_file(f"{utils.local_work('appdata_path')}/user_info/users_database.json"):
            userdata_py('backup',"null")
        else:
            userdata_py('restore_backup',"null") 

    if utils.compare_and_insert_keys():

        start_log_files()
        
        pygame.init()
        pygame.mixer.init()

        loop = threading.Thread(target=loopcheck, args=(), daemon=True)
        loop.start()

        loop_r = threading.Thread(target=looprank, args=(), daemon=True)
        loop_r.start()

        runode= threading.Thread(target=start_node, args=(), daemon=True)
        runode.start()

        authdata = auth_data(f"{utils.local_work('appdata_path')}/auth/auth.json")
        username = authdata.USERNAME()

        if username != "":
            start_websocket_CS()

        if getattr(sys, "frozen", False):
            utils.splash_close()

        webview_start_app("normal")


if lock_manager.already_running:

    error_message = "O programa já está em execução, aguarde."
    messagebox.showerror("Erro", error_message)

else:
    start_app()