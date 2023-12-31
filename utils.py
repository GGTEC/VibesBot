import json
import os
import shutil
import sys
import time
import pytz
import importlib
import requests as req

from dotenv import load_dotenv
from random import randint
from bs4 import BeautifulSoup as bs
from datetime import datetime

if getattr(sys, 'frozen', False):
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash


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


def error_log(ex):

    now = datetime.now()
    time_error = now.strftime("%d/%m/%Y %H:%M:%S")

    trace = []
    error_type = "Unknown"
    error_message = ""

    if isinstance(ex, BaseException):  # Verifica se ex é uma exceção
        tb = ex.__traceback__

        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next

        error_type = type(ex).__name__
        error_message = str(ex)
    else:
        error_message = ex

    error = str(f'Erro = type: {error_type} | message: {error_message} | trace: {trace} | time: {time_error} \n\n')

    with open(f"{local_work('appdata_path')}/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)


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
        print(f'The file {custom_path} was not found.')

    except Exception as e:
        error_log(custom_path)
        error_log(e)


def send_message(data):

    try:

        status_commands_data = manipulate_json(f"{local_work('appdata_path')}/config/commands_config.json", "load")

        type_message = data['type']
        message = data['message']

        status_error_time = status_commands_data['STATUS_ERROR_TIME']
        status_error_user = status_commands_data['STATUS_ERROR_USER']
        status_tts = status_commands_data['STATUS_TTS']
        status_music = status_commands_data['STATUS_MUSIC']
        status_music_error = status_commands_data['STATUS_MUSIC_ERROR']
        status_music_confirm = status_commands_data['STATUS_MUSIC_CONFIRM']

        if type_message == 'CHAT':
            return True

        elif type_message == 'ERROR_TIME':

            if status_error_time == 1:
                return True

        elif type_message == 'ERROR_USER':

            if status_error_user == 1:
                return True

        elif type_message == 'STATUS_TTS':

            if status_tts == 1:
                return True

        elif type_message == 'STATUS_MUSIC':

            if status_music == 1:
                return True

        elif type_message == 'STATUS_MUSIC_CONFIRM':

            if status_music_confirm == 1:
                return True

        elif type_message == 'STATUS_MUSIC_ERROR':

            if status_music_error == 1:
                return True

    except Exception as e:
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


def calculate_time(started):

    try:

        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_date = datetime.fromisoformat(started).replace(tzinfo=pytz.utc)

        gmt_minus_3_now = utc_now.astimezone(pytz.timezone("Etc/GMT+3"))
        gmt_minus_3_date = utc_date.astimezone(pytz.timezone("Etc/GMT+3"))

        difference = gmt_minus_3_now - gmt_minus_3_date

        days = difference.days
        hours = difference.seconds//3600
        minutes = (difference.seconds//60) % 60
        sec = difference.seconds % 60

        time_in_live = {
            'days': str(days),
            'hours': str(hours),
            'minutes': str(minutes),
            'sec': str(sec)
        }

        return time_in_live

    except Exception as e:

        error_log(e)

        return 'none'


def check_delay(delay_command, last_use):

    with open(f"{local_work('appdata_path')}/messages/messages_file.json", "r", encoding='utf-8') as messages_file:
        messages_data = json.load(messages_file)

    message_error = messages_data['response_delay_error']

    last_command_time = last_use
    delay_compare = int(delay_command)

    current_time = int(time.time())

    if current_time >= last_command_time + delay_compare:

        message = 'OK'
        value = True

        return message, value, current_time

    else:

        remaining_time = last_command_time + delay_compare - current_time

        message = message_error.replace('{seconds}', str(remaining_time))
        value = False
        current_time = ''

        return message, value, current_time


def copy_file(source, dest):
    copy = 0

    try:

        shutil.copy2(source, dest)

    except Exception as e:

        error_log(e)
        copy = 1
        return copy

    copy = 1
    return copy


def check_image(image):

    try:
        respon = req.get(image, stream=True)

        if respon.status_code == 200:
            return True
        else:
            return False
        
    except req.exceptions.RequestException as e:

        return False


def update_ranks(data):

    ranks_config = manipulate_json(f"{local_work('appdata_path')}/config/rank.json", "load")

    type_id = data["type_id"]
    info = data["info"]

    if type_id == "likes":

        bg = ranks_config['likes_bg']
        op = ranks_config['likes_op']

        with open(f"{local_work('appdata_path')}/html/ranks/likes/likes.html", 'r', encoding='utf-8') as file:
            content_html = file.read()

            soup = bs(content_html, 'html.parser')

            div = soup.find("div", {"class": f"event_block"})

        for user, userdata in info:

            if check_image(userdata['profile_pic']):
                image = userdata['profile_pic']
            else:
                image = "icon.ico"

            new_block = bs(f'''
                <div class="row user" style="background-color: {bg};opacity: {op};">
                    <div class="d-flex col-auto">
                        <img src="{image}" class="rounded-circle" alt="" width="50px">
                    </div>            
                    <div class="d-flex col flex-column">
                        <div class="infos">
                            <p class="username">{userdata['display_name']}</p>
                            <p class="value">{userdata['likes']} Curtidas</p>
                        </div>
                    </div>
                </div>
            ''', 'html.parser')

            div.append(new_block)

        return str(soup)
        
    elif type_id == "shares":

        bg = ranks_config['shares_bg']
        op = ranks_config['shares_op']

        with open(f"{local_work('appdata_path')}/html/ranks/shares/shares.html", 'r', encoding='utf-8') as file:
            content_html = file.read()

            soup = bs(content_html, 'html.parser')

            div = soup.find("div", {"class": f"event_block"})

        for user, userdata in info:

            if check_image(userdata['profile_pic']):
                image = userdata['profile_pic']
            else:
                image = "icon.ico"

            new_block = bs(f'''
                <div class="row user" style="background-color: {bg};opacity: {op};">
                    <div class="d-flex col-auto">
                        <img src="{image}" class="rounded-circle" alt="" width="50px">
                    </div>            
                    <div class="d-flex col flex-column">
                        <div class="infos">
                            <p class="username">{userdata['display_name']}</p>
                            <p class="value">{userdata['shares']} Compartilhamentos</p>
                        </div>
                    </div>
                </div>
            ''', 'html.parser')

            div.append(new_block)

        return str(soup)
        
    elif type_id == "gifts":

        bg = ranks_config['gifts_bg']
        op = ranks_config['gifts_op']

        with open(f"{local_work('appdata_path')}/html/ranks/gifts/gifts.html", 'r', encoding='utf-8') as file:
            content_html = file.read()

            soup = bs(content_html, 'html.parser')

            div = soup.find("div", {"class": f"event_block"})

        for user, userdata in info:

            if check_image(userdata['profile_pic']):
                image = userdata['profile_pic']
            else:
                image = "icon.ico"

            new_block = bs(f'''
                <div class="row user" style="background-color: {bg};opacity: {op};">
                    <div class="d-flex col-auto">
                        <img src="{image}" class="rounded-circle" alt="" width="50px">
                    </div>               
                    <div class="d-flex col flex-column">
                        <div class="infos">
                            <p class="username">{userdata['display_name']}</p>
                            <p class="value">{userdata['gifts']} Presentes</p>
                        </div>
                    </div>
                </div>
            ''', 'html.parser')

            div.append(new_block)

        return str(soup)
        
    elif type_id == "points":

        bg = ranks_config['points_bg']
        op = ranks_config['points_op']

        with open(f"{local_work('appdata_path')}/html/ranks/points/points.html", 'r', encoding='utf-8') as file:
            content_html = file.read()

            soup = bs(content_html, 'html.parser')

            div = soup.find("div", {"class": f"event_block"})

        for user, userdata in info:

            if check_image(userdata['profile_pic']):
                image = userdata['profile_pic']
            else:
                image = "icon.ico"

            new_block = bs(f'''
                <div class="row user" style="background-color: {bg};opacity: {op};">
                    <div class="d-flex col-auto">
                        <img src="{image}" class="rounded-circle" alt="" width="50px">
                    </div>            
                    <div class="d-flex col flex-column">
                        <div class="infos">
                            <p class="username">{userdata['display_name']}</p>
                            <p class="value">{userdata['points']} Pontos</p>
                        </div>
                    </div>
                </div>
            ''', 'html.parser')

            div.append(new_block)

        return str(soup)


def update_alert(data):

    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/config/notfic.json", "load")
    alert_config_data = manipulate_json(f"{local_work('appdata_path')}/config/alerts.json", "load")

    duration = notifc_config_Data['HTML_ALERT_TIME']

    message = data['message']
    img = data['img']
    
    image_size = alert_config_data['image_size']
    font_size = alert_config_data['font_size']
    background_color = alert_config_data['background_color']

    html_file = f"{local_work('appdata_path')}/html/alerts/alerts.html"

    try:

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"class": f"enter"})
        main_div['style'] = f'animation-duration: {duration}s'

        event_block = soup.find("div", {"class": f"event_block"})
        event_block['style'] = f'background-color: {background_color}'

        img_tag = soup.find("img", {"class": "img"})
        img_tag['src'] = img
        img_tag['width'] = image_size

        messsage_tag = soup.find("span", {"class": "message"})
        messsage_tag.string = message
        messsage_tag['style'] = f"font-size:{font_size};"

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_notif(data):

    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/config/notfic.json", "load")

    duration = notifc_config_Data['HTML_REDEEM_TIME']

    message = data['message']

    html_file = f"{local_work('appdata_path')}/html/events/events.html"

    try:

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        main_div = soup.find("div", {"class": f"enter"})
        main_div['style'] = f"animation-duration: {duration}s;"

        messsage_tag = soup.find("span", {"class": "message"})

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

            type_goal = data['type_goal']

            data = {
                'title_text_value' : goal_data[type_goal]['goal_text'],
                'outer_bar' : goal_data[type_goal]['outer_bar'],
                'title_text' : goal_data[type_goal]['title_text'],
                'progress_bar' : goal_data[type_goal]['progress_bar'],
                'progress_bar_background' : goal_data[type_goal]['progress_bar_background'],
            }

            return data
        
        elif data['type_id'] == 'save_html':

            type_goal = data['type_goal']

            path = normpath_simple(f"{local_work('appdata_path')}/html/goal/{type_goal}/goal.html")
            
            with open(path, "r") as html:
                soup = bs(html, 'html.parser')

            outer_bar = soup.find("div", {"class": "progress-outer"})
            title_text = soup.find("h3", {"class": "progress-title"})
            goal_text = soup.find("span", {"id": "progress-title"})
            progress_bar = soup.find("div", {"class": "progress-bar"})
            progress_bar_bg = soup.find("div", {"class": "progress"})

            goal_text.string = data['text_value']
            outer_bar['style'] = f"background-color: {data['outer_color']}"
            title_text['style'] = f"color: {data['text_color']}"
            progress_bar['style'] = f"background-color: {data['bar_color']}"
            progress_bar_bg['style'] = f"background-color: {data['background_bar_color']}"

            goal_data[type_goal]['goal_text'] = data['text_value']
            goal_data[type_goal]['outer_bar'] = data['outer_color']
            goal_data[type_goal]['title_text'] = data['text_color']
            goal_data[type_goal]['progress_bar'] = data['bar_color']
            goal_data[type_goal]['progress_bar_background'] = data['background_bar_color']

            manipulate_json(f"{local_work('appdata_path')}/config/goal.json", "save", goal_data)

            with open(path, "w", encoding="utf-8") as html_w:
                html_w.write(str(soup))
                
            return str(soup)
        
        elif data['type_id'] == 'update_goal':

            type_goal = data['type_goal']

            path = normpath_simple(f"{local_work('appdata_path')}/html/goal/{type_goal}/goal.html")
            
            with open(path, "r") as html:
                soup = bs(html, 'html.parser')


            data = {
                'text_value' : goal_data[type_goal]['goal_text'],
                'outer_color' : goal_data[type_goal]['outer_bar'],
                'text_color' : goal_data[type_goal]['title_text'],
                'bar_color' : goal_data[type_goal]['progress_bar'],
                'background_bar_color' : goal_data[type_goal]['progress_bar_background'],
            }

            
            outer_bar = soup.find("div", {"class": "progress-outer"})
            title_text = soup.find("h3", {"class": "progress-title"})
            goal_text = soup.find("span", {"id": "progress-title"})
            progress_bar = soup.find("div", {"class": "progress-bar"})
            progress_bar_bg = soup.find("div", {"class": "progress"})

            goal_text.string = data['text_value']
            outer_bar['style'] = f"background-color: {data['outer_color']}"
            title_text['style'] = f"color: {data['text_color']}"
            progress_bar['style'] = f"background-color: {data['bar_color']}"
            progress_bar_bg['style'] = f"background-color: {data['background_bar_color']}"


            with open(path, "r") as html:
                soup = bs(html, 'html.parser')
            
            return str(soup)

    except Exception as e:

        error_log(e)

        return True


def replace_all(text, dic_res):

    try:
        for i, j in dic_res.items():
            text = text.replace(str(i), str(j))

        return text

    except Exception as e:
        error_log(e)

        return ''


def messages_file_load(key):

    with open(f"{local_work('appdata_path')}/messages/messages_file.json", "r", encoding='utf-8') as messages_file:
        messages_data = json.load(messages_file)

    message = messages_data[key]

    return message


def compare_and_insert_keys():
    
    source_directory = f"{local_work('datadir')}/web/src"
    destination_directory = f"{local_work('appdata_path')}"

    if not os.path.exists(destination_directory):

        shutil.copytree(source_directory, destination_directory)

    def update_dict_recursive(dest_dict, source_dict):
        for key, value in source_dict.items():
            if key in dest_dict:
                if isinstance(value, dict) and isinstance(dest_dict[key], dict):
                    update_dict_recursive(dest_dict[key], value)
            else:
                dest_dict[key] = value
                error_log(f"Chave '{key}' atualizada: {value}")

    for root_directory, _, files in os.walk(source_directory):
        
        for file in files:

            if file.endswith('.json') and not file.endswith('gifts.json'):

                source_file_path = os.path.join(root_directory, file)
                destination_file_path = source_file_path.replace(source_directory, destination_directory)

                if not os.path.exists(destination_file_path):
                    error_log(f"File missing in the destination directory: {destination_file_path}")
                    shutil.copy2(source_file_path, destination_file_path)

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
                    error_log(f"Error decoding the source JSON file: {source_file_path}")


    for root_directory, dirs, files in os.walk(destination_directory):

        for d in dirs:

            destination_path = os.path.join(root_directory, d)
            source_path = destination_path.replace(destination_directory, source_directory)

            if not os.path.exists(source_path):
                if os.path.isdir(destination_path):
                    error_log(f"File or directory in the destination directory that is not in the source directory: {destination_path}")
                    shutil.rmtree(destination_path)

        for file in files:

            destination_path = os.path.join(root_directory, file)
            source_path = destination_path.replace(destination_directory, source_directory)

            if not os.path.exists(source_path):
                if os.path.isfile(destination_path):
                    error_log(f"File in the destination directory that is not in the source directory: {destination_path}")
                    os.remove(destination_path)


    return True


def normpath_simple(path):
    
    path_norm = os.path.normpath(path)
    
    path_norm_simple = path_norm.replace('\\', '/')
    
    return path_norm_simple


def update_dict_gifts(dict_b):

    dict_a_load = manipulate_json(f"{local_work('appdata_path')}/config/gifts.json","load")
    dict_a = dict_a_load["gifts"]


    if not dict_a:
        dict_a.update(dict_b)
    else:
        for id_, item_a in dict_a.items():

            if id_ in dict_b:
                item_b = dict_b[id_]

                if item_a['name'] != item_b['name']:
                    print(f"Atualizado 'name' para {id_}")
                    dict_a[id_]['name'] = item_b['name']

                if item_a['value'] != item_b['value']:
                    print(f"Atualizado 'value' para {id_}")
                    dict_a[id_]['value'] = item_b['value']
                
                if item_a['icon'] != item_b['icon']:
                    print(f"Atualizado 'value' para {id_}")
                    dict_a[id_]['icon'] = item_b['icon']

            else:
                print(f"Removendo item para {id_}")
                del dict_a[id_]

    manipulate_json(f"{local_work('appdata_path')}/config/gifts.json","save",dict_a_load)


def check_file(file):

    try:

        with open(file, 'r', encoding='utf-8') as file_r:
            json.load(file_r)

        return True
    
    except Exception as e:
        return False