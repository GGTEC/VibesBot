import sys
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import logging
import win32file
import subprocess
import utils
import webview
import threading
import validators
import webbrowser
import time
import json
import pygame
import requests as req
import tkinter
import textwrap
import keyboard
import random
import yt_dlp
import datetime
import re
import tkinter.messagebox as messagebox
import sk
from io import BytesIO

from collections import namedtuple
from auth import auth_data
from io import BytesIO
from gtts import gTTS
from tkinter import messagebox
from tkinter import filedialog as fd
from random import randint
from discord_webhook import DiscordWebhook, DiscordEmbed

from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import *


global caching, loaded_status, window, window_chat_open, window_chat, window_events, window_events_open

caching = 0
loaded_status = 0
window_chat_open = 0
tiktok_conn = 0
window_events_open = 0

def play_sound(audio, volume):

    convert_vol = int(volume) / 100
    playing = pygame.mixer.music.get_busy()
    pygame.mixer.music.load(audio)
    pygame.mixer.music.set_volume(convert_vol)
    pygame.mixer.music.play()


def send(message):
    window.evaluate_js(f"toast_notifc('{message}')")


def toast(message):
    window.evaluate_js(f"toast_notifc('{message}')")


def append_notice(data_receive):

    try:
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","load")
        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/chat_config.json","load")

        now = datetime.datetime.now()

        data = {
            "message": data_receive["message"],
            "user_input": data_receive["user_input"],
            "font_size": event_log_data["slider-font-events"],
            "font_size_chat": chat_data["font-size"],
            "color_events": event_log_data["color-events"],
            "data_time": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "data_show": event_log_data["data-show-events"],
            "type_event": data_receive["type"],
            "show_commands" : event_log_data["show-commands"],
            "show_commands_chat" : event_log_data["show-commands-chat"],
            "show_follow" : event_log_data["show-follow"],
            "show_follow_chat" : event_log_data["show-follow-chat"],
            "show_likes" : event_log_data["show-likes"],
            "show_likes_chat" : event_log_data["show-likes-chat"],
            "show_gifts" : event_log_data["show-gifts"],
            "show_gifts_chat" : event_log_data["show-gifts-chat"],
            "show_chest" : event_log_data["show-chest"],
            "show_chest_chat" : event_log_data["show-chest-chat"],
            "show_share" : event_log_data["show-share"],
            "show_share_chat" : event_log_data["show-share-chat"],
            "show_join" : event_log_data["show-join"],
            "show_join_chat" : event_log_data["show-join-chat"],
            "show_events" : event_log_data["show-events"],
            "show_events_chat" : event_log_data["show-events-chat"],
            "show_goal_start" : event_log_data["show-goal-start"],
            "show_goal_start_chat" : event_log_data["show-goal-start-chat"],
            "show_goal_end" : event_log_data["show-goal-end"],
            "show_goal_end_chat" : event_log_data["show-goal-end-chat"],
            "event_list" : event_log_data["event-list"],
        }

        event_log_data["event-list"].append(
            f"{now} | {data_receive['type']} | {data_receive['message']} | {data_receive['user_input']}"
        )
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","save",event_log_data)

        window.evaluate_js(f"append_notice({json.dumps(data, ensure_ascii=False)})")
        
        if window_events_open == 1:
            window_events.evaluate_js(f"append_notice_out({json.dumps(data, ensure_ascii=False)})")

        if window_chat_open == 1:
            window_chat.evaluate_js(f"append_notice_chat({json.dumps(data, ensure_ascii=False)})")


    except Exception as e:
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
        authdata = auth_data(f"{utils.local_work('appdata_path')}/VibesBot/web/src/auth/auth.json")
                
        type_id = data["type_id"]

        discord_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/discord.json","load")

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


def logout_auth():
    data = {"USERNAME": "", "SESSIONID": "", "SIDGUARD": ""}

    utils.manipulate_json(
        f"{utils.local_work('appdata_path')}/VibesBot/web/src/auth/auth.json",
        "save",
        data,
    )

    close()


def event_log(data_save):
    
    data_save = json.loads(data_save)
    type_id = data_save['type_id']
    
    if type_id == "get":
        
        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","load")

        if event_log_data is not None:
            
            data = {
                "slider-font-events" : event_log_data["slider-font-events"],
                "color-events" : event_log_data["color-events"],
                "data-show-events" : event_log_data["data-show-events"], 
                "show-commands" : event_log_data["show-commands"],
                "show-commands-chat" : event_log_data["show-commands-chat"],
                "show-events" : event_log_data["show-events"],
                "show-events-chat" : event_log_data["show-events-chat"],
                "show-follow" : event_log_data["show-follow"],
                "show-follow-chat" : event_log_data["show-follow-chat"],
                "show-likes" : event_log_data["show-likes"],
                "show-likes-chat" : event_log_data["show-likes-chat"],
                "show-gifts" : event_log_data["show-gifts"],
                "show-gifts-chat" : event_log_data["show-gifts-chat"],
                "show-chest" : event_log_data["show-chest"],
                "show-chest-chat" : event_log_data["show-chest-chat"],
                "show-goal-start" : event_log_data["show-goal-start"],
                "show-goal-start-chat" : event_log_data["show-goal-start-chat"],
                "show-goal-end" : event_log_data["show-goal-end"],
                "show-goal-end-chat" : event_log_data["show-goal-end-chat"],
                "show-share" : event_log_data["show-share"],
                "show-share-chat" : event_log_data["show-share-chat"],
                "show-join" : event_log_data["show-join"],
                "show-join-chat" : event_log_data["show-join-chat"],
                "show-events" : event_log_data["show-events"],
                "show-events-chat" : event_log_data["show-events-chat"],
                "event-list" : event_log_data["event-list"],
            }
            
            return  json.dumps(data, ensure_ascii=False)

    elif type_id == "save":
        
        try:
            
            event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","load")

            if event_log_data is not None:
                
                event_log_data["slider-font-events"] = data_save["slider-font-events"]
                event_log_data["color-events"] = data_save["color-events"]
                event_log_data["data-show-events"] = data_save["data-show-events"] 
                event_log_data["show-events"] = data_save["show-events"]
                event_log_data["show-events-chat"] = data_save["show-events-chat"]
                event_log_data["show-commands"] = data_save["show-commands"]
                event_log_data["show-commands-chat"] = data_save["show-commands-chat"]
                event_log_data["show-follow"] = data_save["show-follow"]
                event_log_data["show-follow-chat"] = data_save["show-follow-chat"]
                event_log_data["show-likes"] = data_save["show-likes"]
                event_log_data["show-likes-chat"] =data_save["show-likes-chat"]
                event_log_data["show-gifts"] = data_save["show-gifts"]
                event_log_data["show-gifts-chat"] = data_save["show-gifts-chat"]
                event_log_data["show-chest"] = data_save["show-chest"]
                event_log_data["show-chest-chat"] = data_save["show-chest-chat"]
                event_log_data["show-share"] = data_save["show-share"]
                event_log_data["show-share-chat"] = data_save["show-share-chat"]
                event_log_data["show-join"] = data_save["show-join"]
                event_log_data["show-join-chat"] = data_save["show-join-chat"]
                event_log_data["show-goal-end"] = data_save["show-goal-end"]
                event_log_data["show-goal-end-chat"] = data_save["show-goal-end-chat"]
                event_log_data["show-goal-start"] = data_save["show-goal-start"]
                event_log_data["show-goal-start-chat"] = data_save["show-goal-start-chat"]

                utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","save",event_log_data)
                
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
        initialdir=f"{utils.local_work('appdata_path')}/VibesBot/web/src",
        filetypes=filetypes,
    )

    root.destroy()

    return folder


def get_command_list():
    command_simple_data = utils.manipulate_json(
        f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/simple_commands.json",
        "load",
        None,
    )
    command_counter_data = utils.manipulate_json(
        f"{utils.local_work('appdata_path')}/VibesBot/web/src/counter/commands.json",
        "load",
        None,
    )
    command_giveaway_data = utils.manipulate_json(
        f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/commands.json",
        "load",
        None,
    )
    command_player_data = utils.manipulate_json(
        f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json",
        "load",
        None,
    )

    data = {
        "commands_simple": [command_simple_data],
        "commands_counter": [command_counter_data],
        "commands_giveaway": [command_giveaway_data],
        "commands_player": [command_player_data],
    }

    command_list_dump = json.dumps(data, ensure_ascii=False)

    return command_list_dump


def commands_py(data_receive):
    
    data = json.loads(data_receive)
    type_rec = data["type_id"]

    command_json_path = (f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/commands.json")

    if type_rec == "create":
        
        try:
            command = data["command"]
            command_type = data["type"]
            delay = data["delay"]
            user_level = data["user_level"]
            sound = data["sound"]

            command_data = utils.manipulate_json(command_json_path, "load")

            if command_data is not None:
                
                command_data[command.lower().strip()] = {
                    "status": 1,
                    "type": command_type,
                    "user_level": user_level,
                    "delay": delay,
                    "sound": sound,
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
            new_delay = data["delay"]
            sound = data["sound"]
            user_level = data["user_level"]
            command_type = "sound"

            command_data = utils.manipulate_json(command_json_path, "load", None)

            if command_data is not None:
                del command_data[command]

                command_data[new_command] = {
                    "status": status,
                    "type": command_type,
                    "user_level": user_level,
                    "delay": new_delay,
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

                data = {
                    "status": status,
                    "type": type_cmd,
                    "edit_command": command,
                    "edit_level": user_level,
                    "edit_delay": delay,
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

            if commands is not None:
                command_data_queue = utils.manipulate_json(
                    f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/commands.json",
                    "load",
                    None,
                )
                command_data_giveaway = utils.manipulate_json(
                    f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/commands.json",
                    "load",
                    None,
                )
                command_data_player = utils.manipulate_json(
                    f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json",
                    "load",
                    None,
                )

                data = {
                    "commands": [commands],
                    "commands_queue": [command_data_queue],
                    "commands_giveaway": [command_data_giveaway],
                    "commands_player": [command_data_player],
                }
                return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            utils.error_log(e)


def tts_command(data_receive):
    
    data = json.loads(data_receive)
    type_id = data["type_id"]
    tts_json_path = (f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/tts.json")

    if type_id == "get":
        
        
        tts_command_data = utils.manipulate_json(tts_json_path, "load")
        
        if tts_command_data is not None:
            
            data = {
                "command": tts_command_data["command"],
                "status": tts_command_data["status"],
                "delay": tts_command_data["delay"],
            }

            data_dump = json.dumps(data, ensure_ascii=False)
            return data_dump

    elif type_id == "save":
        
        try:
            tts_command_data = utils.manipulate_json(tts_json_path, "load")

            if tts_command_data is not None:
                
                tts_command_data["command"] = data["command"]
                tts_command_data["status"] = data["status"]
                tts_command_data["delay"] = data["delay"]
                tts_command_data["user_level"] = data["user_level"]

                utils.manipulate_json(tts_json_path, "save", tts_command_data)

        except Exception as e:
            utils.error_log(e)


def giveaway_py(type_id, data_receive):

    giveaway_config_path = (f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/config.json")
    giveaway_names_path = (f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/names.json")
    giveaway_backup_path = (f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/backup.json")
    giveaway_result_path = ( f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/result.json")

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

        giveaway_commands_data = utils.manipulate_json(f"{giveaway_names_path}/{data_receive}.json", "load", None)

        if giveaway_commands_data is not None:

            data = {
                "command": giveaway_commands_data["command"],
                "status": giveaway_commands_data["status"],
                "delay": giveaway_commands_data["delay"],
                "last_use": giveaway_commands_data["last_use"],
                "user_level": giveaway_commands_data["user_level"],
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

            giveaway_commands_data = utils.manipulate_json(f"{giveaway_names_path}/{type_command}.json", "load", None)

            giveaway_commands_data["command"] = data["command"]
            giveaway_commands_data["status"] = data["status"]
            giveaway_commands_data["delay"] = data["delay"]
            giveaway_commands_data["user_level"] = data["user_level"]

            utils.manipulate_json(f"{giveaway_names_path}/{type_command}.json","save",giveaway_commands_data)

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

    json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/queue.json"

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
            json_commands_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/commands.json"
            command_queue_data = utils.manipulate_json(json_commands_path, "load")

            data = {
                "command": command_queue_data[data_receive]["command"],
                "status": command_queue_data[data_receive]["status"],
                "delay": command_queue_data[data_receive]["delay"],
                "last_use": command_queue_data[data_receive]["last_use"],
                "user_level": command_queue_data[data_receive]["user_level"],
            }

            return json.dumps(data, ensure_ascii=False)

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "save_commands":

        data_received = json.loads(data_receive)

        try:

            json_commands_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/commands.json"
            command_queue_data = utils.manipulate_json(json_commands_path, "load")

            type_command = data_received["type_command"]

            command_queue_data[type_command] = {
                "command": data_received["command"],
                "status": data_received["status"],
                "delay": data_received["delay"],
                "last_use": command_queue_data[type_command]["last_use"],
                "user_level": data_received["user_level"],
            }

            utils.manipulate_json(json_commands_path, "save", command_queue_data)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")


def not_config_py(data_receive, type_id, type_not):

    json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_not.json"
    event_config_data = utils.manipulate_json(json_path, "load")

    if type_id == "get":

        file_data = event_config_data[type_not]

        data = {"not": file_data["status"], "response_chat": file_data["response_chat"]}

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save":

        try:
            data = json.loads(data_receive)

            event_config_data[type_not]["status"] = data["not"]
            event_config_data[type_not]["response_chat"] = data["response_chat"]

            utils.manipulate_json(json_path, "save", event_config_data)

            toast("success")

        except Exception as e:

            utils.error_log(e)
            toast("error")


def messages_config(type_id, data_receive):

    json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/commands_config.json"
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

    json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/messages/messages_file.json"
    
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

    discord_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/discord.json"

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


def tiktok_auth(data_receive):

    data_receive = json.loads(data_receive)
    auth_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/auth/auth.json"

    data = utils.manipulate_json(auth_json_path, "load")

    data["USERNAME"] = data_receive["username"]
    data["SESSIONID"] = data_receive["sessionid"]
    data["SIDGUARD"] = data_receive["sidguard"]

    utils.manipulate_json(auth_json_path, "save", data)

    return True


def tiktok_alerts(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    event_config_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_not.json"

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

    gifts_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/gifts.json"

    ttk_data_gifts = utils.manipulate_json(gifts_json_path, "load")

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    if type_id == "get":

        data = {"gifts": ttk_data_gifts["gifts"]}

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "save_sound_gift":

        try:
            gift_id = data_receive["id"]

            ttk_data_gifts["gifts"][gift_id]["status"] = data_receive["status"]
            ttk_data_gifts["gifts"][gift_id]["audio"] = data_receive["sound_loc"]
            ttk_data_gifts["gifts"][gift_id]["volume"] = data_receive["sound_volume"]

            utils.manipulate_json(gifts_json_path, "save", ttk_data_gifts)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")

    elif type_id == "get_gift_info":

        gift_id = data_receive["id"]

        data = {
            "audio": ttk_data_gifts["gifts"][gift_id]["audio"],
            "status": ttk_data_gifts["gifts"][gift_id]["status"],
            "volume": ttk_data_gifts["gifts"][gift_id]["volume"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "diamond_gift_get":

        diamond_value = data_receive["diamond_value"]

        data = {
            "status": ttk_data_gifts["diamond_gifts"][diamond_value]["status"],
            "volume": ttk_data_gifts["diamond_gifts"][diamond_value]["volume"],
            "sound": ttk_data_gifts["diamond_gifts"][diamond_value]["sound"],
        }

        return json.dumps(data, ensure_ascii=False)

    elif type_id == "diamond_gift_save":

        try:
            diamond_value = data_receive["diamond_value"]
            ttk_data_gifts["diamond_gifts"][diamond_value]["status"] = data_receive["status"]
            ttk_data_gifts["diamond_gifts"][diamond_value]["sound"] = data_receive["sound"]
            ttk_data_gifts["diamond_gifts"][diamond_value]["volume"] = data_receive["volume"]

            utils.manipulate_json(gifts_json_path, "save", ttk_data_gifts)

            toast("success")

        except Exception as e:
            utils.error_log(e)
            toast("error")


def tiktok_logs(data_receive):

    data_receive = json.loads(data_receive)

    type_id = data_receive["type_id"]

    event_config_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_not.json"

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

    goal_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json"

    goal_data = utils.manipulate_json(goal_json_path, "load")

    if type_id == "get":

        goal_type = data["goal_type"]

        if goal_type == "gift":

            gifts_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/gifts.json"

            ttk_data_gifts = utils.manipulate_json(gifts_json_path, "load")

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

        utils.manipulate_json(goal_json_path, "save", goal_data)

    if type_id == "save_html":
        utils.update_goal(data)

    if type_id == "get_html":
        html_info = utils.update_goal(data)
        data_dump = json.dumps(html_info, ensure_ascii=False)
        return data_dump


def disclosure_py(type_id, data_receive):

    disclosure_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/disclosure.json"

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


def playlist_py(type_id, data):

    playlist_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/list_files/playlist.json"
    config_json_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json"

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

        queue_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/list_files/queue.json", "load")

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

    config_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/"
    commands_path = f"{config_path}commands.json"
    notfic_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/notfic.json"
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


def update_check(type_id):

    if type_id == "check0":
        return "false"
    
    if type_id == "check0":
        
        try:
            
            response = req.get("https://api.github.com/repos/GGTEC/VibesBot/releases/latest")
            response_json = json.loads(response.text)
            version = response_json["tag_name"]

            if version != "v1.0.0":
                return "true"

            else:
                return "false"
        except:
            
            return "false"

    elif type_id == "open":

        url = "https://github.com/GGTEC/VibesBot/releases"
        webbrowser.open(url, new=0, autoraise=True)


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
        response = get_video_info(link)
        media_name = response.title
        music_link = response.url
        music_thumb = response.thumb

        title_split = media_name.split(" - ")
        music_name = title_split[0]
        music_artist = title_split[1] if len(title_split) > 1 else ""

        img_data = req.get(music_thumb).content

        album_art_dir = f"{utils.local_work('datadir')}/web/src/player/images/album.png"
        with open(album_art_dir, "wb") as album_art_local:
            album_art_local.write(img_data)

        appdata_album_art_dir = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/images/album.png"
        with open(appdata_album_art_dir, "wb") as album_art_file:
            album_art_file.write(img_data)

        window.evaluate_js(f"update_image()")
        caching = 1

        if download_music(music_link):

            with open(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/list_files/currentsong.txt", "w", encoding="utf-8") as file_object:
                file_object.write(f"{media_name}")

            music_name_short = textwrap.shorten(media_name, width=30, placeholder="...")

            music_data = {
                "redeem_user": user,
                "music": music_name_short,
                "artist": music_artist,
            }


            data = {"type": "music", "html": utils.update_music(music_data)}
            
            data_dump = json.dumps(data)
            
            sk.broadcast_message(data_dump)

            window.evaluate_js(f"update_music_name('{music_name}', '{music_artist}')")

            aliases = {
                "{music_name}": music_name,
                "{music_name_short}": music_name_short,
                "{music_artist}": music_artist,
                "{username}": user,
            }

            music_webm_path = f"http://localhost:7000/src/player/cache/music.webm"
            window.evaluate_js(f"player('play', '{music_webm_path}', '1')")
            toast(f"Reproduzindo {music_name_short} - {music_artist}")

            data_append = {
                "type": "event",
                "message": utils.replace_all(utils.messages_file_load("music_playing"), aliases),
                "user_input": "",
            }

            append_notice(data_append)

            config_file_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json"

            config_data_player = utils.manipulate_json(config_file_path, "load")

            config_data_player["skip_requests"] = 0

            utils.manipulate_json(config_file_path, "save", config_data_player)

            caching = 0
            
        else:
            
            toast(f"Erro ao processar música {link} - {user}")

            data_append = {
                "type": "event",
                "message": utils.replace_all(utils.messages_file_load("music_process_cache_error"), aliases),
                "user_input": "",
            }

            append_notice(data_append)

    except Exception as e:
        
        utils.error_log(e)

        toast(f"Erro ao processar música {link} - {user}")

        data_append = {
            "type": "event",
            "message": utils.replace_all(utils.messages_file_load("music_process_cache_error"), aliases),
            "user_input": "",
        }

        append_notice(data_append)


def loopcheck():
    
    while True:

        try:

            playlist_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/list_files/playlist.json"
            queue_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/list_files/queue.json"
            config_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json"
            
            if loaded_status == 1:
                
                playlist_data = utils.manipulate_json(playlist_path, "load")
                playlist_execute_data = utils.manipulate_json(config_path, "load")
                
                queue_data = utils.manipulate_json(queue_path,"load")

                playlist_execute = int(playlist_execute_data["STATUS"])

                check_have_playlist = any(playlist_data.keys())
                check_have_queue = any(queue_data.keys())

                playing = window.evaluate_js(f"player('playing', 'none', 'none')")

                
                if caching == 0 and playing == "False":

                    
                    if check_have_queue:

                        queue_keys = [int(x) for x in queue_data.keys()]
                        music_data_key = str(min(queue_keys))

                        music = queue_data[music_data_key]["MUSIC"]
                        user = queue_data[music_data_key]["USER"]

                        del queue_data[music_data_key]

                        utils.manipulate_json(queue_path, "save", queue_data)

                        start_play(music, user)

                        time.sleep(5)

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
                        window.evaluate_js(f"update_music_name('Aguardando', 'Aguardando')")

                time.sleep(3)
                
        except Exception as e:
            
            utils.error_log(e)
            
            time.sleep(3)


def process_redem_music(user_input, redem_by_user):
    
    user_input = user_input.strip()
    
    toast(f"Processando pedido {user_input} - {redem_by_user}")
    
    config_music_path = F"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json"
    queue_json_path = F"{utils.local_work('appdata_path')}/VibesBot/web/src/player/list_files/queue.json"

    config_music_data = utils.manipulate_json(config_music_path, 'load')
    
    blacklist = config_music_data["blacklist"]
    
    max_duration = int(config_music_data["max_duration"])

    queue_data = utils.manipulate_json(queue_json_path, 'load')
    
    last_key = str(max(map(int, queue_data.keys()), default=0) + 1) if queue_data else "1"

    def start_process(user_input):
        
        try:
            if not any(item in user_input for item in blacklist):

                response = get_video_info(user_input)

                music_name, video_url, music_length = response.title, response.url, response.length

                if music_length < max_duration:

                    queue_data[last_key] = {"MUSIC": video_url, "USER": redem_by_user, "MUSIC_NAME": music_name}
                    utils.manipulate_json(queue_json_path, 'save', queue_data)

                    aliases = {"{username}": redem_by_user, "{user_input}": video_url, "{music}": music_name}
                    
                    data_append = {"type": "event", "message": utils.replace_all(utils.messages_file_load("music_added_to_queue"), aliases), "user_input": ""}
                    append_notice(data_append)

                else:
                    music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")
                    aliases = {"{max_duration}": str(max_duration), "{username}": str(redem_by_user),
                               "{user_input}": str(user_input), "{music}": str(music_name),
                               "{music_short}": str(music_name_short)}
                    
                    data_append = {"type": "event", "message": utils.replace_all(utils.messages_file_load("music_length_error"), aliases), "user_input": ""}
                    append_notice(data_append)
            else:

                music_name_short = textwrap.shorten(music_name, width=13, placeholder="...")
                aliases = {"{username}": str(redem_by_user), "{user_input}": str(user_input),
                           "{music}": str(music_name), "{music_short}": str(music_name_short)}
                
                data_append = {"type": "event", "message": utils.replace_all(utils.messages_file_load("music_blacklist"), aliases), "user_input": ""}
                append_notice(data_append)

        except Exception as e:

            utils.error_log(e)
            aliases = {"{username}": str(redem_by_user), "{user_input}": str(user_input)}
            data_append = {"type": "event", "message": utils.replace_all(utils.messages_file_load("music_add_error"), aliases), "user_input": ""}
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
            data_append = {"type": "STATUS_MUSIC_CONFIRM", "message": utils.messages_file_load("music_link_youtube"), "user_input": ""}
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
            subprocess.Popen(f"explorer '{path}\\VibesBot\\web'")
        except subprocess.CalledProcessError as e:
            utils.error_log(e)
            toast("Ocorreu um erro.")

    elif type_id == "errolog":
        
        file = f"{utils.local_work('appdata_path')}/VibesBot/web/src/error_log.txt"

        with open(file, "r", encoding="utf-8") as error_file:
            error_data = error_file.read()

        return error_data

    elif type_id == "errolog_clear":
        
        file = f"{utils.local_work('appdata_path')}/VibesBot/web/src/error_log.txt"

        with open(file, "w", encoding="utf-8") as error_file:
            error_file.write("")

        toast("Relatório de erros limpo")

    elif type_id == "discord":
        webbrowser.open("https://discord.io/ggtec", new=0, autoraise=True)

    elif type_id == "wiki":
        webbrowser.open("https://ggtec.netlify.app/apps/re/", new=0, autoraise=True)

    elif type_id == "debug-get":
        
        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/debug.json","load")

        return debug_data["debug"]

    elif type_id == "debug-save":
        
        debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/debug.json","load")
        debug_data["debug"] = link_profile

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/debug.json","save",debug_data)

        if link_profile == 1:
            
            toast( f"Configuração salva, reinicie o programa para iniciar no modo Debug Visual...")
            
        elif link_profile == 0:
            
            toast(f"Configuração salva, reinicie o programa para sair do modo Debug Visual...")


def chat_config(data_save, type_config):

    chat_file_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/chat_config.json"

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
                "share-role": data_received["share_role"]
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
            "time_format": chat_data.get("time-format"),
            "type_data": chat_data.get("type-data"),
            "data_show": chat_data.get("data-show"),
            "font_size": chat_data.get("font-size"),
            "wrapp_message": chat_data.get("wrapp-message"),
            "gift_role": chat_data.get("gift-role"),
            "like_role": chat_data.get("like-role"),
            "share_role": chat_data.get("share-role")
        }

        return json.dumps(chat_data_return, ensure_ascii=False)


def userdata_py(type_id, username):

    user_data_file_path = f"{utils.local_work('datadir')}/web/src/user_info/users_database.json"

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

        user_data_load = utils.manipulate_json(user_data_file_path, "load")

        if username in user_data_load:

            del user_data_load[username]
            
            utils.manipulate_json(user_data_file_path, "save", user_data_load)

            toast("Nome removido")


def commands_module(data) -> None:

    def send_error_level(user, user_level, command):
        
        aliases = {
            "{username}": str(user),
            "{user_level}": str(user_level),
            "{command}": str(command),
        }

        data_append = {
            "type": "event",
            "message": utils.replace_all(utils.messages_file_load("error_user_level"), aliases),
            "user_input": "",
        }

        append_notice(data_append)

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

    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/user_info/users_database.json","load")
    command_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/commands.json","load")
    command_data_prefix = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/commands_config.json","load")
    command_data_giveaway = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/commands.json","load")
    command_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","load")
    command_data_queue = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/commands.json","load")
    command_data_tts = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/tts.json","load")

    message_sender = data["user_id"]
    message_text = data["message"]
    user = message_sender
    
    username = data["user_name"]

    user_type = user_data_load[user]["roles"]

    command_string = message_text
    command_lower = command_string.lower()

    if len(command_string.split()) > 1:
        split_command = command_string.split(maxsplit=1)
        command, sufix = split_command

    else:
        sufix = None

    command = command_lower.split()[0].strip()

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
    }

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
            status = command_info["status"]
            user_level = command_info["user_level"]
            delay = int(command_info["delay"])
            last_use = command_info["last_use"]

            if check_perm(user_type, user_level):

                message_delay, check_time, current = utils.check_delay(delay, last_use)

                if check_time:

                    if status == 1:

                        command_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/commands.json","save",command_data)


                        data_append = {
                            "type": "command",
                            "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                            "user_input": sufix,
                        }

                        append_notice(data_append)

                        if command_info["type"] == "sound":
                            play_sound()
                    else:
                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)
                else:

                    data_append = {
                        "type": "event",
                        "message": message_delay,
                        "user_input": "",
                    }

                    append_notice(data_append)
            else:
                send_error_level(user, str(user_level), str(command))

        elif compare_strings(command, command_data_giveaway["add_user"]["command"]):

            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }

            append_notice(data_append)

            add_user_info = command_data_giveaway["add_user"]
            status = add_user_info["status"]
            delay = add_user_info["delay"]
            last_use = add_user_info["last_use"]
            user_level = add_user_info["user_level"]

            if status:

                if check_perm(user_type, user_level):

                    message_delay_global, check_time_global, current = utils.check_delay(delay, last_use)

                    if check_time_global:

                        user_input = command_string.split(add_user_info)

                        if sufix != "":
                            user_input = sufix

                            data = {"new_name": user_input.strip(), "user_level": "mod"}
                            giveaway_py("add_user", data)

                        add_user_info["last_use"] = current

                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/giveaway/commands.json","save",command_data_giveaway)
                    else:

                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay_global, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)
                else:

                    send_error_level(user, user_level, str(command))
            else:

                message_event = utils.replace_all(utils.messages_file_load("command_disabled"), aliases)

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": "",
                }

                append_notice(data_append)

        elif compare_strings(command, command_data_player["volume"]["command"]):

            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }

            append_notice(data_append)

            volume_info = command_data_player["volume"]
            delay = volume_info["delay"]
            last_use = volume_info["last_use"]
            status = volume_info["status"]
            user_level = volume_info["user_level"]

            if status:

                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay, last_use)

                    if check_time:

                        prefix_volume = volume_info["command"]

                        volume_value_command = command_lower.split(prefix_volume.lower())

                        if len(volume_value_command) > 1 and volume_value_command[1] != "":

                            volume_value_command = volume_value_command[1]

                            if volume_value_command.strip().isdigit():

                                volume_value_int = int(volume_value_command)

                                if volume_value_int in range(0, 101):

                                    volume_value = volume_value_int / 100

                                    window.evaluate_js(f"player('volume', 'none', {volume_value})")

                                    aliases_commands = {
                                        "{username}": str(user),
                                        "{volume}": str(volume_value_int),
                                    }

                                    data_append = {
                                        "type": "event",
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
                                        "type": "event",
                                        "message": utils.replace_all(utils.messages_file_load("command_volume_error"),aliases_commands),
                                        "user_input": "",
                                    }

                                    append_notice(data_append)

                            else:

                                data_append = {
                                    "type": "event",
                                    "message": utils.messages_file_load("command_volume_number"),
                                    "user_input": "",
                                }

                                append_notice(data_append)

                            volume_info["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player)

                        else:

                            volume_atual = window.evaluate_js(
                                f"player('get_volume', 'none', 'none')"
                            )

                            aliases_commands = {
                                "{username}": str(user),
                                "{volume}": str(volume_atual),
                            }

                            data_append = {
                                "type": "event",
                                "message": utils.replace_all(utils.messages_file_load("command_volume_response"),aliases_commands),
                                "user_input": "",
                            }

                            append_notice(data_append)

                            volume_info["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player)

                    else:
                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)

                else:

                    send_error_level(user, user_level, str(command))

            else:
                

                data_append = {
                    "type": "event",
                    "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
                    "user_input": "",
                }

                append_notice(data_append)

        elif compare_strings(command, command_data_player["skip"]["command"]):

            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }

            config_data_player = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json",type_id="load")

            skip_votes = int(config_data_player["skip_votes"])
            skip_requests = int(config_data_player["skip_requests"])
            skip_mod = config_data_player["skip_mod"]
            skip_users = config_data_player["skip_users"]

            delay = command_data_player["skip"]["delay"]
            last_use = command_data_player["skip"]["last_use"]
            status = command_data_player["skip"]["status"]
            user_level = command_data_player["skip"]["user_level"]

            if status:

                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay, last_use)

                    if check_time:

                        playing = window.evaluate_js(f"player('playing', 'none', 'none')")

                        if not playing == "False":
                            
                            if "moderator" in user_type and skip_mod == 1:
                                
                                window.evaluate_js(f"player('stop', 'none', 'none')")

                                aliases_commands = {
                                    "{username}": str(user),
                                }

                                data_append = {
                                    "type": "event",
                                    "message": utils.replace_all(utils.messages_file_load("command_skip_confirm"),aliases),
                                    "user_input": "",
                                }

                                append_notice(data_append)

                                command_data_player["skip"]["last_use"] = current

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player)

                                config_data_player["skip_requests"] = 0

                                utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json","save",config_data_player)

                            else:
                                if not user in skip_users:

                                    skip_requests = int(skip_requests) + 1

                                    aliases_commands = {
                                        "{username}": str(user),
                                        "{votes}": str(skip_requests),
                                        "{minimum}": str(skip_votes),
                                    }

                                    data_append = {
                                        "type": "event",
                                        "message": utils.replace_all(utils.messages_file_load("skip_votes"),aliases_commands),
                                        "user_input": "",
                                    }

                                    append_notice(data_append)

                                    if int(skip_requests) == skip_votes:

                                        window.evaluate_js(f"player('stop', 'none', 'none')")

                                        aliases_commands = {
                                            "{username}": str(user),
                                        }

                                        data_append = {
                                            "type": "event",
                                            "message": utils.replace_all(utils.messages_file_load("command_skip_confirm"),aliases_commands),
                                            "user_input": "",
                                        }

                                        append_notice(data_append)

                                        command_data_player["skip"]["last_use"] = current

                                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player,)

                                        config_data_player["skip_requests"] = 0
                                        config_data_player["skip_users"] = []

                                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json","save",config_data_player)

                                    else:

                                        skip_users.append(user)

                                        config_data_player["skip_users"] = skip_users
                                        config_data_player["skip_requests"] = int(skip_requests)

                                        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/config.json","save",config_data_player,)

                                else:
                                    aliases_commands = {
                                        "{username}": str(user),
                                    }

                                    data_append = {
                                        "type": "event",
                                        "message": utils.replace_all(utils.messages_file_load("command_skip_inlist"),aliases_commands),
                                        "user_input": "",
                                    }

                                    append_notice(data_append)

                                    command_data_player["skip"]["last_use"] = current

                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player,)

                        else:
                            aliases_commands = {
                                "{username}": str(user),
                            }

                            data_append = {
                                "type": "event",
                                "message": utils.replace_all(utils.messages_file_load("command_skip_noplaying"),aliases_commands),
                                "user_input": "",
                            }

                            append_notice(data_append)

                            command_data_player["skip"]["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player)
                    else:

                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)

                else:
                    
                    send_error_level(user, user_level, str(command))

            else:

                message_event = utils.replace_all(
                    utils.messages_file_load("command_disabled"), aliases
                )

                data_append = {
                    "type": "event",
                    "message": message_event,
                    "user_input": "",
                }

                append_notice(data_append)
        
        elif compare_strings(command,command_data_player['request']['command']):

            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }
            
            append_notice(data_append)

            delay = command_data_player['request']['delay']
            last_use = command_data_player['request']['last_use']
            status = command_data_player['request']['status']
            user_level = command_data_player['request']['user_level']
            
            message_delay, check_time, current = utils.check_delay(delay,last_use)
            
            if status:

                if check_perm(user_type, user_level):

                    if check_time:
                            
                            prefix_sr = command_data_player['request']['command']
                            user_input = command_string.split(prefix_sr)

                            if len(user_input) > 1 and user_input[1] != "":
                                
                                user_input = user_input[1]
                                
                                if sr_config_py('get-status','null') == 1:

                                    threading.Thread(target=process_redem_music, args=(user_input, username,), daemon=True).start()
                                    
                                else:
                                    
                                    data_append = {
                                        "type": "command",
                                        "message": utils.replace_all(utils.messages_file_load('music_disabled'), aliases),
                                        "user_input": sufix,
                                    }
                                    
                                    append_notice(data_append)
                                
                                    command_data_player['request']['last_use'] = current
                                    
                                    utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/player/config/commands.json","save",command_data_player)
                                    

                            else:

                                data_append = {
                                    "type": "command",
                                    "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                                    "user_input": sufix,
                                }
                                
                                append_notice(data_append)

                    else:
                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)
                        
                else:
                    send_error_level(user,user_level, str(command))

            else:
                
                data_append = {
                    "type": "command",
                    "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
                    "user_input": sufix,
                }

                append_notice(data_append)

        elif compare_strings(command, command_data_queue["add_queue"]["command"]):
            
            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }
            append_notice(data_append)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/commands.json","load")

            delay = command_data_queue["add_queue"]["delay"]
            last_use = command_data_queue["add_queue"]["last_use"]
            status = command_data_queue["add_queue"]["status"]
            user_level = command_data_queue["add_queue"]["user_level"]

            if status:

                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay, last_use)

                    if check_time:

                        if sufix != "":
                            
                            queue_file_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/queue.json"

                            queue_data = utils.manipulate_json(queue_file_path,"load")

                            if sufix not in queue_data:

                                queue_data.append(sufix)

                                utils.manipulate_json(queue_file_path,"save",queue_data)

                                toast("Nome adicionado")

                                aliases = {
                                    "{username}": str(user),
                                    "{command}": str(command),
                                    "{prefix}": str(prefix),
                                    "{user_level}": str(user_type),
                                    "{sufix}": str(sufix),
                                    "{random}": str(random_value),
                                    "{value}": str(sufix),
                                }

                                data_append = {
                                    "type": "event",
                                    "message": utils.replace_all(utils.messages_file_load("command_disabled"),aliases),
                                    "user_input": "",
                                }

                                append_notice(data_append)

                            else:

                                toast("O nome já está na lista")

                                aliases = {
                                    "{username}": str(user),
                                    "{command}": str(command),
                                    "{prefix}": str(prefix),
                                    "{user_level}": str(user_type),
                                    "{sufix}": str(sufix),
                                    "{random}": str(random_value),
                                    "{value}": str(sufix),
                                }


                                data_append = {
                                    "type": "event",
                                    "message": utils.messages_file_load("response_namein_queue"),
                                    "user_input": "",
                                }

                                append_notice(data_append)

                            command_data_queue["add_queue"]["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/commands.json","save",command_data_queue)

                        else:

                            data_append = {
                                "type": "event",
                                "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                                "user_input": "",
                            }

                            append_notice(data_append)

                    else:
                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)

                else:
                    send_error_level(user, user_level, str(command))

            else:

                data_append = {
                    "type": "command",
                    "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
                    "user_input": sufix,
                }

                append_notice(data_append)

        elif compare_strings(command, command_data_queue["check_queue"]["command"]):


            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }
            append_notice(data_append)

            delay, last_use, status, user_level = (
                command_data_queue["check_queue"]["delay"],
                command_data_queue["check_queue"]["last_use"],
                command_data_queue["check_queue"]["status"],
                command_data_queue["check_queue"]["user_level"],
            )

            response = utils.messages_file_load("response_get_queue")

            if status:

                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay, last_use)

                    if check_time:

                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(str(response), aliases),
                            "user_input": "",
                        }
                        append_notice(data_append)

                        command_data_queue["check_queue"]["last_use"] = current

                        utils.manipulate_json("save",f"{utils.local_work('appdata_path')}/tiktoktbot/web/src/queue/commands.json",command_data_queue)
                    else:

                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)
                else:

                    send_error_level(user, user_level, str(command))
            else:
                
                message_event = utils.replace_all(utils.messages_file_load("command_disabled"), aliases)

                data_append = {
                    "type": "command",
                    "message": message_event,
                    "user_input": sufix,
                }
                append_notice(data_append)

        elif compare_strings(command, command_data_queue["rem_queue"]["command"]):

            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }
            append_notice(data_append)

            delay, last_use, status, user_level = (
                command_data_queue["rem_queue"]["delay"],
                command_data_queue["rem_queue"]["last_use"],
                command_data_queue["rem_queue"]["status"],
                command_data_queue["rem_queue"]["user_level"],
            )

            if status:

                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay, last_use)

                    if check_time:

                        if sufix != "":

                            queue_file_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/queue/queue.json"
                            
                            queue_data = utils.manipulate_json(queue_file_path,"load")

                            if sufix in queue_data:

                                queue_data.remove(sufix)

                                utils.manipulate_json( queue_file_path,"save", queue_data)

                                toast("Nome removido")

                                aliases = {
                                    "{username}": str(user),
                                    "{command}": str(command),
                                    "{prefix}": str(prefix),
                                    "{user_level}": str(user_type),
                                    "{sufix}": str(sufix),
                                    "{random}": str(random_value),
                                    "{value}": str(sufix),
                                }

                                response = utils.messages_file_load("response_rem_queue")

                            else:
                                toast("O nome não está na lista")

                                aliases = {
                                    "{username}": str(user),
                                    "{command}": str(command),
                                    "{prefix}": str(prefix),
                                    "{user_level}": str(user_type),
                                    "{sufix}": str(sufix),
                                    "{random}": str(random_value),
                                    "{value}": str(sufix),
                                }

                                response = utils.messages_file_load("response_noname_queue")

                            command_data_queue["rem_queue"]["last_use"] = current

                            utils.manipulate_json(f"{utils.local_work('appdata_path')}/tiktoktbot/web/src/queue/commands.json","save",command_data_queue)

                        else:
                            data_append = {
                                "type": "event",
                                "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                                "user_input": "",
                            }

                            append_notice(data_append)

                    else:
                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)

                else:

                    send_error_level(user, user_level, str(command))

            else:
                data_append = {
                    "type": "command",
                    "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
                    "user_input": sufix,
                }

                append_notice(data_append)

        elif compare_strings(command, command_data_tts["command"]):

            data_append = {
                "type": "command",
                "message": utils.replace_all(str(utils.messages_file_load("event_command")), aliases),
                "user_input": sufix,
            }
            append_notice(data_append)

            delay, last_use, status, user_level = (
                command_data_tts["delay"],
                command_data_tts["last_use"],
                command_data_tts["status"],
                command_data_tts["user_level"],
            )

            if status:

                if check_perm(user_type, user_level):

                    message_delay, check_time, current = utils.check_delay(delay, last_use)

                    if check_time:

                        if sufix != "":

                            user_input_short = textwrap.shorten(sufix, width=300, placeholder=" ")
                            tts = gTTS(text=user_input_short, lang="pt-br", slow=False)

                            mp3_fp = BytesIO()
                            tts.write_to_fp(mp3_fp)
                            mp3_fp.seek(0)

                            tts_playing = pygame.mixer.music.get_busy()

                            while tts_playing:
                                tts_playing = pygame.mixer.music.get_busy()
                                time.sleep(2)

                            pygame.mixer.music.load(mp3_fp, "mp3")
                            pygame.mixer.music.play()

                            aliases = {
                                "{username}": str(user),
                                "{command}": str(command),
                                "{prefix}": str(prefix),
                                "{user_level}": str(user_type),
                                "{sufix}": str(sufix),
                                "{random}": str(random_value),
                                "{value}": str(sufix),
                            }

                            command_data_tts["last_use"] = current

                            utils.manipulate_json(
                                "save",
                                f"{utils.local_work('appdata_path')}/tiktoktbot/web/src/config/tts.json",
                                command_data_tts,
                            )

                        else:

                            data_append = {
                                "type": "event",
                                "message": utils.replace_all(utils.messages_file_load("command_sufix"), aliases),
                                "user_input": "",
                            }

                            append_notice(data_append)

                    else:
                        data_append = {
                            "type": "event",
                            "message": utils.replace_all(message_delay, aliases),
                            "user_input": "",
                        }

                        append_notice(data_append)

                else:

                    send_error_level(user, user_level, str(command))
            else:

                data_append = {
                    "type": "command",
                    "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
                    "user_input": sufix,
                }

                append_notice(data_append)


    else:

        data_append = {
            "type": "command",
            "message": utils.replace_all(utils.messages_file_load("command_disabled"), aliases),
            "user_input": sufix,
        }

        append_notice(data_append)


def close():

    if window_chat_open == 1:
        window_chat.destroy()

    if window_events_open == 1:
        window_events.destroy()

    sys.exit(0)


def on_resize(width, height):

    min_width = 1200
    min_height = 600

    if width < min_width or height < min_height:
        window.resize(min_width, min_height)


def loaded():
    
    global loaded_status

    loaded_status = 1

    authdata = auth_data(f"{utils.local_work('appdata_path')}/VibesBot/web/src/auth/auth.json")

    username = authdata.USERNAME()

    if username == "":
        data = {"autenticated": "false"}
    else:
        data = {"autenticated": "true"}

    return json.dumps(data, ensure_ascii=False)


def update_goal(goal_type, ammount):
    
    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")
    
    if goal_data[goal_type]["status"] == 1:
        
        if int(ammount) >= int(goal_data[goal_type]["goal"]):
            
            if goal_data[goal_type]["event"] == "double":
                
                goal = int(goal_data[goal_type]["goal"]) * 2

            elif goal_data[goal_type]["event"] == "add":
                
                if goal_data[goal_type]["goal_after"] == "":
                    
                    goal = int(goal_data[goal_type]["goal"]) + int(goal_data[goal_type]["goal"])

                    goal_data[goal_type]["goal_after"] = goal
                    goal_data[goal_type]["goal"] = goal

                else:
                    
                    goal = int(goal_data[goal_type]["goal"]) + int(goal_data[goal_type]["goal_after"])
                    goal_data[goal_type]["goal"] = goal
            else:
                
                goal = int(goal_data[goal_type]["goal"])
            
            if goal_data[goal_type]["sound_status"] == 1 and goal_data[goal_type]["sound_file"] != "":
                
                play_sound(goal_data[goal_type]["sound_file"],goal_data[goal_type]["sound_volume"])
                
                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","save",goal_data)

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

        sk.broadcast_message(json.dumps(data_goal))


def update_roles(data):
       
    user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/user_info/users_database.json","load")
    chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/chat_config.json","load")

    type_id = data["type_id"]
    user = data["user"]

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
            
            user = data["user"]

            if user in user_data_load:
                if user_data_load[user]["shares"] != "":
                    user_shares = int(user_data_load[user]["shares"])
                    user_data_load[user]["shares"] = user_shares + 1
                else:
                    user_data_load[user]["shares"] = user_shares

                if not "shares" in roles and (user_data_load[user]["shares"]) > int(chat_data["share-role"]):
                    roles.append("shares")

        elif type_id == "follow":
            user = data["user"]

            if user in user_data_load and not "follow" in roles:
                roles.append("follow")

        elif type_id == "gifts":
            user = data["user"]
            gifts = data["gifts"]

            if user in user_data_load:
                if user_data_load[user]["gifts"] != "":
                    user_gifts = int(user_data_load[user]["gifts"])
                    user_data_load[user]["gifts"] = user_gifts + int(gifts)
                else:
                    user_data_load[user]["gifts"] = gifts

                if not "gifts" in roles and int(user_data_load[user]["gifts"]) > int(
                    chat_data["gift-role"]
                ):
                    roles.append("gifts")

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/user_info/users_database.json","save",user_data_load)


async def on_comment(event: CommentEvent):
    
    def add_user_database(data):
        
        try:
            role_mapping = {
                "follower": "follow",
                "moderator": "moderator",
                "subscriber": "subscriber",
            }

            user_data_load = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/user_info/users_database.json","load")

            if data["user_id"] not in user_data_load:
                
                roles = ["spec"]

                for role_key, role_var in role_mapping.items():
                    
                    if data[role_key] == True:
                        roles.append(role_var)

                    user_data_load[data["user_id"]] = {
                        "display_name": data["display_name"],
                        "roles": roles,
                        "likes": "",
                        "shares": "",
                        "gifts": "",
                    }
            else:
                
                roles = user_data_load[data["user_id"]]["roles"]

                for role_key, role_var in role_mapping.items():
                    
                    if role_key not in roles and data[role_key] == True:
                        roles.append(role_var)
                        
                    elif role_key in roles and data[role_key] == False:
                        roles.remove(role_var)

                user_data_load[data["user_id"]] = {
                    "display_name": data["display_name"],
                    "roles": roles,
                    "likes": user_data_load[data["user_id"]]["likes"],
                    "shares": user_data_load[data["user_id"]]["shares"],
                    "gifts": user_data_load[data["user_id"]]["gifts"],
                }

                
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/user_info/users_database.json","save",user_data_load)

        except Exception as e:
            utils.error_log(e)

    username = event.user.nickname
    userid = event.user.unique_id
    comment = event.comment
    follower = event.user.is_following
    moderator = event.user.is_moderator     
    badges_list = event.user.badges
    top_gifter = event.user.is_top_gifter
    subscriber = event.user.is_subscriber
    
    try:

        chat_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/chat_config.json","load")
        
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

                if badge.image and badge.image.urls:
                    first_url = badge.image.urls[0]
                    
                badge_dict = {
                    "label": badge.label,
                    "name": badge.name,
                    "first_url": first_url,
                }

                badges.append(badge_dict)

        data_res = {
            "type": "PRIVMSG",
            "display_name": username,
            "user_id": userid,
            "user_name": username,
            "message": comment,
            "badges": badges,
            "follower": follower,
            "moderator": moderator,
            "subscriber": subscriber,
            "top_gifter": top_gifter,    
            "font_size": chat_data["font-size"],
            "chat_color_border": chat_data["chat-color-border"],
            "chat_color_name": chat_data["chat-color-name"],
            "chat_name_select": chat_data["chat-name-select"],
            "chat_border_select": chat_data["chat-border-select"],
            "wrapp_message": chat_data["wrapp-message"],
            "data_show": chat_data["data-show"],
            "chat_time": chat_time,
            "type_data": chat_data["type-data"],
        }

        add_user_database(data_res)

        window.evaluate_js(f"append_message({json.dumps(data_res, ensure_ascii=False)})")

        if window_chat_open == 1:
            
            window_chat.evaluate_js(f"append_message_out({json.dumps(data_res, ensure_ascii=False)})")

        commands_module(data_res)

    except Exception as e:
        utils.error_log(e)


async def on_connect(_: ConnectEvent):


    like_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/likes.json","load")
    
    like_list = {
        "likes" : {
            
        }
    }
    
    utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/likes.json","save",like_list)
    
    join_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/joins.json","load")
    
    join_list = [] 
    
    utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/joins.json","save",join_list)

    data_append = {
        "type": "event",
        "message": utils.messages_file_load(f"event_ttk_connect"),
        "user_input": "",
    }
    
    append_notice(data_append)

    toast("Conectado ao chat do TikTok.")
    
    send_discord_webhook({"type_id": "live_start"})

    tiktok_conn = 1


async def on_disconnect(event: DisconnectEvent):
    
    tiktok_conn = 0

    message_event = utils.messages_file_load("event_ttk_disconected")

    data_append = {
        "type": "live_end",
        "message": message_event,
        "user_input": "",
    }

    append_notice(data_append)

    window.evaluate_js(f"update_specs_tiktok('disconect')")

    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")

    goal_data["max_viewer"]["max_specs"] = 0
    goal_data["diamonds"]["total_diamonds"] = 0
    goal_data["share"]["total_shares"] = 0
    goal_data["gift"]["total_gifts"] = 0

    utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","save",goal_data)

    send_discord_webhook({"type_id": "live_end"})


async def on_like(event: LikeEvent):
    
    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_not.json", "load")
    like_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/likes.json","load")
    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")

    try:
        
        username = event.user.nickname
        user_id = event.user.unique_id
        likes_send = event.likes
        total_likes = event.total_likes
        
        like_list = like_data["likes"]
        
        send_discord_webhook({"type_id": "like", "username" : username, "likes_send" : likes_send, "total_likes" : total_likes})
        
        if user_id not in like_list:
            
            current_time = int(time.time())
            
            like_list[user_id] = current_time
            
            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/likes.json","save",like_data)
            
            aliases = {
                "{username}": username,
            }
            
            data_append = {
                "type": "like",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_like"), aliases),
                "user_input": "",
            }
            
            append_notice(data_append)

            if event_config_data["ttk_like"]["sound"] == 1:
                
                audio_path = event_config_data["ttk_like"]["sound_loc"]
                audio_volume = event_config_data["ttk_like"]["sound_volume"]

                threading.Thread(target=play_sound,args=(audio_path,audio_volume),daemon=True).start()
            
        else:
            
            delay = event_config_data["ttk_like"]["delay"]

            last_like = like_list[user_id]

            message_delay, check_time, current = utils.check_delay(delay, last_like)

            if check_time:
                
                like_list[user_id] = current
                
                utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/likes.json","save",like_data)

                aliases = {
                    "{username}": username,
                    "{amount}" : likes_send
                }
                
                data_append = {
                    "type": "like",
                    "message": utils.replace_all(utils.messages_file_load("event_ttk_like"),aliases),
                    "user_input": "",
                }

                append_notice(data_append)

        update_goal("likes", total_likes)

        data_roles = {
            "type_id": "likes",
            "user": user_id,
            "likes": likes_send,
        }

        update_roles(data_roles)

        aliases = {
            "{username}": username,
            "{amount}" : likes_send
        }
        
        data = {
            "goal": goal_data["likes"]["goal"],
            "total": total_likes,
            "user": utils.replace_all(utils.messages_file_load("event_ttk_like"),aliases)
        }

        data_dump = json.dumps(data, ensure_ascii=False)

        window.evaluate_js(f"update_carousel_tiktok('likes',{data_dump})")

    except Exception as e:
        utils.error_log(e)


async def on_join(event: JoinEvent):
    
    join_list = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/joins.json","load")

    if event.user != None:
        
        username = event.user.nickname
        user_id = event.user.unique_id

        if user_id not in join_list:
            
            join_list.append(user_id)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/joins.json","save",join_list)
            
            aliases = {"{username}": username}

            data_append = {
                "type": "join",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_join"), aliases),
                "user_input": ""
            }
            
            append_notice(data_append)


async def on_gift(event: GiftEvent):
    
    ttk_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/gifts.json","load")

    gift_id = str(event.gift.id)
    gift_diamonds = str(event.gift.info.diamond_count)

    gifts_data = ttk_data["gifts"]
    diamonds_data = ttk_data["diamond_gifts"]

    
    user_id = event.user.unique_id
    username = event.user.nickname
        
    try:
        
        if gift_id in gifts_data:
            
            giftname = gifts_data[gift_id]["name_br"]
        else :
            giftname = event.gift.info.name
            
            if isinstance(giftname, tuple):
                giftname = giftname[0]
            
        print(giftname)
        
        if event.gift.streakable and not event.gift.streaking:
            
            
            aliases = {
                "{username}": username,
                "{amount}": event.gift.count,
                "{giftname}": giftname,
                "{diamonds}": gift_diamonds,
                "{id}": gift_id,
            }
            
            
            send_discord_webhook({
                "type_id": "gift", 
                "username" : username, 
                "gifts_send" : event.gift.count, 
                "gift_name" : giftname,
                "diamonds": gift_diamonds
            })

            data_append = {
                "type": "gift",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_gift"), aliases),
                "user_input": "",
            }
            
            append_notice(data_append)

            data_roles = {
                "type_id": "gifts",
                "user": user_id,
                "gifts": event.gift.count,
            }

            update_roles(data_roles)


            if gift_id in gifts_data:
                
                if (gifts_data[gift_id]["status"] == 1 and gifts_data[gift_id]["audio"] != ""):
                    
                    audio_path = ttk_data["gifts"][gift_id]["audio"]
                    audio_volume = ttk_data["gifts"][gift_id]["volume"]

                    threading.Thread(target=play_sound,args=( audio_path,audio_volume),daemon=True).start()

                elif gift_diamonds in diamonds_data:
                    
                    if (diamonds_data[gift_diamonds]["status"] == 1 and diamonds_data[gift_diamonds]["sound"] != ""):
                        
                        audio_path = ttk_data["diamond_gifts"][gift_diamonds]["sound"]
                        audio_volume = ttk_data["diamond_gifts"][gift_diamonds]["volume"]

                        threading.Thread(target=play_sound,args=(audio_path,audio_volume),daemon=True).start()

            elif gift_diamonds in diamonds_data:
                
                if (diamonds_data[gift_diamonds]["status"] == 1 and diamonds_data[gift_diamonds]["sound"] != ""):
                    
                    audio_path = ttk_data["diamond_gifts"][gift_diamonds]["sound"]
                    audio_volume = ttk_data["diamond_gifts"][gift_diamonds]["volume"]

                    threading.Thread(target=play_sound,args=(audio_path,audio_volume), daemon=True).start()


            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")
            
            if int(gift_id) == int(goal_data["gift"]["gift"]):
                
                total_gifts = int(goal_data["gift"]["total_gifts"]) + int(event.gift.count)
                goal_data["gift"]["total_gifts"] = total_gifts

            diamonds = int(gift_diamonds) * int(event.gift.count)
            
            total_diamonds = int(goal_data["diamonds"]["total_diamonds"]) + int(diamonds)
            
            goal_data["diamonds"]["total_diamonds"] = int(total_diamonds)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json", "save", goal_data)

            if int(gift_id) == int(goal_data["gift"]["gift"]):
                update_goal("gift", total_gifts)

            update_goal("diamonds", total_diamonds)

        elif not event.gift.streakable:
                    
            aliases = {
                "{username}": username,
                "{amount}": event.gift.count,
                "{giftname}": giftname,
                "{diamonds}": gifts_data[gift_id]["value"],
                "{id}": gifts_data[gift_id]["id"],
            }
            print(aliases)
            
            send_discord_webhook({
                "type_id": "gift", 
                "username" : username, 
                "gifts_send" : event.gift.count, 
                "gift_name" : giftname,
                "diamonds": gifts_data[gift_id]["value"]
            })
            

            data_append = {
                "type": "gift",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_gift"), aliases),
                "user_input": "",
            }

            append_notice(data_append)
            
            data_roles = {
                "type_id": "gifts",
                "user": user_id,
                "gifts": event.gift.count,
            }

            update_roles(data_roles)

            if gift_id in gifts_data:
                
                if (gifts_data[gift_id]["status"] == 1 and gifts_data[gift_id]["audio"] != ""):
                    
                    audio_path = ttk_data["gifts"][gift_id]["audio"]
                    audio_volume = ttk_data["gifts"][gift_id]["volume"]

                    threading.Thread(target=play_sound,args=(audio_path,audio_volume,),daemon=True).start()

                elif gift_diamonds in diamonds_data:
                    
                    if (diamonds_data[gift_diamonds]["status"] == 1 and diamonds_data[gift_diamonds]["sound"] != ""):
                        
                        audio_path = ttk_data["diamond_gifts"][gift_diamonds]["sound"]
                        audio_volume = ttk_data["diamond_gifts"][gift_diamonds]["volume"]

                        threading.Thread(target=play_sound,args=(audio_path,audio_volume,),daemon=True,).start()

            elif gift_diamonds in diamonds_data:
                
                if (diamonds_data[gift_diamonds]["status"] == 1 and diamonds_data[gift_diamonds]["sound"] != ""):
                    
                    audio_path = ttk_data["diamond_gifts"][gift_diamonds]["sound"]
                    audio_volume = ttk_data["diamond_gifts"][gift_diamonds]["volume"]

                    threading.Thread(target=play_sound,args=(audio_path,audio_volume,),daemon=True,).start()

                
            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")


            if int(gift_id) == int(goal_data["gift"]["gift"]):
                
                total_gifts = goal_data["gift"]["total_gifts"] + int(event.gift.count)
                goal_data["gift"]["total_gifts"] = total_gifts

                update_goal("gift", total_gifts)

            diamonds = int(gift_diamonds)
            
            total_diamonds = int(goal_data["diamonds"]["total_diamonds"]) + int(diamonds)
            
            goal_data["diamonds"]["total_diamonds"] = total_diamonds

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","save",goal_data)
            
            update_goal("diamonds", total_diamonds)

    except Exception as e:
        
        utils.error_log(e)


async def on_follow(event: FollowEvent):
    
    event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_not.json", "load")
    goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")
    ttk_follows = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/follow.json","load")

    username = event.user.nickname
    user_id = event.user.unique_id

    try:
        
        if user_id not in ttk_follows:
            
            ttk_follows.append(user_id)

            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/follow.json","save",ttk_follows)

            aliases = {
                "{username}": username
            }

            data_append = {
                "type": "follow",
                "message": utils.replace_all(utils.messages_file_load("event_ttk_follow"), aliases),
                "user_input": "",
            }
        
            append_notice(data_append)
            
            send_discord_webhook({"type_id": "follow", "username" : username})

            if event_config_data["ttk_follow"]["sound"] == 1:
                
                audio_path = event_config_data["ttk_follow"]["sound_loc"]
                audio_volume = event_config_data["ttk_follow"]["sound_volume"]

                threading.Thread(target=play_sound,args=(audio_path,audio_volume,),daemon=True).start()

        data_roles = {"type_id": "follow", "user": user_id}

        update_roles(data_roles)

        update_goal("follow", event.total_followers)

        data = {"goal": goal_data["follow"]["goal"], "total": event.total_followers}

        data_dump = json.dumps(data, ensure_ascii=False)

        window.evaluate_js(f"update_carousel_tiktok('update_follows',{data_dump})")

    except Exception as e:
        utils.error_log(e)


async def on_share(event: ShareEvent):
    
    try:
        user_id = event.user.unique_id
        
        event_config_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_not.json", "load")
        
        aliases = {"{username}": event.user.nickname}

        goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")

        total_shares = int(goal_data["share"]["total_shares"]) + 1
        goal_data["share"]["total_shares"] = int(total_shares)
        
        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","save",goal_data)

        data_roles = {"type_id": "share", "user": user_id}

        update_roles(data_roles)
        update_goal("share", total_shares)
        send_discord_webhook({"type_id": "share", "username" : event.user.nickname})
        
        data_append = {
            "type": "share",
            "message":  utils.replace_all(utils.messages_file_load("event_ttk_share"), aliases),
            "user_input": "",
        }
        
        append_notice(data_append)
        
        if event_config_data["ttk_share"]["sound"] == 1:
            
            audio_path = event_config_data["ttk_share"]["sound_loc"]
            audio_volume = event_config_data["ttk_share"]["sound_volume"]

            threading.Thread(target=play_sound,args=(audio_path,audio_volume),daemon=True).start()
        
        

    except Exception as e:
        utils.error_log(e)


async def on_viewer_update(event: ViewerUpdateEvent):
    
    if event.viewer_count != None:
        
        if int(event.viewer_count) > int(1):
            
            goal_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","load")

            max_specs = int(goal_data["max_viewer"]["max_specs"])

            if int(event.viewer_count) > max_specs:
                
                goal_data["max_viewer"]["max_specs"] = int(event.viewer_count)
                update_goal("max_viewer", int(event.viewer_count))


            utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/goal.json","save",goal_data)

            window.evaluate_js(f"update_specs_tiktok({int(event.viewer_count)})")

            topviewers = event.top_viewers

            for item in topviewers:
                
                if item.user.nickname != None and item.rank == 1:
                    
                    avatar_list = item.user.avatar.urls
                    avatar = avatar_list[0]
                    username = item.user.nickname
                    diamonds = item.coins_given
                    rank = item.rank

                    user_info = {
                        "rank": rank,
                        "user": username,
                        "avatar": avatar,
                        "diamonds": diamonds,
                    }

                    data_dump = json.dumps(user_info, ensure_ascii=False)

                    window.evaluate_js(f"update_carousel_tiktok('update_topspecs',{data_dump})")


async def on_envelope(event: EnvelopeEvent):
    
    user = event.treasure_box_user.nickname

    aliases = {"{username}": user}

    data_append = {
        "type": "chest",
        "message": utils.replace_all(utils.messages_file_load("event_ttk_envelope"), aliases),
        "user_input": "",
    }

    append_notice(data_append)
    
    send_discord_webhook({"type_id": "envelope", "username" : event.user.nickname})


async def on_unknownevent(event: UnknownEvent):
    
    type_mess = event.type
    binary_mess = event.binary
    data_mess = event.data

    data_append = {
        "type": "event",
        "message": f"Mensagem do tipo (UnknowEvent) recebida {type_mess}{binary_mess}{data_mess}",
        "user_input": "",
    }

    append_notice(data_append)


async def on_error(error: Exception):
    
    data_append = {
        "type": "event",
        "message": f"Mensagem do tipo (Error) recebida {error}",
        "user_input": "",
    }

    append_notice(data_append)


def webview_start_app(app_mode):
    
    global window, window_chat, window_events, window_chat_open

    def set_window_chat_open():
        global window_chat_open

        window_chat_open = 1

    def set_window_chat_close():
        global window_chat_open

        window_chat_open = 0

    def set_window_events_open():
        global window_events_open

        window_events_open = 1

    def set_window_events_close():
        global window_events_open

        window_events_open = 0

    debug_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/debug.json","load")

    debug_status = debug_data["debug"]

    if debug_status == 0:
        debug_status = False
        
    elif debug_status == 1:
        debug_status = True

    if app_mode == "normal":
        
        window = webview.create_window("VibesBot",f"{utils.local_work('datadir')}/web/index.html",width=1200,height=680,min_size=(1200, 680))

        window.events.closed += close
        window.events.resized += on_resize

        window.expose(
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
        )

        webview.start(storage_path=utils.local_work("datadir"),private_mode=True,debug=True,http_server=True,http_port=7000)

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


def start_ttk():
    
    while True:
        
        authdata = auth_data(f"{utils.local_work('appdata_path')}/VibesBot/web/src/auth/auth.json")

        username = authdata.USERNAME()

        if tiktok_conn == 0 and username != "":
            
            try:
                
                cookie_data = {
                    "sessionid": authdata.SESSIONID(),
                    "sid_guard": authdata.SIDGUARD(),
                }

                client_ttk: TikTokLiveClient = TikTokLiveClient(
                    unique_id='ronaldinhososiaoficial',
                    enable_detailed_gifts=True,
                    additional_cookies=cookie_data,
                )

                client_ttk.add_listener("comment", on_comment)
                client_ttk.add_listener("connect", on_connect)
                client_ttk.add_listener("like", on_like)
                client_ttk.add_listener("join", on_join)
                client_ttk.add_listener("gift", on_gift)
                client_ttk.add_listener("follow", on_follow)
                client_ttk.add_listener("share", on_share)
                client_ttk.add_listener("viewer_update", on_viewer_update)
                client_ttk.add_listener("envelope", on_envelope)
                client_ttk.add_listener("disconnect", on_disconnect)
                client_ttk.add_listener("error", on_error)

                client_ttk.run()

                time.sleep(10)

            except Exception as e:
                
                if type(e).__name__ != "LiveNotFound":
                    utils.error_log(e)

                time.sleep(10)


def start_app():
    

    def lock_file():
        
        lock_file_path = f"{utils.local_work('appdata_path')}/VibesBot/web/my_program.lock"

        try:
            file_handle = win32file.CreateFile(
                lock_file_path,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.CREATE_ALWAYS,
                win32file.FILE_ATTRIBUTE_NORMAL,
                None,
            )

            win32file.LockFile(file_handle, 0, 0, 0, 0x2)

        except win32file.error as e:
            error_message = "O programa já está em execução, aguarde."
            messagebox.showerror("Erro", error_message)
            sys.exit(0)


    def start_log_files():

        MAX_LOG_SIZE = 1024 * 1024 * 10  

        log_file_path = f"{utils.local_work('appdata_path')}/VibesBot/web/src/error_log.txt"

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

        event_log_data = utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","load")
        event_list = event_log_data["event-list"]

        if len(event_list) > 100:
            event_list = event_list[-100:]
            event_log_data["event-list"] = event_list

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/event_log.json","save",event_log_data)

        join_list = []

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/joins.json","save",join_list)

        like_data = {"likes": {}}

        utils.manipulate_json(f"{utils.local_work('appdata_path')}/VibesBot/web/src/config/likes.json","save",like_data)
    
    
    lock_file()
    start_log_files()
    
    utils.compare_and_insert_keys()
    utils.get_files_list()
    
    pygame.init()
    pygame.mixer.init()

    threading.Thread(target=loopcheck, args=(), daemon=True).start()
    threading.Thread(target=sk.start_server, args=("localhost", 7688), daemon=True).start()
    threading.Thread(target=start_ttk, args=(), daemon=True).start()


    if getattr(sys, "frozen", False):
        utils.splash_close()

    webview_start_app("normal")



start_app()
