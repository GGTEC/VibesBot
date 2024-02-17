//CONFIG

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function toggle_div(type_id, div_id){
    
    if (type_id == 'show'){

        if (div_id == "config-chat-messages-div") {

            messages_config_js('get');

        } else if (div_id == "config-discord-div") {

            discord_js('event','get-profile');

        } else if (div_id == "config-music-div"){

            sr_config_js('event','get')

        } else if (div_id == "config-chat-div"){

            chat_config('get')

        } else if (div_id == "config-points-div"){

            points_config('get')
            ttk_gift('get_points')

        } else if (div_id == "config-events-div"){

            event_log_config('get')

        } else if (div_id == "userdata-div"){

            userdata_js('get')

        } else if (div_id == "config-roles-div"){
            roles_config('get')
        } else if (div_id == "config-alerts-div"){
            ttk_alerts('get_overlay')
        }

        document.getElementById("config-div").hidden = true;
        document.getElementById(div_id).hidden = false;

    } else if (type_id == 'hide'){

        if (div_id == "userdata-div"){ 
            userdata_js('destroy','')
        }
        
        document.getElementById("config-div").hidden = false;
        document.getElementById(div_id).hidden = true;

    }
}

function toggle_div_int(toShow,ToHide){

    if (toShow == 'global-gifts-div'){
        ttk_gift('get_global')
    } else if (toShow == 'individual-gifts-div'){
        ttk_gift('get_table')
    } else if (toShow == "config-queue-div"){
        queue_js('get_config','null')
    } else if (toShow == "commom-queue"){
        queue_js('get_queue','null')
    } else if (toShow == "command-tts-div"){
        tts_command('get_command')
    } else if (toShow == "config-tts-div"){
        tts_command('get_config')
    } else if (toShow == 'giveaway-config'){
        giveaway_js('get_config')
    } else if (toShow == 'giveaway-style'){
        giveaway_js('get_style')
    } else if (toShow == "subathon-config-div"){

        subathon_js('get')

    } else if (toShow == "subathon-style-div"){

        subathon_js('get_style')

    } else if (toShow == "highlighted-painel"|| toShow == "highlighted-style"){

        highlighted('get')

    }

    document.getElementById(ToHide).hidden = true;
    document.getElementById(toShow).hidden = false;

}

async function config_responses_js(type_id) {

    var select_message = document.getElementById('response-select-edit').value;
    var response_input = document.getElementById('response-message-new');
    var status = document.getElementById('response-status');
    var status_s = document.getElementById('response-status-s');
    var aliases_responses = document.getElementById('aliases-responses');
    var edit_div = document.getElementById('response-edit-div');

    if (type_id == 'get_response'){

        data = {
            type_id: type_id,
            key:select_message
        }

        var message = await window.pywebview.api.responses_config(type_id, data);
    
        if (message) {

            response_input.value = message.response;

            status.checked = message.status == 1 ? true : false
            status_s.checked = message.status_s == 1 ? true : false

            edit_div.hidden = false
    
        }

        const responses_aliases_respo = {

            "Likes_role_name": "",
            "balance": "{username}, {nickname}, {points}, {likes}, {gifts}, {shares}, {rank}",
            "balance_moderator": "{username}, {nickname}, {usercheck}, {points}, {likes}, {gifts}, {shares}, {rank}",
            "balance_top_error_response": "{username}, {nickname}",
            "balance_top_gifts": "{username}, {nickname} , {top-1}, {top-2}, {top-3}... ",
            "balance_top_likes": "{username}, {nickname} , {top-1}, {top-2}, {top-3}... ",
            "balance_top_points": "{username}, {nickname} , {top-1}, {top-2}, {top-3}... ",
            "balance_top_share": "{username}, {nickname} , {top-1}, {top-2}, {top-3}... ",
            "balance_user_gived": "{username}, {nickname}",
            "balance_user_insuficient": "{username}, {nickname}",
            "balance_user_not_found": "{username}, {nickname}",
            "balance_user_spended": "{username}, {nickname}",
            "command_cost": "{username}, {nickname}, {cost}",
            "command_current_confirm": "{username}, {nickname}, {music}",
            "command_disabled": "{username}, {nickname}",
            "command_next_confirm": "{username}, {nickname}, {music}, {request_by}",
            "command_next_no_music": "{username}, {nickname}",
            "command_root_sufix": "",
            "command_root_sufix_number": "",
            "command_skip_confirm": "{username}, {nickname}",
            "command_skip_inlist": "{username}, {nickname}",
            "command_skip_noplaying": "{username}, {nickname}",
            "command_sr_error_link": "{username}, {nickname}",
            "command_string": "{username}, {nickname}",
            "command_sufix": "{username}, {nickname}",
            "command_value": "{username}, {nickname}",
            "command_volume_confirm": "{username}, {nickname}, {volume}",
            "command_volume_error": "{username}, {nickname}",
            "command_volume_number": "{username}, {nickname}",
            "command_volume_response": "{username}, {nickname}, {volume}",
            "command_vote_arvoted": "",
            "command_vote_ended": "{votes}, {winner}, {name]",
            "command_vote_norun": "",
            "command_vote_notfound": "",
            "command_vote_started": "",
            "command_vote_voted": "",
            "commands_disabled": "",
            "error_tts_disabled": "{username}, {nickname},",
            "error_tts_no_text": "{username}, {nickname}",
            "error_tts_no_text_command": "",
            "error_user_level": "{username}, {nickname}, {user_level}, {command}",
            "event_command": "",
            "event_ttk_connect": "",
            "event_ttk_disconected": "",
            "event_ttk_envelope": "{username}, {nickname}, {coins}",
            "event_ttk_follow": "{username}, {nickname}",
            "event_ttk_gift": "{username}, {nickname}, {amount}, {giftname}, {diamonds}",
            "event_ttk_join": "{username}, {nickname}",
            "event_ttk_like": "{username}, {nickname}, {likes}",
            "event_ttk_reconected": "",
            "event_ttk_share": "{username}, {nickname}",
            "follow_role_name": "",
            "gifts_role_name": "",
            "giveaway_clear": "",
            "giveaway_response_mult_add": "{username}, {nickname}",
            "giveaway_response_perm": "{perm}",
            "giveaway_response_user_add": "{username}, {nickname}",
            "giveaway_response_win": "{username}, {nickname}",
            "giveaway_status_disable": "{giveaway_name}",
            "giveaway_status_disabled": "",
            "giveaway_status_enable": "{giveaway_name}",
            "goal_end": "{current}, {target}, {type}",
            "goal_progress": "{current}, {target}, {type}",
            "goal_start": "{current}, {target}, {type}",
            "moderator_role_name": "",
            "music_add_error": "{username}, {nickname}",
            "music_added_to_queue": "{username}, {nickname}, {music}",
            "music_blacklist": "{music}",
            "music_disabled": "{username}, {nickname}",
            "music_error_name": "",
            "music_leght_error": "{max_duration}",
            "music_length_error": "",
            "music_link_error": "",
            "music_link_youtube": "",
            "music_playing": "{music_name}, {music_artist}, {username}, {nickname}",
            "music_process_cache_error": "",
            "music_process_error": "",
            "music_stream_error": "",
            "response_add_champ": "",
            "response_add_queue": "{username}, {nickname}, {value}, {match}, {players}",
            "response_add_winner": "",
            "response_check_error_giveaway": "{username}, {nickname}",
            "response_clear_queue": "",
            "response_clear_queue_pri": "",
            "response_delay_error": "{seconds}",
            "response_end_champ": "",
            "response_get_queue": "{username}, {nickname}, {match}, {players}",
            "response_giveaway_disabled": "",
            "response_giveaway_nonames": "",
            "response_in_champ": "",
            "response_namein_playing": "",
            "response_namein_queue": "{username}, {nickname}, {value}, {match}, {players}",
            "response_no_user_giveaway": "{username}, {nickname}",
            "response_noname_queue": "{username}, {nickname}, {value}",
            "response_not_in_champ": "",
            "response_queue": "{username}, {nickname}, {match}, {players}",
            "response_queue_end_match": "",
            "response_queue_move": "{username}, {nickname},{user}, {match_actual}, {match_move_to}, {queue_type}",
            "response_queue_playing": "{username}, {nickname}, {queue_type}, {players}",
            "response_rem_queue": "{username}, {nickname}, {value}",
            "response_remove_champ": "",
            "response_user_error_giveaway": "{username}, {nickname}",
            "response_user_giveaway": "{username}, {nickname}",
            "shares_role_name": "",
            "skip_votes": "{username}, {nickname}, {votes}, {minimum}",
            "subathon_minutes_add": "",
            "subathon_minutes_remove": "",
            "subathon_minutes_reset": "",
            "subscriber_custom_role_name": "",
            "subscriber_role_name": "",
            "tts_prefix": "",
            "user_in_blacklist": ""
        }

            
        aliases_responses.value = responses_aliases_respo[select_message];

        if (select_message in responses_aliases_respo) {
            aliases_responses.value = responses_aliases_respo[select_message];
        } else {
            aliases_responses.value = "{username}";
        }

    } else if (type_id == "save-response"){

        data = {
            type_id: type_id,
            key: select_message,
            response: response_input.value,
            status : status.checked ? 1 : 0,
            status_s : status_s.checked ? 1 : 0,
        }

        window.pywebview.api.responses_config(type_id,data)

        response_input.value = '';
        aliases_responses.value = '';
        edit_div.hidden = true

    } else if (type_id == "change"){
        edit_div.hidden = true
    }
}

async function black_list_remove(music){

    var music_data = await window.pywebview.api.sr_config_py('list_rem',music);
        
    if (music_data){

        music_list = JSON.parse(music_data)

        var dataTableData = [];

        $.each(music_list, function(index, value) {

            var button_config = document.createElement("button");

            button_config.innerText = "Remover";
            button_config.classList.add('bnt','bt-submit')
            button_config.setAttribute('onclick', `black_list_remove('${value}')`)

            dataTableData.push([
                value,
                button_config.outerHTML
            ]);
        });

        if ($.fn.DataTable.isDataTable("#list_musics_block")) {

            $('#list_musics_block').DataTable().clear().draw();
            $('#list_musics_block').DataTable().destroy();
        }  

        var table = $('#list_musics_block').DataTable( {
            destroy: true,
            scrollX: true,
            paging: false,
            ordering:  false,
            retrieve : false,
            processing: true,
            responsive: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            },
            columns: [
                { title: 'Termos de musicas bloqueados' },
                { title: 'Remover' }
            ]
        } );

        for (var i = 0; i < dataTableData.length; i++) {
            table.row.add(dataTableData[i]).draw();
        }
    }


}

async function sr_config_js(event,type_id){
    
    if (type_id == 'get'){

        var check_seletor = document.querySelector('#music-enable');
        var max_duration = document.getElementById("max-duration")
        var skip_votes = document.getElementById("skip-requests");
        var skip_mod = document.getElementById("skip-ignore");
    
        var music_config = await window.pywebview.api.sr_config_py(type_id,'null');
        
        if(music_config){
            
            music_config = JSON.parse(music_config)

            if (music_config.allow_music == 1){
                check_seletor.checked = true;
            } else if (music_config.allow_music == 0){
                check_seletor.checked = false;
            }

            if(music_config.skip_mod == 1){
                skip_mod.checked = true
            }
            
            max_duration.value = music_config.max_duration;
            skip_votes.value = music_config.skip_votes;
    
        }

    }   else if (type_id == 'save'){

        var check_seletor = document.getElementById('music-enable');
        var max_duration = document.getElementById("max-duration")

        var skip_votes = document.getElementById("skip-requests");
        var skip_mod = document.getElementById("skip-ignore");
    
        allow_music = check_seletor.checked == true ? 1 : 0

        skip_mod = skip_mod.checked == true ? 1 : 0
    
        data = {
            max_duration: max_duration.value,
            allow_music_save : allow_music,
            skip_votes : skip_votes.value,
            skip_mod : skip_mod
        }
    
        var formData = JSON.stringify(data);
        window.pywebview.api.sr_config_py(type_id,formData);
        
        
    } else if (type_id == 'list_get'){

        var music_data = await window.pywebview.api.sr_config_py(type_id,'null')
        
        if (music_data){

            music_list = JSON.parse(music_data)
            
            $("#modal_list_block").modal("show")

            var dataTableData = [];

            $.each(music_list, function(index, value) {

                var button_config = document.createElement("button");

                button_config.innerText = "Remover";
                button_config.classList.add('bnt','bt-submit')
                button_config.setAttribute('onclick', `black_list_remove('${value}')`)

                dataTableData.push([
                    value,
                    button_config.outerHTML
                ]);
            });

            if ($.fn.DataTable.isDataTable("#list_musics_block")) {

                $('#list_musics_block').DataTable().clear().draw();
                $('#list_musics_block').DataTable().destroy();
            }
            

            var table = $('#list_musics_block').DataTable( {
                destroy: true,
                scrollX: true,
                paging: false,
                ordering:  false,
                retrieve : false,
                processing: true,
                responsive: false,
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                },
                columns: [
                    { title: 'Termos de musicas bloqueados' },
                    { title: 'Remover' }
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }
        }

    } else if (type_id == 'list_add'){

        var blocked_music = document.getElementById('blocked-music').value;

        window.pywebview.api.sr_config_py(type_id,blocked_music);

        blocked_music.value = '';
        
    } else if (type_id == 'list_rem'){

        var blocked_music = document.getElementById('blocked-music').value;

        window.pywebview.api.sr_config_py(type_id,blocked_music);

        blocked_music.value = '';
        
    }
}

async function setElementState(elementId, value) {

    var element = document.getElementById(elementId);

    if (element) {

      if (element.type === "checkbox") {

        element.checked = value === 1;

      } else if (element.tagName === "SELECT") {

        $("#" + elementId).selectpicker('val', value);

      } else if (element.tagName === "INPUT" && element.type === "range") {

        element.value = value;

      } else if (element.tagName === "INPUT" && element.type === "number") {

        element.value = value;

      }
    }
}

async function get_event_state(){

    var select = document.getElementById('select-event-type')

    data ={
        "type_id" : 'get_state',
        "type" : select.value
    };

    var event_data = await window.pywebview.api.event_log(JSON.stringify(data))

    if (event_data){

        document.getElementById('select-show').hidden = false

        data_parse = JSON.parse(event_data)
        
        setElementState('show-event',data_parse["show-event"])
        setElementState('show-event-chat',data_parse["show-event-chat"])
        setElementState('show-event-html',data_parse["show-event-html"])
        setElementState('show-event-alert',data_parse["show-event-alert"])

    }
}

async function event_log_config(type_id){

    var sliderFontEvents = document.getElementById("slider-font-events");
    var sliderFontEventsOverlay = document.getElementById("font-events-overlay");
    var colorEvents = document.getElementById("color-events");
    var dataShowEvents = document.getElementById("data-show-events");
    var backgroundColorEvent = document.getElementById("event-background-color-text");
    var backgroundColorEventText = document.getElementById("event-text-color-text");
    var backgroundColorEventspan = document.getElementById("event-background-color-span");
    var backgroundColorEventTextspan = document.getElementById("event-text-color-span");
    var eventDelay = document.getElementById('event-delay');

    if (type_id == 'save'){

        dataShowEvents = dataShowEvents.checked ? 1 : 0

        data = {}
        data["type_id"] = type_id;
        data['font-events-overlay'] = sliderFontEventsOverlay.value
        data["slider-font-events"] = sliderFontEvents.value;
        data["color-events"] = colorEvents.value;
        data["data-show-events"] = dataShowEvents;
        data["background-color"] = backgroundColorEvent.value;
        data["text-color"] = backgroundColorEventText.value;
        data["event-delay"] = eventDelay.value;

        window.pywebview.api.event_log(JSON.stringify(data));

    } else if (type_id == 'get'){

        data ={
            "type_id" : type_id
        };

        var event_data = await window.pywebview.api.event_log(JSON.stringify(data))

        if (event_data){

            event_data_parse = JSON.parse(event_data)
              
            Object.keys(event_data_parse).forEach(function(elementId) {
                var value = event_data_parse[elementId];
                setElementState(elementId, value);
            });

            backgroundColorEvent.value = event_data_parse.background_color
            backgroundColorEventText.value = event_data_parse.text_color

            backgroundColorEventspan.style.backgroundColor = event_data_parse.background_color;
            backgroundColorEventTextspan.style.backgroundColor = event_data_parse.text_color;

        }

    } else if (type_id == 'save_state'){
        
        element = document.getElementById('select-event-type');
        data = {}
        data["type_id"] = type_id;
        data["type"] = element.value;
        data["show-event"] = document.getElementById('show-event').checked ? 1 : 0;
        data["show-event-chat"] = document.getElementById('show-event-chat').checked ? 1 : 0;
        data["show-event-html"] = document.getElementById('show-event-html').checked ? 1 : 0;
        data["show-event-alert"] = document.getElementById('show-event-alert').checked ? 1 : 0;

        window.pywebview.api.event_log(JSON.stringify(data));

        document.getElementById('select-show').hidden = true

    }


}

async function show_error_log(type_id){

    if (type_id == 'get-errorlog'){

        $("#errorlog-modal").modal("show");

        $('#errorlog-textarea').val('Aguarde, carregando...');
        
        var textarea = document.getElementById('errorlog-textarea');

        var errors_data = await window.pywebview.api.open_py('errolog','null')
        
        text_to_textarea = ''

        if (errors_data){
            
            errors_data.forEach(error_item => {

                text_to_textarea += `${error_item.message} \n`
                text_to_textarea += "\n"
                
            });

            $('#errorlog-textarea').val(text_to_textarea);
        }

    } else if (type_id == 'clear-errorlog'){

        $("#errorlog-modal").modal("hide");
        $('#errorlog-textarea').val('');

        window.pywebview.api.open_py('errolog_clear','null')

    }

    debug_status('rel-get')
}

async function debug_status(type_id){

    var status_debug = document.getElementById("debug-status");

    if (type_id == "debug-save"){

        status_debug = status_debug.checked ? 1 : 0;

        window.pywebview.api.open_py(type_id,status_debug)

    } else if (type_id == "debug-get"){

        var get_debug = await window.pywebview.api.open_py(type_id,'null');

        if (get_debug){

            status_debug.checked = get_debug == 1 ? true : false;

        }
    } else if (type_id == "rel-get"){

        var status_rel = document.getElementById('rel-status') 
        
        var get_rel = await window.pywebview.api.open_py(type_id,'null');

        if (get_rel){

            status_rel.checked = get_rel == 1 ? true : false;

        }

    } else if (type_id == "rel-save"){

        var status_rel = document.getElementById('rel-status') 
        
        status_rel = status_rel.checked ? 1 : 0;

        window.pywebview.api.open_py(type_id,status_rel)

    }

}

async function ttk_alerts(type){

    var follow_input_sound = document.getElementById('file-select-ttk-follow');
    var follow_status_sound = document.getElementById('ttk-sound-status-follow');
    var follow_volume_sound = document.getElementById('audio-volume-ttk-follow');
    var follow_video = document.getElementById('video-follow');
    var follow_video_status = document.getElementById('follow-video-status');
    var follow_video_time = document.getElementById('video-time-follow');

    var like_input_sound = document.getElementById('file-select-ttk-like');
    var like_status_sound = document.getElementById('ttk-sound-status-like');
    var like_volume_sound = document.getElementById('audio-volume-ttk-like');
    var like_video = document.getElementById('video-like');
    var like_video_status = document.getElementById('like-video-status');
    var like_video_time = document.getElementById('video-time-like');
    
    var like_delay = document.getElementById('ttk-like-delay');

    var share_input_sound = document.getElementById('file-select-ttk-share');
    var share_status_sound = document.getElementById('ttk-sound-status-share');
    var share_volume_sound = document.getElementById('audio-volume-ttk-share');
    var share_video = document.getElementById('video-share');
    var share_video_status = document.getElementById('share-video-status');
    var share_video_time = document.getElementById('video-time-share');

    var share_delay = document.getElementById('ttk-share-delay');
    
    
    if (type == 'get'){

        data = {
            type_id : type,
        }

        var data = JSON.stringify(data);

        var data_re = await window.pywebview.api.tiktok_alerts(data);
    
        if (data_re) {

            rec_data = JSON.parse(data_re)

            select_alert = document.getElementById('alert-select').value;

            if (select_alert == 'likes'){

                like_delay.value = rec_data.like_delay;
                like_status_sound.checked = rec_data.like_sound_status == 1 ? true : false;
                like_volume_sound.value = rec_data.like_sound_volume;
                like_input_sound.value = rec_data.like_sound_loc;
                like_video.value = rec_data.like_video;
                like_video_status.checked = rec_data.like_video_status == 1 ? true : false;
                like_video_time.value = rec_data.like_video_time;

                document.getElementById('alert-like').hidden = false;

            } else if (select_alert == 'follow'){

                follow_status_sound.checked = rec_data.follow_sound_status == 1 ? true : false;
                follow_volume_sound.value = rec_data.follow_sound_volume;
                follow_input_sound.value = rec_data.follow_sound_loc;
                follow_video.value = rec_data.follow_video;
                follow_video_status.checked = rec_data.follow_video_status == 1 ? true : false;
                follow_video_time.value = rec_data.follow_video_time;

                document.getElementById('alert-follow').hidden = false;
    
            } else if (select_alert == 'share'){

                share_delay.value = rec_data.share_delay;
                share_status_sound.checked = rec_data.share_sound_status == 1 ? true : false;
                share_volume_sound.value = rec_data.share_sound_volume;
                share_input_sound.value = rec_data.share_sound_loc;
                share_video.value = rec_data.share_video;
                share_video_status.checked = rec_data.share_video_status == 1 ? true : false;
                share_video_time.value = rec_data.share_video_time;

                document.getElementById('alert-share').hidden = false;
            }
    
        }

    } else if (type == "save_sound_follow"){
        
        var status_sound = follow_status_sound.checked ? 1 : 0;
        var status_video = follow_video_status.checked ? 1 : 0;

        data = {
            type_id : "save_sound_follow",
            sound: status_sound,
            sound_loc : follow_input_sound.value,
            sound_volume : follow_volume_sound.value,
            video: follow_video.value,
            video_status: status_video,
            video_time: follow_video_time.value
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_alerts(data)
        
        document.getElementById('alert-follow').hidden = true;
        
    } else if (type == "save_sound_like"){
        
        var status_sound = like_status_sound.checked ? 1 : 0;
        var status_video = like_video_status.checked ? 1 : 0;

        data = {
            type_id : "save_sound_like",
            sound: status_sound,
            sound_loc : like_input_sound.value,
            sound_volume : like_volume_sound.value,
            delay : like_delay.value,
            video: like_video.value,
            video_status: status_video,
            video_time: like_video_time.value
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_alerts(data)

        document.getElementById('alert-like').hidden = true;
        
    } else if (type == "save_sound_share"){
        
        var status_sound = share_status_sound.checked ? 1 : 0;
        var status_video = share_video_status.checked ? 1 : 0;

        data = {
            type_id : "save_sound_share",
            sound: status_sound,
            sound_loc : share_input_sound.value,
            sound_volume : share_volume_sound.value,
            delay : share_delay.value,
            video: share_video.value,
            video_status: status_video,
            video_time: share_video_time.value
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_alerts(data)

        document.getElementById('alert-share').hidden = true;

    } else if (type == "change"){
        document.getElementById('alert-follow').hidden = true;
        document.getElementById('alert-like').hidden = true;
        document.getElementById('alert-share').hidden = true;
    } else if (type == "get_overlay"){

        var sliderFontAlerts = document.getElementById('slider-font-alerts');
        var sliderOpacityAlerts = document.getElementById('slider-opacity-alerts');
        var sliderFontAlertsValue = document.getElementById('rangevaluessalertsopacity');
        var alertsTextColorText = document.getElementById('alerts-text-color-text');
        var alertsTextColorTextSpan = document.getElementById('alerts-text-color-span');
        var alertsBackgroundColorText = document.getElementById('alerts-background-color-text');
        var alertsBackgroundColorTextSpan = document.getElementById('alerts-background-color-span');
        var alertDelay = document.getElementById('alert-delay');
        var alertImageSize = document.getElementById('alert-imagesize');

        var sliderFontAlertsVideo = document.getElementById('slider-font-alertsvideo');
        var sliderOpacityAlertsVideo = document.getElementById('slider-opacity-alertsvideo');
        var sliderFontAlertsValue = document.getElementById('rangevaluessalertsvideoopacity');
        var alertsvideoTextColorText = document.getElementById('alertsvideo-text-color-text');
        var alertsvideoTextColorTextSpan = document.getElementById('alertsvideo-text-color-span');
        var alertsvideoBackgroundColorText = document.getElementById('alertsvideo-background-color-text');
        var alertsvideoBackgroundColorTextSpan = document.getElementById('alertsvideo-background-color-span');
        var alertsvideoImageSize = document.getElementById('alertsvideo-imagesize');

        data = {
            type_id : type,
        }

        var data = JSON.stringify(data);

        var data_re = await window.pywebview.api.tiktok_alerts(data);
    
        if (data_re) {
            
            rec_data = JSON.parse(data_re)

            sliderFontAlerts.value = rec_data.font_alerts;
            sliderOpacityAlertsVideo.value = rec_data.opacity_alerts;
            sliderFontAlertsValue.innerHTML = rec_data.opacity_alerts;
            alertsTextColorText.value = rec_data.color_alerts;
            alertsBackgroundColorText.value = rec_data.background_alerts;
            alertDelay.value = rec_data.delay_alerts;
            alertImageSize.value = rec_data.image_size;
            

            sliderFontAlertsVideo.value = rec_data.font_alertsvideo;
            sliderOpacityAlertsVideo.value = rec_data.opacity_alertsvideo;
            sliderFontAlertsValue.innerHTML = rec_data.opacity_alertsvideo;
            alertsvideoTextColorText.value = rec_data.color_alertsvideo;
            alertsvideoBackgroundColorText.value = rec_data.background_alertsvideo;
            alertsvideoImageSize.value = rec_data.image_sizevideo;
            
            alertsTextColorTextSpan.style.backgroundColor = rec_data.color_alerts;
            alertsBackgroundColorTextSpan.style.backgroundColor = rec_data.background_alerts;
            alertsvideoTextColorTextSpan.style.backgroundColor = rec_data.color_alertsvideo;
            alertsvideoBackgroundColorTextSpan.style.backgroundColor = rec_data.background_alertsvideo;

        }
    } else if (type == "save_overlay"){

        var sliderFontAlerts = document.getElementById('slider-font-alerts');
        var sliderOpacityAlerts = document.getElementById('slider-opacity-alerts');
        var sliderFontAlertsValue = document.getElementById('rangevaluessalertsopacity');
        var alertsTextColorText = document.getElementById('alerts-text-color-text');
        var alertsTextColorTextSpan = document.getElementById('alerts-text-color-span');
        var alertsBackgroundColorText = document.getElementById('alerts-background-color-text');
        var alertsBackgroundColorTextSpan = document.getElementById('alerts-background-color-span');
        var alertDelay = document.getElementById('alert-delay');
        var alertImageSize = document.getElementById('alert-imagesize');
      
        var sliderFontAlertsVideo = document.getElementById('slider-font-alertsvideo');
        var sliderOpacityAlertsVideo = document.getElementById('slider-opacity-alertsvideo');
        var sliderFontAlertsValue = document.getElementById('rangevaluessalertsvideoopacity');
        var alertsvideoTextColorText = document.getElementById('alertsvideo-text-color-text');
        var alertsvideoTextColorTextSpan = document.getElementById('alertsvideo-text-color-span');
        var alertsvideoBackgroundColorText = document.getElementById('alertsvideo-background-color-text');
        var alertsvideoBackgroundColorTextSpan = document.getElementById('alertsvideo-background-color-span');
        var alertsvideoImageSize = document.getElementById('alertsvideo-imagesize');

        font_alerts = sliderFontAlerts.value
        color_alerts = alertsTextColorText.value 
        background_alerts = alertsBackgroundColorText.value
        opacity_alerts = sliderOpacityAlerts.value
        delay_alerts = alertDelay.value
        alertImageSize = alertImageSize.value
        
        font_alertsvideo = sliderFontAlertsVideo.value
        color_alertsvideo = alertsvideoTextColorText.value
        background_alertsvideo = alertsvideoBackgroundColorText.value
        opacity_alertsvideo = sliderOpacityAlertsVideo.value
        alertsvideoImageSize = alertsvideoImageSize.value
        
        data = {
            type_id : "save_overlay",
            font_alerts : font_alerts,
            color_alerts : color_alerts,
            background_alerts : background_alerts,
            image_size : alertImageSize,
            opacity_alerts : opacity_alerts,
            delay_alerts : delay_alerts,
            font_alertsvideo : font_alertsvideo,
            color_alertsvideo : color_alertsvideo,
            background_alertsvideo : background_alertsvideo,
            image_sizevideo : alertsvideoImageSize,
            opacity_alertsvideo : opacity_alertsvideo
        }

        window.pywebview.api.tiktok_alerts(JSON.stringify(data));
    }
}

async function ttk_modal(button){

    var id = button.getAttribute('data-id');
    var gift_id_inp = document.getElementById('ttk-gift-id');
    gift_id_inp.value = id
    ttk_gift('modal')

}

async function ttk_modal_points(button){

    var id = button.getAttribute('data-id');
    var gift_id_inp = document.getElementById('ttk-gift-id-point');
    gift_id_inp.value = id
    ttk_gift('modal-points')

}

async function ttk_gift(type_id){

    if (type_id == "get_table"){

        data = {
            type_id : "get",
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.tiktok_gift(data);
    
        if (rec) {

            rec_data = JSON.parse(rec)

            var dataTableData = [];

            var gift_data = rec_data.gifts

            for (const key in gift_data) {

                if (gift_data.hasOwnProperty(key)) {

                    const item = gift_data[key];
                    
                    var gift_id = key
                    var gift_name = item.name
                    var gift_name_br = item.name_br
                    var diamonds = item.value
                    
                    var button_config = document.createElement("button");

                    button_config.innerText = "Configurar";
                    button_config.classList.add('bnt','bt-submit')
                    button_config.setAttribute('data-id', `${gift_id}`)
                    button_config.setAttribute('onclick', `ttk_modal(this)`)

                    dataTableData.push([
                        gift_name,
                        gift_name_br,
                        diamonds,
                        button_config.outerHTML
                    ]);

                }
            }


            if ($.fn.DataTable.isDataTable("#giftlist_table")) {

                $('#giftlist_table').DataTable().clear().draw();
                $('#giftlist_table').DataTable().destroy();
            }

            var table = $('#giftlist_table').DataTable( {
                destroy: true,
                scrollX: true,
                scrollY: '300px',
                paging: false,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                },
                columns: [
                    { title: 'ID',"searchable": true },
                    { title: 'Nome' },
                    { title: 'Diamantes' },
                    { title: 'Ação' }
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }

        }

    } else if (type_id == "get_global"){

        data = {
            type_id : "get_global",
        }

        var data = JSON.stringify(data);

        var rec_data = await window.pywebview.api.tiktok_gift(data);
    
        if (rec_data) {

            var global_gift_status = document.getElementById('global-gift-status');
            var global_gift_volume = document.getElementById('global-gift-volume');
            var global_gift_volume_text = document.getElementById('rangevalue_global_gift_volume');
            var global_gift_sound = document.getElementById('global-gift-sound');

            var global_gift_video = document.getElementById('global-video-gift');
            var global_gift_video_status = document.getElementById('global-gift-video-status');
            var global_gift_video_time = document.getElementById('global-video-time-gift');
            var global_gift_video_time_text = document.getElementById('rangevalue_globalvideotime_gift');
    
            global_gift_video.value = rec_data.video;
            global_gift_video_status.checked = rec_data.video_status == 1 ? true : false;
            global_gift_video_time.value = rec_data.video_time;
            global_gift_status.checked = rec_data.status == 1 ? true : false;
            global_gift_sound.value = rec_data.audio;
            global_gift_volume.value = rec_data.volume;
            global_gift_volume_text.innerHTML = rec_data.volume;
            global_gift_video_time_text.innerHTML = rec_data.video_time;
        }

    } else if (type_id == "get_points"){

        data = {
            type_id : "get",
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.tiktok_gift(data);
    
        if (rec) {

            rec_data = JSON.parse(rec)

            var dataTableData = [];

            var gift_data = rec_data.gifts

            for (const key in gift_data) {

                if (gift_data.hasOwnProperty(key)) {

                    const item = gift_data[key];
                    
                    var gift_id = key
                    var gift_name = item.name
                    var gift_name_br = item.name_br
                    var points = item.points
                    
                    var button_config = document.createElement("button");

                    button_config.innerText = "Configurar";
                    button_config.classList.add('bnt','bt-submit')
                    button_config.setAttribute('data-id', `${gift_id}`)
                    button_config.setAttribute('onclick', `ttk_modal_points(this)`)

                    dataTableData.push([
                        gift_name,
                        gift_name_br,
                        points,
                        button_config.outerHTML
                    ]);

                }
            }


            if ($.fn.DataTable.isDataTable("#giftlist_points_table")) {

                $('#giftlist_points_table').DataTable().clear().draw();
                $('#giftlist_points_table').DataTable().destroy();
            }

            var table = $('#giftlist_points_table').DataTable( {
                destroy: true,
                scrollX: true,
                scrollY: '300px',
                paging: false,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                },
                columns: [
                    { title: 'ID',"searchable": true },
                    { title: 'Nome' },
                    { title: 'Pontos' },
                    { title: 'Ação' }
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }

        }
        
    } else if (type_id == "modal"){

        var gift_name = document.getElementById('gift-name');
        var gift_sound = document.getElementById('file-select-sound-gift');
        var gift_video = document.getElementById('video-gift');
        var gift_video_time = document.getElementById('video-time-gift');
        var gift_video_status = document.getElementById('gift-video-status');
        var gift_status = document.getElementById('gift-sound-status');
        var gift_volume_sound = document.getElementById('audio-volume-ttk-gift');
        var gift_id_inp = document.getElementById('ttk-gift-id');
        var gift_key_status = document.getElementById('gift-key-status');
        var gift_key1 = document.getElementById('gift-key-1');
        var gift_key2 = document.getElementById('gift-key-2');
        var gift_key3 = document.getElementById('gift-key-3');
        var gift_key4 = document.getElementById('gift-key-4');
        var gift_key_time = document.getElementById('time-key-gift');

        data = {
            type_id : "get_gift_info",
            id : gift_id_inp.value
        }

        var data = JSON.stringify(data);

        var gift_data = await window.pywebview.api.tiktok_gift(data);

        if (gift_data){

            gift_rec_data = JSON.parse(gift_data)

            $("#gift-modal").modal("show");

            gift_name.value = gift_rec_data.name
            gift_sound.value = gift_rec_data.audio
            gift_video.value = gift_rec_data.video
            gift_video_time.value = gift_rec_data.video_time
            gift_status.checked = gift_rec_data.status == 1 ? true : false;
            gift_volume_sound.value = gift_rec_data.volume;

            gift_video_status.checked = gift_rec_data.video_status == 1 ? true : false;
            gift_key_status.checked = gift_rec_data.key_status == 1 ? true : false;

            $("#gift-key-1").selectpicker('val', gift_rec_data.keys[0]);
            $("#gift-key-1").selectpicker("refresh");

            $("#gift-key-2").selectpicker('val', gift_rec_data.keys[1]);
            $("#gift-key-2").selectpicker("refresh");

            $("#gift-key-3").selectpicker('val', gift_rec_data.keys[2]);
            $("#gift-key-3").selectpicker("refresh");

            $("#gift-key-4").selectpicker('val', gift_rec_data.keys[3]);
            $("#gift-key-4").selectpicker("refresh");

            gift_key_time.value = gift_rec_data.key_time

            document.getElementById('save-gift-notification').setAttribute('onclick',`ttk_gift('save_sound_gift')`)
            document.getElementById('test-gift-notification').setAttribute('onclick',`test_js('test_sound_gift')`)

        }
        
    } else if (type_id == "modal-points"){

        var gift_points = document.getElementById('gift-point');
        var gift_points_status = document.getElementById('gift-global-point-status');
        var gift_id_inp_point = document.getElementById('ttk-gift-id-point');

        data = {
            type_id : "get_gift_info",
            id : gift_id_inp_point.value
        }

        var data = JSON.stringify(data);

        var gift_data = await window.pywebview.api.tiktok_gift(data);

        if (gift_data){

            gift_rec_data = JSON.parse(gift_data)

            $("#gift-points-modal").modal("show");

            gift_points_status.checked = gift_rec_data.points_status == 1 ? true : false;
            gift_points.value = gift_rec_data.points;

            document.getElementById('save-gift-points').setAttribute('onclick',`ttk_gift('save_point_gift')`)
        }
        
    } else if (type_id == "save_point_gift"){ 

        var gift_points = document.getElementById('gift-point');
        var gift_points_status = document.getElementById('gift-global-point-status');

        var gift_status = gift_points_status.checked ? 1 : 0;

        var gift_id_inp = document.getElementById('ttk-gift-id-point');

        data = {
            type_id : "save_point_gift",
            id : gift_id_inp.value,
            status: gift_status,
            points : gift_points.value
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_gift(data)
        gift_id_inp.value = ''

    } else if (type_id == "save_sound_gift"){ 

        var gift_name = document.getElementById('gift-name');
        var gift_sound = document.getElementById('file-select-sound-gift')
        var gift_status = document.getElementById('gift-sound-status')
        var gift_volume_sound = document.getElementById('audio-volume-ttk-gift')
        var gift_video = document.getElementById('video-gift');
        var gift_video_time = document.getElementById('video-time-gift');
        var gift_video_status = document.getElementById('gift-video-status');
        var gift_key_status = document.getElementById('gift-key-status');
        var gift_key1 = document.getElementById('gift-key-1');
        var gift_key2 = document.getElementById('gift-key-2');
        var gift_key3 = document.getElementById('gift-key-3');
        var gift_key4 = document.getElementById('gift-key-4');
        var gift_key_time = document.getElementById('time-key-gift');

        var gift_status = gift_status.checked ? 1 : 0;
        var gift_key_status = gift_key_status.checked ? 1 : 0;
        
        var gift_key_list = [gift_key1.value, gift_key2.value, gift_key3.value, gift_key4.value]

        var gift_id_inp = document.getElementById('ttk-gift-id');

        data = {
            type_id : "save_sound_gift",
            id : gift_id_inp.value,
            name: gift_name.value,
            status: gift_status,
            sound_loc : gift_sound.value,
            sound_volume : gift_volume_sound.value,
            video : gift_video.value,
            video_time : gift_video_time.value,
            video_status : gift_video_status.checked ? 1 : 0,
            keys: gift_key_list,
            key_status : gift_key_status,
            key_time : gift_key_time.value
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_gift(data)
        gift_id_inp.value = ''
        $("#gift-modal").modal("hide");
        

    } else if (type_id == "global_gift_save"){

        var global_gift_status = document.getElementById('global-gift-status');
        var global_gift_volume = document.getElementById('global-gift-volume');
        var global_gift_sound = document.getElementById('global-gift-sound');

        var global_gift_video = document.getElementById('global-video-gift');
        var global_gift_video_status = document.getElementById('global-gift-video-status');
        var global_gift_video_time = document.getElementById('global-video-time-gift');

        data = {
            type_id : "global_gift_save",
            status : global_gift_status.checked ? 1 : 0,
            volume : global_gift_volume.value,
            sound : global_gift_sound.value,
            video : global_gift_video.value,
            video_status : global_gift_video_status.checked ? 1 : 0,
            video_time : global_gift_video_time.value
        }

        var data = JSON.stringify(data);
        window.pywebview.api.tiktok_gift(data)
        
    } 
    
}

async function ttk_goal(type_id){
    
    var goal_type = document.getElementById('goal-select');
    var goal_html_type = document.getElementById('goal-html-select');
    var edit_goal_div = document.getElementById('edit-goal-div');

    var goal_add_div = document.getElementById('goal-add-div');

    if(type_id == 'get'){

        data = {
            type_id : type_id,
            goal_type : goal_type.value
        }
    
        var data_parse = JSON.stringify(data);
    
        var goal_data = await window.pywebview.api.tiktok_goal(data_parse);
    
        if (goal_data){
    
            goal_data = JSON.parse(goal_data)
    
            edit_goal_div.hidden = false
    
            var status_goal = document.getElementById('goal-status') 
            var goal_sound_status = document.getElementById('goal-status-sound');

            var goal_video_status = document.getElementById('goal-video-status');
            var goal_video_file = document.getElementById('video-goal');
            var goal_video_time = document.getElementById('video-time-goal');
    
            status_goal.checked = goal_data.status == 1 ? true : false;
            goal_sound_status.checked = goal_data.status_sound == 1 ? true : false;
    
            document.getElementById('goal').value = goal_data.goal;
            document.getElementById('file-select-ttk-goal-sound').value = goal_data.sound_file;
            document.getElementById('audio-volume-ttk-goal-sound').value = goal_data.sound_volume;
            goal_video_file.value = goal_data.video_file;
            goal_video_time.value = goal_data.video_time;
            goal_video_status.checked = goal_data.video_status == 1 ? true : false;

            if (goal_data.goal_add != "double"){

                goal_add_div.hidden = false
                document.getElementById('goal-add-value').value = goal_data.goal_add

            } else {
                goal_add_div.hidden = true
            }

            if (goal_type.value == "gift"){

                document.getElementById("goal-gift-select").hidden = false;

                goal_data.gift_list.forEach(element => {

                    $("#goal-gift").append('<option style="background: #000; color: #fff;" value="'+ element.id +'">'+ element.name +'</option>');
                    $("#goal-gift").selectpicker("refresh");

                });

            } else {
                
                document.getElementById("goal-gift-select").hidden = true;

            }
            
            $("#goal-event").selectpicker('val',goal_data.event)
    
        }

    } else if (type_id == 'save'){

        var status_goal = document.getElementById('goal-status') 
        var status_goal_value = status_goal.checked ? 1 : 0;

        var goal = document.getElementById('goal').value;
        var goal_event = document.getElementById('goal-event');

        var goal_sound_status = document.getElementById('goal-status-sound');
        var goal_sound_status_value = goal_sound_status.checked ? 1 : 0;

        var goal_sound_file = document.getElementById('file-select-ttk-goal-sound');
        var goal_sound_volume = document.getElementById('audio-volume-ttk-goal-sound');

        var goal_video_status = document.getElementById('goal-video-status');
        var goal_video_file = document.getElementById('video-goal');
        var goal_video_time = document.getElementById('video-time-goal');

        var goal_add_value = document.getElementById('goal-add-value');

        if  (goal_type.value == "gift"){

            data = {
                type_id : type_id,
                gift: document.getElementById('goal-gift').value,
                goal : goal,
                goal_type : goal_type.value,
                goal_add_value : goal_add_value.value,
                status: status_goal_value,
                event:goal_event.value,
                sound_status: goal_sound_status_value,
                sound_file: goal_sound_file.value,
                sound_volume: goal_sound_volume.value,
                video_status: goal_video_status.checked ? 1 : 0,
                video_file: goal_video_file.value,
                video_time: goal_video_time.value
            }

        } else{

            data = {
                type_id : type_id,
                goal : goal,
                goal_type : goal_type.value,
                goal_add_value : goal_add_value.value,
                status: status_goal_value,
                event:goal_event.value,
                sound_status: goal_sound_status_value,
                sound_file: goal_sound_file.value,
                sound_volume: goal_sound_volume.value,
                video_status: goal_video_status.checked ? 1 : 0,
                video_file: goal_video_file.value,
                video_time: goal_video_time.value
            }
        }

        var data_parse = JSON.stringify(data);
        window.pywebview.api.tiktok_goal(data_parse);

        goal_add_div.hidden = true
        edit_goal_div.hidden = true
        document.getElementById("goal-gift-select").hidden = true;

    } else if (type_id == 'save_html'){


        var goalText = document.getElementById("goal-text");

        var goal_style = document.getElementById('goal-style');
        var goal_text_above = document.getElementById('goal-text-above');
        var goal_text_type = document.getElementById('goal-text-type');
        var goal_text_size = document.getElementById('slider-font-bar');
        var goalTextColorInput = document.getElementById("goal-text-color-text");
        var goalBarColorInput = document.getElementById("goal-bar-color-text");
        var goalBackgroundBarColorInput = document.getElementById("goal-background-bar-color-text");
        var goalBackgroundBarColorOpacity = document.getElementById("goal-background-opacity");
        var goalBackgroundColorInput = document.getElementById("goal-background-color-text");
        var goalBackgroundBarBorderColorInput = document.getElementById("goal-background-color-border-text");

        var goalTextColorspan = document.getElementById("goal-text-color-span");
        var goalBarColorspan = document.getElementById("goal-bar-color-span");
        var goalBackgroundBarColorspan = document.getElementById("goal-background-bar-color-span");
        var goalBackgroundColorspan = document.getElementById("goal-background-color-span");
        var goalBackgroundBorderColorspan = document.getElementById("goal-background-color-border-span");

        var goal_text_above = goal_text_above.checked ? 1 : 0;

        data = {
            type_id : type_id,
            type_goal : goal_html_type.value,
            goal_above : goal_text_above,
            goal_style : goal_style.value,
            goal_type : goal_text_type.value,
            text_value : goalText.value,
            text_color : goalTextColorInput.value,
            text_size : goal_text_size.value,
            bar_color: goalBarColorInput.value,
            background_bar_color: goalBackgroundBarColorInput.value,
            background_bar_color_opacity: goalBackgroundBarColorOpacity.value,
            background_border: goalBackgroundBarBorderColorInput.value,
            background_color : goalBackgroundColorInput.value
        }

        var data_parse = JSON.stringify(data);

        window.pywebview.api.tiktok_goal(data_parse);

        for (var key in DataIframeLinks) {

            if (key === goal_html_type.value) {
                document.getElementById(`iframe-${key}-config`).hidden = false
            } else {
                document.getElementById(`iframe-${key}-config`).hidden = true
            }
        }


    } else if (type_id == 'get_html'){

        
        var goalText = document.getElementById("goal-text");


        var goal_text_above = document.getElementById('goal-text-above');
        var goal_text_type = document.getElementById('goal-text-type');

        var goal_text_size = document.getElementById('slider-font-bar');

        var goalTextColorInput = document.getElementById("goal-text-color-text");
        var goalBarColorInput = document.getElementById("goal-bar-color-text");
        var goalBackgroundBarColorInput = document.getElementById("goal-background-bar-color-text");
        var goalBackgroundBarBorderColorInput = document.getElementById("goal-background-color-border-text");
        
        var goalBackgroundBarColorOpacity = document.getElementById("goal-background-opacity");
        var goalBackgroundColorInput = document.getElementById("goal-background-color-text");

        var goalTextColorspan = document.getElementById("goal-text-color-span");
        var goalBarColorspan = document.getElementById("goal-bar-color-span");
        var goalBackgroundBarColorspan = document.getElementById("goal-background-bar-color-span");
        var goalBackgroundColorspan = document.getElementById("goal-background-color-span");
        var goalBackgroundBorderColorspan = document.getElementById("goal-background-color-border-span");

        var GoalLinkInput = document.getElementById("iframe-link");
        
        data = {
            type_id : type_id,
            type_goal : goal_html_type.value
        }
    
        var data_parse = JSON.stringify(data);
        
        var html_data = await window.pywebview.api.tiktok_goal(data_parse);
    
        if (html_data){

            html_data_parse = JSON.parse(html_data)

            console.log(html_data_parse)

            document.getElementById('html_editor').hidden = false

            goalText.value = html_data_parse.title_text_value;

            $("#goal-style").selectpicker('val',html_data_parse.goal_style)
            $("#goal-text-type").selectpicker('val',html_data_parse.goal_type)

            goal_text_above.checked = html_data_parse.goal_above == 1 ? true : false

            goal_text_size.value = html_data_parse.text_size;

            goalTextColorInput.value = html_data_parse.title_text;
            goalBarColorInput.value = html_data_parse.progress_bar;
            goalBackgroundBarColorInput.value = html_data_parse.progress_bar_background;
            goalBackgroundColorInput.value = html_data_parse.background_color;
            goalBackgroundBarBorderColorInput.value = html_data_parse.background_border;

            goalTextColorspan.style.backgroundColor = html_data_parse.title_text;
            goalBarColorspan.style.backgroundColor = html_data_parse.progress_bar;
            goalBackgroundBarColorspan.style.backgroundColor = html_data_parse.progress_bar_background;
            goalBackgroundBarColorOpacity.value = html_data_parse.progress_bar_background_opacity;
            goalBackgroundColorspan.style.backgroundColor = html_data_parse.background_color;
            goalBackgroundBorderColorspan.style.backgroundColor = html_data_parse.background_border;


            DataIframeLinks = {
                "likes" : "http://127.0.0.1:7000/src/html/goal/likes/iframe.html",
                "follow" : "http://127.0.0.1:7000/src/html/goal/follow/iframe.html",
                "gift" : "http://127.0.0.1:7000/src/html/goal/gift/iframe.html",
                "share" : "http://127.0.0.1:7000/src/html/goal/share/iframe.html",
                "diamonds": "http://127.0.0.1:7000/src/html/goal/diamonds/iframe.html",
                "max_viewer" : "http://127.0.0.1:7000/src/html/goal/max_viewer/iframe.html"
            }

            GoalLinkInput.value = DataIframeLinks[goal_html_type.value]


            for (var key in DataIframeLinks) {

                if (key === goal_html_type.value) {
                    document.getElementById(`iframe-${key}-config`).hidden = false
                } else {
                    document.getElementById(`iframe-${key}-config`).hidden = true
                }
            }
            

        }


    } else if (type_id == 'select_event'){
        
        var goal_event = document.getElementById('goal-event');

        if (goal_event.value != 'double'){
            goal_add_div.hidden = false
        } else {
            goal_add_div.hidden = true
        }
    } else if (type_id == 'change'){
        document.getElementById('edit-goal-div').hidden = true
        document.getElementById('html_editor').hidden = true
    } else if (type_id == 'reset'){
        
        data = {
            type_id : type_id,
            goal_type : goal_type.value
        }
    
        var data_parse = JSON.stringify(data);
    
        var goal_data = await window.pywebview.api.tiktok_goal(data_parse);
    
    }
}

async function ttk_logs(type_id){
    
    var seletor = document.getElementById('ttk-events');
    var checker = document.getElementById('ttk-log-status');
    var button = document.getElementById('ttk-save-log');
    var input = document.getElementById('ttk-message-new');
    
    if (type_id == 'get'){

        data = {
            type_id : 'get',
            type_not : seletor.value,
        }

        var data = JSON.stringify(data);

        var log_message = await window.pywebview.api.tiktok_logs(data);
    
        if (log_message) {

            log_message_data = JSON.parse(log_message)

            button.removeAttribute("disabled");

            input.value = log_message_data.message;
            checker.checked = log_message_data.status == 1 ? true : false;
    
        }

    } else if (type_id == "save"){
        
        button.setAttribute("disabled", true);

        var status = checker.checked ? 1 : 0;
        
        data = {
            type_not : seletor.value,
            type_id : 'save',
            status : status,
            message : input.value
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_logs('save',data)
        input.value = '';

    }
}

async function points_config(type_id){

    var gift_points = document.getElementById('gift_points');
    var like_points = document.getElementById('like_points');
    var share_points = document.getElementById('share_points');
    var follow_points = document.getElementById('follow_points');

    if(type_id == 'get'){

        data = {
            type_id : type_id
        }

        var data_parse = await window.pywebview.api.points_config(JSON.stringify(data))

        if (data_parse){

            var data_parse = JSON.parse(data_parse);

            gift_points.value = data_parse.gift_points;
            like_points.value = data_parse.like_points;
            share_points.value = data_parse.share_points;
            follow_points.value = data_parse.follow_points;

        }

    } else if (type_id == 'save'){

        data = {
            type_id : type_id,
            gift_points: gift_points.value,
            like_points: like_points.value,
            share_points: share_points.value,
            follow_points: follow_points.value
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.points_config(formData)

    } else if (type_id == 'clear-points'){

        data = {
            type_id : type_id
        }

        window.pywebview.api.points_config(JSON.stringify(data))

    }
}

async function roles_config(type_id){

    var gift_role = document.getElementById('gift_role');
    var like_role = document.getElementById('like_role');
    var share_role = document.getElementById('share_role');

    if(type_id == 'get'){

        data = {
            type_id : type_id
        }

        var data_parse = await window.pywebview.api.roles_config(JSON.stringify(data))

        if (data_parse){

            var data_parse = JSON.parse(data_parse);

            gift_role.value = data_parse.gift_role;
            like_role.value = data_parse.like_role;
            share_role.value = data_parse.share_role;

        }

    } else if (type_id == 'save'){

        data = {
            type_id : type_id,
            gift_role : gift_role.value,
            like_role : like_role.value,
            share_role: share_role.value,
        }

        window.pywebview.api.roles_config(JSON.stringify(data));

    }
}

async function command_cost(type){
    
    var checkbox = document.getElementById(`command-cost-status-${type}`);

    if (checkbox.checked){
        document.getElementById(`command-costdiv-${type}`).hidden = false
    } else {
        document.getElementById(`command-costdiv-${type}`).hidden = true
    }

}

async function command_cost_get(type,value){
    
    if (value == 1){
        document.getElementById(`command-costdiv-${type}`).hidden = false
    } else {
        document.getElementById(`command-costdiv-${type}`).hidden = true
    }

}

async function rank_js(type_id){

    var rankStatusCheckbox = document.getElementById('rank-status');
    var rankIntervalInput = document.getElementById('rank-interval');
    
    var RankBackgroundTextInput = document.getElementById('rank-background-text');
    
    var RankTextTextInput = document.getElementById("rank-font-text");
    var RankTextSpan = document.getElementById("rank-font-span");

    var RankTextSize = document.getElementById("rank-text-size");
    var RankProfilepicSize = document.getElementById("rank-profilepic-size");

    var RankBackgroundOpacitySpan = document.getElementById('rank-background-span');
    var RankBackgroundOpacityRange = document.getElementById('rank-background-opacity');

    var rangeOpinner = document.getElementById('rangevaluesrankopacity');
    var rangePicinner = document.getElementById('rangevaluesrankpicsize');
    var rangeTxinner = document.getElementById('rangevaluesranktextsize');
    var rangeCardinner = document.getElementById('rangevaluesrankcardsize');
    
    var rangeRankMaxinner = document.getElementById('rangevaluesrankmax');

    var rankstatus = rankStatusCheckbox.checked;

    var rank_type = document.getElementById('rank-select');
    var rank_status_side = document.getElementById("rank-status-side");
    var rank_card_size = document.getElementById('rank-card-size');

    var rank_max_users = document.getElementById("rank-users-max");



    if (type_id == 'get'){

        data = {
            type_id : 'get',
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.ranks_config(data);
    
        if (rec) {

            rec_parse = JSON.parse(rec)

            rankStatusCheckbox.checked = rec_parse.status == 1  ? true : false;
            rankIntervalInput.value = rec_parse.interval;
            rank_max_users.value = rec_parse.max_users;
            rangeRankMaxinner.innerHTML = rec_parse.max_users;

            RankTextTextInput.value = rec_parse.font_color;
            RankTextSpan.style.backgroundColor = rec_parse.font_color;

            RankTextSize.value = rec_parse.font_size;
            RankProfilepicSize.value = rec_parse.image_size;
            rank_card_size.value = rec_parse.card_size;

            rank_status_side.checked = rec_parse.rank_side == 1 ? true : false;

            RankBackgroundTextInput.value = rec_parse.bg
            RankBackgroundOpacityRange.value = rec_parse.op;
            RankBackgroundOpacitySpan.style.backgroundColor = rec_parse.bg;

            rangeOpinner.innerHTML = rec_parse.op;
            rangePicinner.innerHTML = rec_parse.image_size;
            rangeTxinner.innerHTML = rec_parse.font_size;
            rangeCardinner.innerHTML = rec_parse.font_size;
            
            $("#rank-select").val(rec_parse.type_rank);

            if (rec_parse.type_rank == "card"){
                document.getElementById('rank-config-div').hidden = false
            } else {
                document.getElementById('rank-config-div').hidden = true
            }
        }

    } else if (type_id == 'save'){

        data = {
            type_id : 'save',
            status : rankstatus,
            interval : rankIntervalInput.value,
            max_users : rank_max_users.value,
        }

        var data = JSON.stringify(data);

        window.pywebview.api.ranks_config(data)

    } else if (type_id == 'save_rank'){
        
        var opacity = RankBackgroundOpacityRange.value;
        var background = RankBackgroundTextInput.value;
        var text = RankTextTextInput.value;
        var size = RankTextSize.value;
        var profilepic = RankProfilepicSize.value;
        var card_size = rank_card_size.value;
        var rank_side = rank_status_side.checked ? 1 : 0;
        var type_rank = rank_type.value;

        data = {
            type_id : 'save_rank',
            op: opacity,
            bg: background,
            font_color: text,
            font_size: size,
            image_size: profilepic,
            card_size: card_size,
            rank_side: rank_side,
            rank_type: type_rank,
        }

        var data = JSON.stringify(data);

        window.pywebview.api.ranks_config(data)

    } else if (type_id == 'change'){

        var type_config = document.getElementById('rank-select').value; 

        if (type_config == "card"){
            document.getElementById('rank-config-div').hidden = false
        
        } else {
            document.getElementById('rank-config-div').hidden = true
        }
    }
}

async function test_js(type_id){

    if (type_id == "edit_command"){

        var command = document.getElementById('command-select-edit');

        data ={
            type_id : 'comment',
            comment : command.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);
        
    } else if (type_id == "tts_command"){

        var command_input = document.getElementById('tts-command');
        command = `${command_input.value} Esta é uma mensagem de teste, siga o canal GG TEC`

        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "balance_command"){

        var command_input = document.getElementById('balance-command');
        var command_type = document.getElementById('command-balance-select');

        if (command_type.value == "mod_balance"){
            command = `${command_input.value} usuarioexemplo`
        } else if (command_type.value == "mod_balance_take"){
            command = `${command_input.value} usuarioexemplo 1000`
        }else if (command_type.value == "mod_balance_give"){
            command = `${command_input.value} usuarioexemplo 1000`
        } else {
            command = `${command_input.value}`
        }

        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "champ_command"){

        var command_input = document.getElementById('command-champ-command');
        var command_select = document.getElementById('command-camp-select');
        
        if (command_select.value == "add_camp" || command_select.value == "remove_camp"){
            command = `${command_input.value} usuarioexemplo`
        } else {
            command = `${command_input.value}`
        }

        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "votes_command"){

        var command = document.getElementById('vote-command-test');

        data ={
            type_id : 'comment',
            comment : command.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "giveaway_command"){

        var command_input = document.getElementById('command-giveaway-command');
        var command_type = document.getElementById('command-giveaway-select');

        if (command_type.value == "add_user" || command_type.value == "check_name"){
            command = `${command_input.value} usuarioexemplo`
        } else {
            command = command_input.value
        }

        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "queue_command"){
        
        var command_input = document.getElementById('command-queue-command');
        var command_type = document.getElementById('command-queue-select');

        if (command_type.value == "add_queue" || command_type.value == "rem_queue"){
            command = `${command_input.value} usuarioexemplo`
        } else {
            command = command_input.value
        }

        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "music_command"){

        var command_input = document.getElementById('command-player-command');
        var command_type = document.getElementById('command-player-edit');

        if (command_type.value == "request"){
            command = `${command_input.value} Rap Da Akatsuki: Os Ninjas Mais Procurados Do Mundo (Nerd Hits)`
        } else if (command_type.value == "volume") {
            command = `${command_input.value} 50`
        } else {
            command = `${command_input.value}`
        }
        
        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "subathon_command"){

        var command_input = document.getElementById('command-subathon-command');
        var command_type = document.getElementById('command-subathon-select');

        if (command_type.value == "add_minutes" || command_type.value == "remove_minutes"){
            command = `${command_input.value} 10`
        } else {
            command = command_input.value
        }

        data ={
            type_id : 'comment',
            comment : command
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);

    } else if (type_id == "goal"){

        var select_goal = document.getElementById('goal-select');
        var select_gift = document.getElementById('goal-gift');

        data ={
            type_id : 'goal',
            type_goal : select_goal.value,
            gift_id : select_gift.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.test_fun(formData);
    
    } else if (type_id == "like_alert"){

        data ={
            type_id : 'like_alert'
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.test_fun(formData);

    } else if (type_id == "share_alert"){

        data ={
            type_id : 'share_alert'
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.test_fun(formData);

    } else if (type_id == "follow_alert"){

        data ={
            type_id : 'follow_alert'
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.test_fun(formData);

    } else if (type_id == "test_sound_gift"){

        var gift_id_inp = document.getElementById('ttk-gift-id');

        data ={
            type_id : 'test_sound_gift',
            gift_id : gift_id_inp.value
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.test_fun(formData);

    } else if (type_id == "alerts_overlay"){

        data ={
            type_id : 'alerts_overlay'
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.test_fun(formData);

    } else if (type_id == "alerts_video_overlay"){

        data ={
            type_id : 'alerts_video_overlay'
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.test_fun(formData);

    }
}

async function subathon_modal(button){

    var id = button.getAttribute('data-id');
    var gift_id_inp = document.getElementById('subathon-gift-id');
    gift_id_inp.value = id
    subathon_js('modal')

}

async function subathon_js(type_id){

    if (type_id == "get"){

        data = {
            type_id : "get",
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.subathon(data);
    
        if (rec) {

            rec_data = JSON.parse(rec)
            
            var status = rec_data.status
            var time_global = rec_data.time_global
            var time_type = rec_data.time_type

            $("#subathon-time-type").selectpicker('val', time_type);
            $("#subathon-time-type").selectpicker("refresh");

            document.getElementById('time-global').value = time_global;
            
            var status_checkbox = document.getElementById('status-subathon');

            status_checkbox.checked = status ? true : false;

            var dataTableData = [];

            var gift_data = rec_data.gifts

            for (const key in gift_data) {

                if (gift_data.hasOwnProperty(key)) {

                    const item = gift_data[key];
                    
                    
                    var gift_id = key
                    var gift_name = item.name_br != "" ? item.name_br : item.name
                    var time = item.time

                    
                    var button_config = document.createElement("button");

                    button_config.innerText = "Configurar";
                    button_config.classList.add('bnt','bt-submit')
                    button_config.setAttribute('data-id', `${gift_id}`)
                    button_config.setAttribute('onclick', `subathon_modal(this)`)

                    dataTableData.push([
                        gift_name,
                        time,
                        button_config.outerHTML
                    ]);

                }
            }


            if ($.fn.DataTable.isDataTable("#giftlist_subathon_table")) {

                $('#giftlist_subathon_table').DataTable().clear().draw();
                $('#giftlist_subathon_table').DataTable().destroy();
            }

            var table = $('#giftlist_subathon_table').DataTable( {
                destroy: true,
                scrollX: true,
                scrollY: '300px',
                paging: false,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                },
                columns: [
                    { title: 'Nome' ,"searchable": true },
                    { title: 'Tempo' },
                    { title: 'Ação' }
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }
        }

    } else if (type_id == "modal"){

        var gift_name = document.getElementById('subathon-gift-name');
        var gift_time = document.getElementById('subathon-gift-time');
        var gift_status = document.getElementById('subathon-status');
        var gift_id_inp = document.getElementById('subathon-gift-id');

        data = {
            type_id : "get_gift_info",
            id : gift_id_inp.value
        }

        var data = JSON.stringify(data);

        var gift_data = await window.pywebview.api.subathon(data);

        if (gift_data){

            gift_rec_data = JSON.parse(gift_data)

            $("#gift-modal-subathon").modal("show");

            gift_name.innerHTML = gift_rec_data.name
            gift_time.value = gift_rec_data.time
            gift_status.checked = gift_rec_data.status_subathon ? true : false;

            document.getElementById('save-gift-subathon').setAttribute('onclick',`subathon_js('save_gift_info')`)
        }
    } else if (type_id == "save"){

        var globa0l = document.getElementById('time-global');
        var status_checkbox = document.getElementById('status-subathon');
        var time_type = document.getElementById('ssubathon-time-type');

        status = status_checkbox.checked ? 1 : 0;

        data = {
            type_id : "save",
            status : status,
            tume_type: time_type,
            time_global : globa0l.value
        }

        var data = JSON.stringify(data);
        window.pywebview.api.subathon(data);

    } else if (type_id == "save_command"){

        var command_subathon_select = document.getElementById('command-subathon-select');
        var command_subathon_status = document.getElementById('command-subathon-status');
        var command_subathon_command = document.getElementById('command-subathon-command');
        var command_subathon_delay = document.getElementById('command-subathon-delay');
        var command_subathon_cost_status = document.getElementById('command-cost-status-subathon'); 
        var command_subathon_cost = document.getElementById('command-cost-subathon');

        var command_subathon_whitelistStatus = document.getElementById('whitelist-status-subathon');

        var command_status = command_subathon_status.checked ? 1 : 0;
        var command_cost_status = command_subathon_cost_status.checked ? 1 : 0;
        var whitelist_status = command_subathon_whitelistStatus.checked ? 1 : 0;

        var roles = []; 

        $('#command-subathon-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data  = {
            type_id : type_id,
            type_command_table: 'subathon',
            type_command: command_subathon_select.value,
            command: command_subathon_command.value,
            status: command_status,
            delay: command_subathon_delay.value,
            user_level: roles,
            cost: command_subathon_cost.value,
            cost_status: command_cost_status,
            whitelist_status: whitelist_status
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.commands_default_py(formData)

        document.getElementById("command_subathon_form").hidden = true

    } else if (type_id == "get_command"){

        var command_subathon_select = document.getElementById('command-subathon-select');
        var command_subathon_status = document.getElementById('command-subathon-status');
        var command_subathon_command = document.getElementById('command-subathon-command');
        var command_subathon_delay = document.getElementById('command-subathon-delay');
        var command_subathon_cost_status = document.getElementById('command-cost-status-subathon'); 
        var command_subathon_cost = document.getElementById('command-cost-subathon');

        var command_subathon_whitelistStatus = document.getElementById('whitelist-status-subathon');

        var subathon_command_edit = document.getElementById('command_subathon_form');

        data = {
            type_id : type_id,
            type_command : command_subathon_select.value,
            type_command_table: 'subathon'
        }

        var subathon_parse = await window.pywebview.api.commands_default_py(data)

        if (subathon_parse){
            
            subathon_command_edit.hidden = false       

            command_cost_get('subathon',subathon_parse.cost_status)

            command_subathon_cost_status.checked = subathon_parse.cost_status == 1 ? true : false;
            command_subathon_status.checked = subathon_parse.status == 1 ? true : false;
            command_subathon_whitelistStatus.checked = subathon_parse.whitelist_status == 1 ? true : false;
            command_subathon_command.value = subathon_parse.command
            command_subathon_delay.value = subathon_parse.delay
            command_subathon_cost.value = subathon_parse.cost

            $("#command-subathon-perm").selectpicker('val',subathon_parse.user_level)
            $("#command-subathon-perm").selectpicker("refresh");

        }

    } else if (type_id == "save_gift_info"){

        var gift_name = document.getElementById('subathon-gift-name');
        var gift_time = document.getElementById('subathon-gift-time');
        var gift_status = document.getElementById('subathon-status');
        var gift_id_inp = document.getElementById('subathon-gift-id');

        data = {
            type_id : "save_gift_info",
            id : gift_id_inp.value,
            time : gift_time.value,
            status : gift_status.checked ? 1 : 0,
        }

        var data = JSON.stringify(data);

        window.pywebview.api.subathon(data);

        gift_status.checked = false
        gift_time.value = "00:00:00"
        gift_name.innerHTML = ""
        gift_id_inp.value = ""
        $("#gift-modal-subathon").modal("hide");

        data = {
            type_id : "get",
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.subathon(data);
    
        if (rec) {

            rec_data = JSON.parse(rec)
            
            var status = rec_data.status
            var minutes_global = rec_data.global_minutes

            var time_type = rec_data.time_type

            $("#subathon-time-type").selectpicker('val', time_type);
            $("#subathon-time-type").selectpicker("refresh");

            document.getElementById('global-minutes').value = minutes_global;
            
            var status_checkbox = document.getElementById('status-subathon');

            status_checkbox.checked = status ? true : false;

            var dataTableData = [];

            var gift_data = rec_data.gifts

            for (const key in gift_data) {

                if (gift_data.hasOwnProperty(key)) {

                    const item = gift_data[key];
                    
                    var gift_id = key
                    var gift_name = item.name_br != "" ? item.name_br : item.name
                    var time = item.time

                    
                    var button_config = document.createElement("button");

                    button_config.innerText = "Configurar";
                    button_config.classList.add('bnt','bt-submit')
                    button_config.setAttribute('data-id', `${gift_id}`)
                    button_config.setAttribute('onclick', `subathon_modal(this)`)

                    dataTableData.push([
                        gift_name,
                        time,
                        button_config.outerHTML
                    ]);

                }
            }


            if ($.fn.DataTable.isDataTable("#giftlist_subathon_table")) {

                $('#giftlist_subathon_table').DataTable().clear().draw();
                $('#giftlist_subathon_table').DataTable().destroy();
            }

            var table = $('#giftlist_subathon_table').DataTable( {
                destroy: true,
                scrollX: true,
                scrollY: '300px',
                paging: false,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
                },
                columns: [
                    { title: 'Nome', "searchable": true },
                    { title: 'Tempo' },
                    { title: 'Ação' }
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }
        }
        
    } else if (type_id == "add"){

        var value = document.getElementById('subathon-time').value;

        data = {
            type_id : "add",
            value : value,
        }

        var data = JSON.stringify(data);

        window.pywebview.api.subathon(data);

    } else if (type_id == "remove"){

        var value = document.getElementById('subathon-time').value;

        data = {
            type_id : "remove",
            value : value,
        }
        var data = JSON.stringify(data);

        window.pywebview.api.subathon(data);

    } else if (type_id == "reset"){

        var value = document.getElementById('subathon-time').value;

        data = {
            type_id : "reset",
            value : value,
        }
        var data = JSON.stringify(data);

        window.pywebview.api.subathon(data);

    } else if (type_id == "get_style"){

        var subathon_color1 = document.getElementById('subathon-color1-text');
        var subathon_color1_span = document.getElementById('subathon-color1-span');

        var subathon_color2 = document.getElementById('subathon-color2-text');
        var subathon_color2_span = document.getElementById('subathon-color2-span');

        var subathon_opacity = document.getElementById("subathon-background-opacity");

        data = {
            type_id : "get_style",
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.subathon(data);
    
        if (rec) {

            rec_data = JSON.parse(rec)
            
            var color1 = rec_data.color1
            var color2 = rec_data.color2
            var opacity = rec_data.opacity

            subathon_color1_span.style.backgroundColor = color1;
            subathon_color2_span.style.backgroundColor = color2;

            subathon_color1.value = color1;
            subathon_color2.value = color2;
            subathon_opacity.value = opacity;

        }
    } else if (type_id == "save_style"){

        var subathon_color1 = document.getElementById('subathon-color1-text');
        var subathon_color1_span = document.getElementById('subathon-color1-span');

        var subathon_color2 = document.getElementById('subathon-color2-text');
        var subathon_color2_span = document.getElementById('subathon-color2-span');

        var subathon_opacity = document.getElementById("subathon-background-opacity");

        data = {
            type_id : "save_style",
            color1 : subathon_color1.value,
            color2 : subathon_color2.value,
            opacity : subathon_opacity.value,

        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.subathon(data);
    }
}