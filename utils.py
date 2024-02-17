# -*- coding: utf-8 -*-
import json
import os
import shutil
import sys
import time
import pytz
import importlib
import requests as req

import tkinter.messagebox as messagebox
from dotenv import load_dotenv
from random import randint
from bs4 import BeautifulSoup as bs
from errorlog import ErrorManager

if getattr(sys, 'frozen', False):
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash


def check_local_work():

    if getattr(sys, 'frozen', False):
        return True
    else:
        return False


def local_work(type_id):

    if type_id == 'datadir':

        extDataDir = os.getcwd()

        if getattr(sys, 'frozen', False):
            extDataDir = f"{sys._MEIPASS}"

        return extDataDir

    elif type_id == 'appdata_path':

        appdata_path = f"{os.getenv('APPDATA')}/VibesBot/web/src"

        return appdata_path
    
    elif type_id == 'tempdir':

        appdata_path = os.getenv('APPDATA')

        return appdata_path


load_dotenv(dotenv_path=os.path.join(local_work('datadir'), '.env'))

def clear_logs():

    
    errormanager = ErrorManager()

    errormanager.clear_logs()

    return True


def get_recent_logs():

    
    errormanager = ErrorManager()

    return errormanager.get_recent_logs()


def error_log(ex):

    
    errormanager = ErrorManager()

    errormanager.error_log(ex)


class DictDot:

    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]


def manipulate_json(custom_path, type_id, data=None):

    try:

        if type_id == 'load':

            with open(custom_path, 'r',encoding='utf-8') as file:
                loaded_data = json.load(file)
            return loaded_data
        elif type_id == 'save':

            with open(custom_path, 'w',encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

    except FileNotFoundError:
        error_log(f'O arquivo {custom_path} não foi encontrado.')

    except Exception as e:
        error_log(custom_path)
        error_log(e)


def splash_close():
    pyi_splash.close()

 
def find_between(s, first, last):

    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]

    except ValueError:

        return False


def check_image(image):

    try:
        respon = req.get(url=image, stream=True)

        if respon.status_code == 200:
            return True
        else:
            return False
        
    except req.exceptions.RequestException as e:

        return False
    
    except Exception as e:

        return False
    

def convert_opacity_to_hex(opacity):

    if opacity < 0 or opacity > 1:
        raise ValueError("Opacity must be between 0 and 1")

    hex_list = [
        "FF", "FC", "FA", "F7", "F5", "F2", "F0", "ED", "EB", "E8",
        "E6", "E3", "E0", "DE", "DB", "D9", "D6", "D4", "D1", "CF",
        "CC", "C9", "C7", "C4", "C2", "BF", "BD", "BA", "B8", "B5",
        "B3", "B0", "AD", "AB", "A8", "A6", "A3", "A1", "9E", "9C",
        "99", "96", "94", "91", "8F", "8C", "8A", "87", "85", "82",
        "80", "7D", "7A", "78", "75", "73", "70", "6E", "6B", "69",
        "66", "63", "61", "5E", "5C", "59", "57", "54", "52", "4F",
        "4D", "4A", "47", "45", "42", "40", "3D", "3B", "38", "36",
        "33", "30", "2E", "2B", "29", "26", "24", "21", "1F", "1C",
        "1A", "17", "14", "12", "0F", "0D", "0A", "08", "05", "03", "00"
    ]

    index = round(opacity * (len(hex_list) - 1))
    hex_opacity = hex_list[index]

    return hex_opacity


def update_ranks(data):

    ranks_config_data = manipulate_json(f"{local_work('appdata_path')}/config/rank.json", "load")

    type_id = data["type_id"]
    info = data["info"]
    rank_type = ranks_config_data["rank_type"]
    rank_side = ranks_config_data["rank_side"]
    font_size = ranks_config_data["font_size"]
    font_color = ranks_config_data["font_color"]
    card_size = ranks_config_data["card_size"]
    image_size = ranks_config_data["image_size"]

    bg = ranks_config_data['bg']
    op = convert_opacity_to_hex(float(ranks_config_data['op'])) 

    with open(f"{local_work('appdata_path')}/html/ranks/{type_id}/{type_id}.html", 'r', encoding='utf-8') as file:
        content_html = file.read()

        soup = bs(content_html, 'html.parser')

        div = soup.find("div", {"class": f"event_block"})


    if rank_type == "card":
        
        if rank_side == 1:

            if "flex-column" in div['class']:
                div['class'].remove("flex-column")
            
            div['class'] = ["event_block", "d-flex", "flex-row"]

        user_number = 0


        for userdata in info:

            user_number += 1

            value_user = userdata[type_id]

            if check_image(userdata['profile_pic']):
                image = userdata['profile_pic']
            else:
                image = "icon.ico"

            new_block = bs(f'''
                <div class="card ms-2 text-center" style="width: {card_size}rem; background-color: {bg}{op} !important;">
                    <img src="{image}" class="rounded" width="{image_size}px" alt="...">
                    <div style="white-space: nowrap;overflow: hidden;text-overflow: ellipsis;">
                        <p style="font-size: {font_size} !important;color:{font_color} !important; text-align: center; margin:0px;">Posição {user_number}</p>
                        <p style="font-size: {font_size} !important;color:{font_color} !important; text-align: center; margin:0px;">{userdata['display_name']}</p>
                        <p style="font-size: {font_size} !important;color:{font_color} !important; text-align: center; margin:0px;">{value_user}</p>
                    </div>
                </div>
            ''', 'html.parser')

            div.append(new_block)

    elif rank_type == "list":

        user_number = 0

        for userdata in info:

            user_number += 1

            value_user = userdata[type_id]

            if check_image(userdata['profile_pic']):
                image = userdata['profile_pic']
            else:
                image = "icon.ico"


            new_block = bs(f'''
                <div class="row user" style="background-color: {bg}{op};">
                    <div class="d-flex col-auto">
                        <img src="{image}" class="rounded-circle" alt="" width="{image_size}px">
                    </div>            
                    <div class="d-flex col flex-column">
                        <div class="infos">
                            <p style="font-size: {font_size} !important; color: {font_color} !important; margin:0px;">Posição {user_number}</p>
                            <p style="font-size: {font_size} !important; color: {font_color} !important; margin:0px;">{userdata['display_name']}</p>
                            <p style="font-size: {font_size} !important; color: {font_color} !important; margin:0px;">{value_user} </p>
                        </div>
                    </div>
                </div>
            ''', 'html.parser')

            div.append(new_block)


    return str(soup)


def update_alert(data):

    alert_config_data = manipulate_json(f"{local_work('appdata_path')}/config/alerts.json", "load")

    message = data['message']
    img = data['img']
    duration = data['duration']

    font_alerts  = alert_config_data["font_alerts"]
    color_alerts  = alert_config_data["color_alerts"]
    background_alerts  = alert_config_data["background_alerts"]
    opacity_alerts  = alert_config_data["opacity_alerts"]
    delay_alerts  = alert_config_data["delay_alerts"]
    image_size = alert_config_data["image_size"]

    font_alertsvideo  = alert_config_data["font_alertsvideo"]
    color_alertsvideo = alert_config_data["color_alertsvideo"]
    background_alertsvideo = alert_config_data["background_alertsvideo"]
    opacity_alertsvideo = alert_config_data["opacity_alertsvideo"]
    image_sizevideo = alert_config_data["image_sizevideo"]

    opacity_alerts_cv = convert_opacity_to_hex(float(opacity_alerts)) 
    opacity_alertsvideo_cv = convert_opacity_to_hex(float(opacity_alertsvideo)) 

    try:

        if img.endswith('.mp4') or img.endswith('.gif'):

            html_file_video = f"{local_work('appdata_path')}/html/alertsvideo/alertsvideo.html"

            with open(html_file_video, "r") as html:

                soup = bs(html, 'html.parser')

                event_block = soup.find("div", {"class": f"event_block"})
                event_block['style'] = f'background-color: {background_alertsvideo}{opacity_alertsvideo_cv}; animation-duration: {duration}s'

                video_tag = soup.find("iframe")
                video_tag['src'] = f'{img}?controls=0'
                video_tag['width'] = image_sizevideo
                video_tag['height'] = image_sizevideo

                messsage_tag = soup.find("span", {"class": "message"})

                if message == "" or message == None:
                    messsage_tag['style'] = f"display: none;"
                else:
                    messsage_tag.string = message
                    messsage_tag['style'] = f"font-size:{font_alertsvideo}px ; color: {color_alertsvideo}"

                return str(soup)
        

        else:

            html_file = f"{local_work('appdata_path')}/html/alerts/alerts.html"

            with open(html_file, "r") as html:

                soup = bs(html, 'html.parser')

                main_div = soup.find("div", {"class": f"enter"})
                main_div['style'] = f'animation-duration: {delay_alerts}s'

                event_block = soup.find("div", {"class": f"event_block"})
                event_block['style'] = f'background-color: {background_alerts}{opacity_alerts_cv};'

                img_tag = soup.find("img", {"class": "img"})
                img_tag['src'] = img
                img_tag['width'] = image_size

                messsage_tag = soup.find("span", {"class": "message"})
                messsage_tag.string = message
                messsage_tag['style'] = f"font-size:{font_alerts}px ;color: {color_alerts}"

                return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_notif(data):

    try:
            
        event_log_config_data = manipulate_json(f"{local_work('appdata_path')}/events/event_log_config.json","load")

        duration = int(event_log_config_data['event-delay'])

        message = data['message']

        html_file = f"{local_work('appdata_path')}/html/events/events.html"

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"class": f"enter"})
        main_div['style'] = f"animation-duration: {duration}s;"

        event_block = soup.find("div", {"class": f"event_block"})
        event_block['style'] = f"background-color: {event_log_config_data['background-color']};color:{event_log_config_data['text-color']}"

        messsage_tag = soup.find("span", {"class": "message"})
        messsage_tag['style'] = f"font-size:{event_log_config_data['font-events-overlay']}px;color:{event_log_config_data['text-color']}"

        if message != None:
            messsage_tag.string = message

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_music(data):

    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/config/notfic.json", "load")
    
    duration = notifc_config_Data['HTML_MUSIC_TIME']

    user = data['redeem_user']
    artist = data['artist']
    music = data['music']

    html_file = f"{local_work('appdata_path')}/html/music/music.html"

    try:

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        album_src = f"../../player/images/album.png?noCache={randint(0, 100000)}"

        main_div = soup.find("div", {"class": f"player"})
        main_div['style'] = f'animation-duration: {duration}s'

        music_name_tag = soup.find("span", {"class": "music_name"})
        artist_name_tag = soup.find("span", {"class": "artist_name"})
        user_name_tag = soup.find("span", {"class": "user_name"})

        music_name_tag.string = music
        artist_name_tag.string = artist
        user_name_tag.string = user

        artwork_tag = soup.find("div", {'class':'artwork'})

        if artwork_tag:

            artwork_tag['style'] = f"background: url(https://i.imgur.com/3idGgyU.png), url({album_src}) center no-repeat;"

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_goal(data):

    goal_data = manipulate_json(f"{local_work('appdata_path')}/config/goal.json", "load")

    try:

        if data['type_id'] == 'get_html':

            from database import GoalManager
            
            type_goal = data['type_goal']

            goal_manager = GoalManager()
            goal_data = goal_manager.get_goal(type_goal)


            data = {
                'title_text_value' : goal_data['goal_text'],
                'goal_above' : goal_data['goal_above'],
                'goal_type' : goal_data['goal_type'],
                'title_text' : goal_data['title_text'],
                'goal_style' : goal_data['goal_style'],
                'text_size' : goal_data['text_size'],
                'progress_bar' : goal_data['progress_bar'],
                'background_border' : goal_data['background_border'],
                'background_color' : goal_data['background_color'],
                'progress_bar_background' : goal_data['progress_bar_background'],
                'progress_bar_background_opacity' : goal_data['progress_bar_background_opacity'],
            }

            return data
        
        elif data['type_id'] == 'save_html':


            from database import GoalManager
            
            goal_manager = GoalManager()

            type_goal = data['type_goal']

            goal_style = data['goal_style']
            goal_text_type = data['goal_type']
            goal_text_value = data['text_value']
            font_size = data['text_size']
            goal_above = data['goal_above']
            background_opacity = data['background_bar_color_opacity']
            background_color = data['background_color']
            background_border = data['background_border']

            background_opacity = convert_opacity_to_hex(float(background_opacity)) 

            goal_value = goal_data[type_goal]['goal']
            current_value = goal_data[type_goal]['current']

            if goal_value == 0 or goal_value == None:
                goal_value = 10

            path = normpath_simple(f"{local_work('appdata_path')}/html/goal/{type_goal}/goal{goal_style}.html")

            with open(path, "r") as html:
                soup = bs(html, 'html.parser')

            outer_bar = soup.find("div", {"class": "progress-outer"})
            title_text = soup.find("h3", {"class": "progress-title"})
            progress_bar = soup.find("div", {"class": "progress-bar"})
            progress_bar_bg = soup.find("div", {"class": "progress"})
            progress_bar_width = soup.find("div",{"id": "progress-bar"})


            if goal_text_type == 'percent':
                goal_value_inner = f"{(int(current_value)/int(goal_value))*100}%"
            elif goal_text_type == 'number':
                goal_value_inner = f"{int(current_value)}/{int(goal_value)}"

            progress_bar_width = (int(current_value)/int(goal_value))*100
            
            progress_bar['style'] = f"background-color: {data['bar_color']};width: {progress_bar_width}%;"

            progress_div_list = [1,2,4]
            if int(goal_style) in progress_div_list:

                percentage = round((int(current_value)/int(goal_value))*100, 1)
                progress_bar_value_div = soup.find("div",{"class": "progress-value"})
                progress_bar_value_div.string = f"{percentage}%"

            if goal_above == 1:
                title_text['style'] = f"display: block !important;color: {data['text_color']};font-size:{font_size}px;"
                title_text.string = f"{goal_text_value} : {goal_value_inner}"
            else :
                title_text['style'] = "display: none !important;"


            outer_bar['style'] = f"background-color: {background_color}{background_opacity};border-color: {background_border}{background_opacity} "
            progress_bar_bg['style'] = f"background-color: {data['background_bar_color']}"

            goal_manager.save_html(data,type_goal)

                
            return str(soup)
        
        elif data['type_id'] == 'update_goal':

            from database import GoalManager
            
            type_goal = data['type_goal']

            goal_manager = GoalManager()
            goal_data = goal_manager.get_goal(type_goal)

            data = {
                'goal' : goal_data['goal'],
                'current' : goal_data['current'],
                'text_value' : goal_data['goal_text'],
                'text_size' : goal_data['text_size'],
                'goal_style' : goal_data['goal_style'],
                'goal_above' : goal_data['goal_above'],
                'goal_type' : goal_data['goal_type'],
                'text_value' : goal_data['goal_text'],
                'text_size' : goal_data['text_size'],
                'text_color' : goal_data['title_text'],
                'bar_color' : goal_data['progress_bar'],
                'background_color' : goal_data['background_color'],
                'background_border' : goal_data['background_border'],
                'background_bar_color' : goal_data['progress_bar_background'],
                'progress_bar_background_opacity' : goal_data['progress_bar_background_opacity'],
            }

            goal_style = data['goal_style']

            path = normpath_simple(f"{local_work('appdata_path')}/html/goal/{type_goal}/goal{goal_style}.html")

            with open(path, "r") as html:
                soup = bs(html, 'html.parser')

            goal_text_value = data['text_value']

            goal_value = data['goal']
            current_value = data['current']

            if goal_value == 0 or goal_value == None:
                goal_value = 10

            goal_text_type = data['goal_type']
            goal_above = data['goal_above']
            font_size = data['text_size']

            background_opacity = convert_opacity_to_hex(float(data['progress_bar_background_opacity'])) 

            background_color = data['background_color']
            background_border = data['background_border']
            
            outer_bar = soup.find("div", {"class": "progress-outer"})
            title_text = soup.find("h3", {"class": "progress-title"})
            progress_bar = soup.find("div", {"class": "progress-bar"})
            progress_bar_bg = soup.find("div", {"class": "progress"})
            progress_bar_width = soup.find("div",{"id": "progress-bar"})

            
            if goal_text_type == 'percent':
                percentage = round((int(current_value)/int(goal_value))*100, 1)
                goal_value_inner = f"{percentage}%"
            elif goal_text_type == 'number':
                goal_value_inner = f"{int(current_value)}/{int(goal_value)}"


            progress_bar_width = (int(current_value)/int(goal_value))*100

            progress_bar['style'] = f"background-color: {data['bar_color']};width: {progress_bar_width}%;"

            progress_div_list = [1,2,4]

            if int(goal_style) in progress_div_list:
                percentage = round((int(current_value)/int(goal_value))*100, 1)
                progress_bar_value_div = soup.find("div",{"class": "progress-value"})
                progress_bar_value_div.string = f"{percentage}%"

            if goal_above == 1:
                title_text['style'] = f"display: block !important;color: {data['text_color']};font-size:{font_size}px;"
                title_text.string = f"{goal_text_value} : {goal_value_inner}"
            else :
                title_text['style'] = "display: none !important;"

            outer_bar['style'] = f"background-color: {background_color}{background_opacity};border-color: {background_border}{background_opacity} "

            progress_bar_bg['style'] = f"background-color: {data['background_bar_color']}"

            
            return str(soup)

    except Exception as e:

        error_log(e)

        return True


def create_votes_html(options_data,total_votes):

    style_data = manipulate_json(f"{local_work('appdata_path')}/voting/style.json", "load")

    style = style_data['style']


    def create_progress_bar(option_data, percentage):

        style_data = manipulate_json(f"{local_work('appdata_path')}/voting/style.json", "load")

        background_opacity = convert_opacity_to_hex(float(style_data['progress_bar_background_opacity'])) 
        style = style_data['style']

        percentage = round(percentage, 1)

        if style == "0":
            html = f"""
            <div class="progress-outer" style="background-color: {style_data['background_color']}{background_opacity}">
                <h3 class="progress-title" style="color: {style_data['text_color']}; font-size: {style_data['text_size']}px">{option_data['name']} : {option_data['votes']} Votos | {percentage}%</h3>
                <div class="progress" style="background-color: {style_data['progress_bar_background']}">
                    <div class="progress-bar progress-bar-striped" id="progress-bar" style="background-color: {style_data['progress_bar']}; width: {percentage}%">
                    </div>
                </div>
            </div>
            """

        elif style == "1":
            html = f"""
            <div class="progress-outer" style="background-color: {style_data['background_color']}{background_opacity}">
                <h3 class="progress-title" style="color: {style_data['text_color']}; font-size: {style_data['text_size']}px">{option_data['name']} : {option_data['votes']} Votos | {percentage}%</h3>
                <div class="progress-outer-bar">
                    <div class="progress" style="background-color: {style_data['progress_bar_background']}">
                        <div class="progress-bar progress-bar-striped progress-bar-info" id="progress-bar" style="background-color: {style_data['progress_bar']}; width: {percentage}%">
                            <div class="progress-value">{percentage}>%</div>
                        </div>
                    </div>
                </div>
            </div>
            """
        elif style == "2":
            html = f"""
            <div class="progress-outer" style="background-color: {style_data['background_color']}{background_opacity}">
                <h3 class="progress-title" style="color: {style_data['text_color']}; font-size: {style_data['text_size']}px">{option_data['name']} : {option_data['votes']} Votos | {percentage}%</h3>
                <div class="progress" style="background-color: {style_data['progress_bar_background']}">
                    <div class="progress-bar progress-bar-striped progress-bar-info active" id="progress-bar" style="background-color: {style_data['progress_bar']}; width: {option_data['votes']}%">
                        <div class="progress-value">{percentage}%</div>
                    </div>
                </div>
            </div>
            """
        elif style == "3":
            html = f"""
            <div class="progress-outer" style="background-color: {style_data['background_color']}{background_opacity}">
                <h3 class="progress-title" style="color: {style_data['text_color']}; font-size: {style_data['text_size']}px">{option_data['name']} : {option_data['votes']} Votos | {percentage}%</h3>
                <div class="progress" style="background-color: {style_data['progress_bar_background']}">
                    <div class="progress-bar progress-bar-info active" id="progress-bar" style="background-color: {style_data['progress_bar']}; width: {percentage}%">
                    </div>
                </div>
            </div>
            """
        elif style == "4":
            html = f"""
            <div class="progress-outer" style="background-color: {style_data['background_color']}{background_opacity}">
                <h3 class="progress-title" style="color: {style_data['text_color']}; font-size: {style_data['text_size']}px">{option_data['name']} : {option_data['votes']} Votos | {percentage}%</h3>
                <div class="progress" style="background-color: {style_data['progress_bar_background']}">
                    <div class="progress-bar" id="progress-bar" style="background-color: {style_data['progress_bar']}; width: {percentage}%">
                        <div class="progress-value">{percentage}%</div>
                    </div>
                </div>
            </div>
            """
        elif style == "5":
            html = f"""
            <div class="progress-outer" style="background-color: {style_data['background_color']}{background_opacity}">
                <h3 class="progress-title" style="color: {style_data['text_color']}; font-size: {style_data['text_size']}px">{option_data['name']} : {option_data['votes']} Votos | {percentage}%</h3>
                <div class="progress">
                    <div class="progress-bar" id="progress-bar" style="border-top-color: {style_data['progress_bar']}; width: {percentage}%">
                    </div>
                </div>
            </div>
            """

        return html

    def extract_style_tag(style):

        path = f"{local_work('appdata_path')}/html/voting/voting{style}.html"

        with open(path, "r") as html_file:
            soup = bs(html_file, 'html.parser')
            style_tag = soup.find('style')
        
        return style_tag


    final_html = """
    <html>
    <head>
        <meta charset="utf-8" />
        <meta content="IE=edge" http-equiv="X-UA-Compatible" />
        <meta content="width=device-width, initial-scale=1.0" name="viewport" />
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css?family=Kanit" rel="stylesheet" />
        <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js"></script>
        <title>Event</title>
    </head>
    """

    style_tag = extract_style_tag(style)
    final_html += f"\n    {style_tag}"

    final_html += """

    <body>
    """

    for option_name, option_data in options_data.items():

        votes = option_data['votes']
        percentage = (votes / total_votes) * 100
        html = create_progress_bar(option_data,percentage)
        final_html += f"\n    {html}"


    final_html += """
    </body>
    </html>
    """

    return final_html


def update_votes(data):

    config_data = manipulate_json(f"{local_work('appdata_path')}/voting/style.json", "load")

    try:

        if data['type_id'] == 'get_html':

            
            data = {
                'style' : config_data['style'],
                'text_size' : config_data['text_size'],
                'text_color' : config_data['text_color'],
                'progress_bar' : config_data['progress_bar'],
                'background_color' : config_data['background_color'],
                'background_border' : config_data['background_border'],
                'progress_bar_background' : config_data['progress_bar_background'],
                'progress_bar_background_opacity' : config_data['progress_bar_background_opacity'],
            }

            return data
        
        elif data['type_id'] == 'save_html':

            config_data['style'] = data['style']
            config_data['text_color'] = data['text_color']
            config_data['text_size'] = data['text_size']
            config_data['progress_bar'] = data['bar_color']
            config_data['progress_bar_background'] = data['background_bar_color']
            config_data['background_color'] = data['background_color']
            config_data['background_border'] = data['background_border']
            config_data['progress_bar_background_opacity'] = data['background_bar_color_opacity']

            manipulate_json(f"{local_work('appdata_path')}/voting/style.json", "save", config_data)

            options_data = manipulate_json(f"{local_work('appdata_path')}/voting/votesEx.json", "load")
            total_votes = len(options_data['voted'])

            html = create_votes_html(options_data['options'], total_votes)
                
            return html
        
        elif data['type_id'] == 'update_votes':

            data = {
                'style' : config_data['style'],
                'text_size' : config_data['text_size'],
                'text_color' : config_data['text_color'],
                'bar_color' : config_data['progress_bar'],
                'background_border' : config_data['background_border'],
                'background_bar_color' : config_data['progress_bar_background'],
                'background_color' : config_data['background_color'],
                'progress_bar_background_opacity' : config_data['progress_bar_background_opacity']
            }

            options_data = manipulate_json(f"{local_work('appdata_path')}/voting/votes.json", "load")
            total_votes = len(options_data['voted'])

            html = create_votes_html(options_data['options'], total_votes)

            return html

    except Exception as e:

        error_log(e)

        return True


def replace_all(text, dic_res):

    try:
        
        if isinstance(text, dict):

            error_log(f"{dic_res} - Dicionario com erro para replace.")
            return None
        
        else:

            if not text == None:
                for i, j in dic_res.items():
                    text = text.replace(str(i), str(j))
            return text

    except Exception as e:

        error_log(e)
        return text


def compare_and_insert_keys():

    source_directory = f"{local_work('datadir')}/web/src"
    destination_directory = f"{local_work('appdata_path')}"

    try:

        if not os.path.exists(destination_directory):

            shutil.copytree(source_directory, destination_directory)

        path_giveaway = f"{local_work('appdata_path')}/html/giveaway"
        path_follow = f"{local_work('appdata_path')}/html/goal/follow"
        path_highlighted = f"{local_work('appdata_path')}/html/goal/follow"
        path_ranks = f"{local_work('appdata_path')}/html/ranks"
        
        if os.path.exists(path_follow):

            shutil.rmtree(path_follow)
        
        if os.path.exists(path_giveaway):

            shutil.rmtree(path_giveaway)
        
        if os.path.exists(path_highlighted):

            shutil.rmtree(path_highlighted)

        if os.path.exists(path_ranks):

            shutil.rmtree(path_ranks)

        for root, dirs, files in os.walk(source_directory):
            
            relative_path = os.path.relpath(root, source_directory)
            destination_path = os.path.join(destination_directory, relative_path)

            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination_path, file)

                if not os.path.exists(destination_file):
                    shutil.copy2(source_file, destination_file)

        def update_dict_recursive(dest_dict, source_dict):
            
            for key, value in source_dict.items():
                if key in dest_dict:
                    if isinstance(value, dict) and isinstance(dest_dict[key], dict):
                        update_dict_recursive(dest_dict[key], value)
                else:
                    dest_dict[key] = value

        for root_directory, _, files in os.walk(source_directory):

            for file in files:

                if file.endswith('.json') and not file.endswith('gifts.json'):

                    source_file_path = os.path.join(root_directory, file)
                    destination_file_path = source_file_path.replace(source_directory, destination_directory)

                    try:

                        with open(source_file_path, 'r', encoding='utf-8') as src_file, open(destination_file_path, 'r+', encoding='utf-8') as dest_file:
                            
                            data1 = json.load(src_file)
                            data2 = json.load(dest_file)

                            if isinstance(data1, dict) and isinstance(data2, dict):

                                update_dict_recursive(data2, data1)
                                
                                dest_file.seek(0)

                                json.dump(data2, dest_file, indent=4, ensure_ascii=False)
                                dest_file.truncate()

                    except json.JSONDecodeError as e:
                        print(f"Error decoding the source JSON file: {source_file_path}")
                        print(e)

        
        queue_data = manipulate_json(f"{local_work('appdata_path')}/queue/queue.json", "load")

        if type(queue_data["priority"]) == list:

            queue_data["priority"] = {}
            queue_data["normal"] = {}

            manipulate_json(f"{local_work('appdata_path')}/queue/queue.json", "save", queue_data)
            
        gifts_data = manipulate_json(f"{local_work('appdata_path')}/gifts/gifts.json","load")

        if not "video" in gifts_data:

            gifts_data["video"] = ""
            gifts_data["video_status"] = 0
            gifts_data["video_time"] = 50

            manipulate_json(f"{local_work('appdata_path')}/gifts/gifts.json", "save", gifts_data)

        return True
    
    except Exception as e:

        error_message = f"Erro ao criar os arquivos internos {str(e)}."
        messagebox.showerror("Erro", error_message)

        return False


def normpath_simple(path):
    
    path_norm = os.path.normpath(path)
    
    path_norm_simple = path_norm.replace('\\', '/')
    
    return path_norm_simple


def check_file(file):

    try:

        with open(file, 'r', encoding='utf-8') as file_r:
            json.load(file_r)

        return True
    
    except Exception as e:

        return False


def get_version(type_id):

    try:

        if type_id == "online":

            response = req.get("https://api.github.com/repos/GGTEC/VibesBot/releases/latest")
            response_json = json.loads(response.text)

            if "tag_name" in response_json:
                version = response_json["tag_name"]
            else:
                version = "2.0.8"

            return version
        
        elif type_id == "code":

            return "2.0.8"
    
    except Exception as e:

        error_log(e)
        return "0.0.0"    