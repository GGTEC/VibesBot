import json
import os
import shutil
import sys
import time
from datetime import datetime
import pytz
from random import randint
from bs4 import BeautifulSoup as bs
import urllib.request
import zipfile
import tempfile
import importlib
from dotenv import load_dotenv

extDataDir = os.getcwd()

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
        extDataDir = sys._MEIPASS


def local_work(type_id):

    if type_id == 'datadir':

        extDataDir = os.getcwd()

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            if getattr(sys, 'frozen', False):
                if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
                    import pyi_splash
                extDataDir = sys._MEIPASS

        return extDataDir
    
    elif type_id == 'appdata_path':

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

    with open(f"{local_work('appdata_path')}/VibesBot/web/src/error_log.txt", "a+", encoding='utf-8') as log_file_r:
        log_file_r.write(error)


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

        error_log(e)


def send_message(type_message):

    try:
        with open(f"{local_work('appdata_path')}/rewardevents/web/src/config/commands_config.json") as status_commands_check:
            status_commands_data = json.load(status_commands_check)

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

    with open(f"{local_work('appdata_path')}/VibesBot/web/src/messages/messages_file.json", "r", encoding='utf-8') as messages_file:
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


def update_notif(data):

    with open(f"{local_work('appdata_path')}/VibesBot/web/src/config/notfic.json", 'r', encoding='utf-8') as notifc_config_file:
        notifc_config_Data = json.load(notifc_config_file)

    duration = notifc_config_Data['HTML_REDEEM_TIME']

    redeem = data['redeem_name']
    user = data['redeem_user']
    image = data['redeem_image']

    html_file = f"{local_work('appdata_path')}/VibesBot/web/src/html/redeem/redeem.html"

    try:

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        redeem_src = image

        main_div = soup.find("div", {"id": f"main-block"})
        main_div['style'] = f'animation-duration: {duration}s'

        image_redeem = soup.find("img", {"class": "img-responsive"})
        redeem_name_tag = soup.find("span", {"class": "redem_name"})
        redeem_user_tag = soup.find("span", {"class": "redem_user"})

        image_redeem['src'] = redeem_src
        redeem_name_tag.string = redeem
        redeem_user_tag.string = user

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_music(data):


    notifc_config_Data = manipulate_json(f"{local_work('appdata_path')}/VibesBot/web/src/config/notfic.json", "load")
    
    duration = notifc_config_Data['HTML_MUSIC_TIME']

    user = data['redeem_user']
    artist = data['artist']
    music = data['music']

    html_file = f"{local_work('appdata_path')}/VibesBot/web/src/html/music/music.html"

    try:

        with open(html_file, "r") as html:
            soup = bs(html, 'html.parser')

        album_src = f"../../player/images/album.png?noCache={randint(0, 100000)}"

        main_div = soup.find("div", {"id": f"main-block"})
        main_div['style'] = f'animation-duration: {duration}s'

        image_redeem = soup.find("img", {"class": "img-responsive"})
        music_name_tag = soup.find("span", {"class": "music_name"})
        artist_name_tag = soup.find("span", {"class": "artist_name"})
        redeem_user_music_tag = soup.find("span", {"class": "redem_user_music"})

        image_redeem['src'] = album_src
        music_name_tag.string = music
        artist_name_tag.string = artist
        redeem_user_music_tag.string = user

        return str(soup)

    except Exception as e:

        error_log(e)
        return True


def update_goal(data):

    goal_data = manipulate_json(f"{local_work('appdata_path')}/VibesBot/web/src/config/goal.json", "load")

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

            path = normpath_simple(f"{local_work('appdata_path')}/VibesBot/web/src/html/goal/{type_goal}/goal.html")
            
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

            manipulate_json(f"{local_work('appdata_path')}/VibesBot/web/src/config/goal.json", "save", goal_data)

            with open(path, "w", encoding="utf-8") as html_w:
                html_w.write(str(soup))
                
            return str(soup)
        
        elif data['type_id'] == 'update_goal':

            type_goal = data['type_goal']

            path = normpath_simple(f"{local_work('appdata_path')}/VibesBot/web/src/html/goal/{type_goal}/goal.html")

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

    with open(f"{local_work('appdata_path')}/VibesBot/web/src/messages/messages_file.json", "r", encoding='utf-8') as messages_file:
        messages_data = json.load(messages_file)

    message = messages_data[key]

    return message


def compare_and_insert_keys():
    
    source_directory = f"{local_work('datadir')}/web/src"
    destination_directory = f"{local_work('appdata_path')}/VibesBot/web/src"

    if not os.path.exists(destination_directory):

        shutil.copytree(source_directory, destination_directory)


    for root_directory, _, files in os.walk(source_directory):
        
        for file in files:
            
            if file.endswith('.json') and file:
                
                source_file_path = os.path.join(root_directory, file)
                destination_file_path = source_file_path.replace(source_directory, destination_directory)

                if not os.path.exists(destination_file_path):
                    print(f"File missing in the destination directory: {destination_file_path}")
                    shutil.copy2(source_file_path, destination_file_path)

                try:
                    
                    with open(source_file_path, 'r', encoding='utf-8') as src_file, open(destination_file_path, 'r+', encoding='utf-8') as dest_file:
                        data1 = json.load(src_file)
                        dest_file.seek(0)
                        
                        try:
                            data2 = json.load(dest_file)

                            if isinstance(data1, list) and isinstance(data2, list):
                                updated_content = data1 + [item for item in data2 if item not in data1]

                                if updated_content != data2:
                                    
                                    dest_file.seek(0)
                                    
                                    json.dump(updated_content, dest_file, indent=4, ensure_ascii=False)
                                    
                                    dest_file.truncate()
                                    
                                    print(f"Content updated in the file {destination_file_path}")

                            elif isinstance(data1, dict) and isinstance(data2, dict):
                                
                                keys1 = set(data1.keys())
                                keys2 = set(data2.keys())
                                
                                missing_keys = keys1 - keys2

                                if missing_keys:
                                    
                                    print(f"Keys missing in the file {destination_file_path}:")
                                    
                                    for key in missing_keys:
                                        print(key)
                                        
                                    content = data2
                                    altered = False

                                    for key in missing_keys:
                                        
                                        if key not in content or content[key] != data1[key]:
                                            content[key] = data1[key]
                                            altered = True

                                    if altered:
                                        
                                        dest_file.seek(0)
                                        json.dump(content, dest_file, indent=4, ensure_ascii=False)
                                        dest_file.truncate()
                                        print(f"Content updated in the file {destination_file_path}")

                            else:
                                
                                print(f"Error: File {source_file_path} or {destination_file_path} contains an incompatible format.")

                        except json.JSONDecodeError as e:
                            
                            print(f"Error decoding the destination JSON file: {destination_file_path}")
                            print(e)
                            
                            # If a read error occurs, copy the source file to the destination file
                            
                            shutil.copy2(source_file_path, destination_file_path)
                            print(f"Destination file copied to resolve the issue: {destination_file_path}")
                            
                except json.JSONDecodeError as e:
                    print(f"Error decoding the source JSON file: {source_file_path}")
                    print(e)

    return True

def normpath_simple(path):
    
    path_norm = os.path.normpath(path)
    
    path_norm_simple = path_norm.replace('\\', '/')
    
    return path_norm_simple
