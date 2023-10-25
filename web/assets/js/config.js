//CONFIG

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function config_responses_js(event,fun_id_responses) {

    event.preventDefault();

    var button_el = document.getElementById('submit-responses-config');
    var select_id_el = document.getElementById('response-select-edit').value;
    var in_reponse_el = document.getElementById('response-message-new');
    var aliases_responses = document.getElementById('aliases-responses');

    if (fun_id_responses == 'get_response'){

        var messages = await window.pywebview.api.responses_config('get_response',select_id_el,'none');
    
        if (messages) {

            button_el.removeAttribute("disabled");
            in_reponse_el.value = messages;
    
        }

        const responses_aliases_respo = {
            error_tts_disabled: "{username}",
            error_tts_no_text: "{username}",
            error_user_level: "{username},{user_level},{command}",
            giveaway_response_win: "{username}",
            giveaway_response_user_add: "{username}",
            giveaway_status_enable: "{giveaway_name}",
            giveaway_status_disable: "{giveaway_name}",
            giveaway_response_mult_add: "{username}",
            giveaway_clear: "",
            giveaway_response_perm: "{perm}",
            giveaway_status_disabled: "",
            response_user_giveaway: "{username}",
            response_no_user_giveaway: "{username}",
            response_giveaway_disabled: "",
            response_user_error_giveaway: "{username}",
            response_check_error_giveaway: "{username}",
            response_delay_error: "{seconds}",
            commands_disabled: "",
            command_disabled: "{username}",
            music_disabled: "{username}",
            music_added_to_queue: "{username},{music}",
            music_add_error: "{username}",
            music_process_error: "",
            music_process_cache_error: "",
            music_leght_error: "{max_duration}",
            music_playing: "{music_name},{music_artist},{username}",
            music_link_error: "",
            music_error_name: "",
            music_stream_error: "",
            music_link_youtube: "",
            command_sr_error_link: "{username}",
            command_volume_confirm: "{username},{volume}",
            command_volume_error: "{username}",
            command_skip_confirm: "{username}",
            command_current_confirm: "{username},{music}",
            command_next_no_music: "{username}",
            command_next_confirm: "{username},{music}",
            command_volume_number: "",
            command_volume_response: "{username},{volume}",
            command_value: "{username}",
            command_string: "{username}",
            music_blacklist: "{music}",
            cmd_created: "",
            cmd_edited: "",
            cmd_removed: "",
            cmd_use: "{command}",
            cmd_exists: "",
            cmd_not_exists: "",
            command_sufix: "{username}",
            response_queue: "{username}",
            response_add_queue: "{value}",
            response_namein_queue: "{value}",
            response_rem_queue: "{value}",
            response_noname_queue: "{value}",
            response_get_queue: "{username},{queue-3}",
            skip_votes: "{username},{votes},{minimum}",
            command_skip_inlist: "{username}",
            goal_start: "{current},{target},{type}",
            goal_end: "{current},{target},{type}",
            goal_progress: "{current},{target},{type}",
            command_skip_noplaying: "{username}",
            event_ttk_connect: "",
            event_ttk_envelope: "{username}",
            event_ttk_gift: "{username},{amount},{giftname},{diamonds}",
            event_ttk_join: "{username}",
            event_ttk_like: "{username}",
            event_ttk_share: "{username}",
            event_ttk_follow: "{username}",
            event_ttk_disconected: "",
        }

            
        aliases_responses.value = responses_aliases_respo[select_id_el];

        if (select_id_el in responses_aliases_respo) {
            aliases_responses.value = responses_aliases_respo[select_id_el];
          } else {
            aliases_responses.value = "{username}";
          }

    } else if (fun_id_responses == "save-response"){

        window.pywebview.api.responses_config('save_response',select_id_el,in_reponse_el.value)
        in_reponse_el = '';
    }
}

function show_config_div(div_id) {

    if (div_id == "config-chat-messages-div") {
        messages_config_js('get');
    } else if (div_id == "config-discord-div") {
        discord_js('event','get-profile');
    } else if (div_id == "config-music-div"){
        sr_config_js('event','get')
    } else if (div_id == "chat-config-div"){
        chat_config('get')
    } else if (div_id == "events-config-div"){
        event_log_config('get')
    }

    document.getElementById("config-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_config_div(div_id, modal) {
    $("#" + modal).modal("hide");
    document.getElementById("config-div").hidden = false;
    document.getElementById(div_id).hidden = true;
}

function slider_font_events() {
    slider = document.getElementById('slider-font-events');
    output = document.getElementById('rangevalue_config_events');
    $('.chat-message ').css("font-size", slider.value + "px");
    output.innerHTML = slider.value
};

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

    } else if (type_id == 'get_command'){

        var select_command_player = document.getElementById('command-player-edit');

        var form_player = document.getElementById('command_player_form');
        var command_player_command = document.getElementById('command-player-command');
        var command_player_status = document.getElementById('command-player-status');
        var command_player_delay = document.getElementById('command-player-delay');

        var command_data_parse = await window.pywebview.api.sr_config_py(type_id,select_command_player.value)

        if (command_data_parse){

            command_data_parse = JSON.parse(command_data_parse)

            form_player.hidden = false

            command_player_command.value = command_data_parse.command
            command_player_status.checked = command_data_parse.status == 1 ? true : false
            command_player_delay.value = command_data_parse.delay

            $("#command-player-perm").selectpicker('val', command_data_parse.user_level);
            $("#command-player-perm").selectpicker("refresh");

        }

    } else if (type_id == 'save_command') {

        var select_command_player = document.getElementById('command-player-edit');

        var form_player = document.getElementById('command_player_form');
        
        var command_player_command = document.getElementById('command-player-command');
        var command_player_status = document.getElementById('command-player-status');
        var command_player_delay = document.getElementById('command-player-delay');

        var roles = []; 

        $('#command-player-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_command : select_command_player.value,
            command: command_player_command.value,
            delay: command_player_delay.value,
            user_level: roles,
            status: command_player_status = command_player_status.checked ? 1 : 0
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.sr_config_py(type_id,formData);

    } else if (type_id == 'save'){

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

function setElementState(elementId, value) {

    var element = document.getElementById(elementId);

    if (element) {

      if (element.type === "checkbox") {

        element.checked = value === 1;

      } else if (element.tagName === "SELECT") {

        $("#" + elementId).selectpicker('val', value);

      } else if (element.tagName === "INPUT" && element.type === "range") {

        element.value = value;

      }
    }
}

async function get_event_state(element){

    data ={
        "type_id" : 'get_state',
        "type" : element.value
    };

    var event_data = await window.pywebview.api.event_log(JSON.stringify(data))

    if (event_data){

        document.getElementById('select-show').hidden = false

        data_parse = JSON.parse(event_data)
        
        console.log(data_parse)
        setElementState('show-event',data_parse["show-event"])
        setElementState('show-event-chat',data_parse["show-event-chat"])
        setElementState('show-event-html',data_parse["show-event-html"])

    }
}   

async function event_log_config(type_id){

    var font_size_range = document.getElementById('rangevalue_config_events');

    var sliderFontEvents = document.getElementById("slider-font-events");
    var colorEvents = document.getElementById("color-events");
    var dataShowEvents = document.getElementById("data-show-events");

    if (type_id == 'save'){

        data = {}
        data["type_id"] = type_id;
        data["slider-font-events"] = sliderFontEvents.value;
        data["color-events"] = colorEvents.value;
        data["data-show-events"] = dataShowEvents.value;

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
        }

    } else if (type_id == 'save_state'){
        
        element = document.getElementById('select-event-type');
        data = {}
        data["type_id"] = type_id;
        data["type"] = element.value;
        data["show-event"] = document.getElementById('show-event').checked ? 1 : 0;
        data["show-event-chat"] = document.getElementById('show-event-chat').checked ? 1 : 0;;
        data["show-event-html"] = document.getElementById('show-event-html').checked ? 1 : 0;;

        window.pywebview.api.event_log(JSON.stringify(data));

    }


}

async function show_error_log(type_id){

    if (type_id == 'get-errorlog'){

        $("#errorlog-modal").modal("show");

        $('#errorlog-textarea').val('');

        var errors_data = await window.pywebview.api.open_py('errolog','null')
    
        if (errors_data){
    
            var textarea = document.getElementById('errorlog-textarea');
    
            $('#errorlog-textarea').val(errors_data);
            
            textarea.scrollTop = textarea.scrollHeight;
        }

    } else if (type_id == 'clear-errorlog'){

        $("#errorlog-modal").modal("hide");
        $('#errorlog-textarea').val('');

        window.pywebview.api.open_py('errolog_clear','null')

    }

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
    }

}

async function ttk_alerts(type){

    var follow_input_sound = document.getElementById('file-select-ttk-follow');
    var follow_status_sound = document.getElementById('ttk-sound-status-follow');
    var follow_volume_sound = document.getElementById('audio-volume-ttk-follow');

    var like_input_sound = document.getElementById('file-select-ttk-like');
    var like_status_sound = document.getElementById('ttk-sound-status-like');
    var like_volume_sound = document.getElementById('audio-volume-ttk-like');
    
    var like_delay = document.getElementById('ttk-like-delay');

    var share_input_sound = document.getElementById('file-select-ttk-share');
    var share_status_sound = document.getElementById('ttk-sound-status-share');
    var share_volume_sound = document.getElementById('audio-volume-ttk-share');
    
    var share_delay = document.getElementById('ttk-share-delay');
    
    
    if (type == 'get'){

        data = {
            type_id : type,
        }

        var data = JSON.stringify(data);

        var data_re = await window.pywebview.api.tiktok_alerts(data);
    
        if (data_re) {

            rec_data = JSON.parse(data_re)

            follow_status_sound.checked = rec_data.follow_sound_status == 1 ? true : false;
            follow_volume_sound.value = rec_data.follow_sound_volume;
            follow_input_sound.value = rec_data.follow_sound_loc;

            like_delay.value = rec_data.like_delay;
            like_status_sound.checked = rec_data.like_sound_status == 1 ? true : false;
            like_volume_sound.value = rec_data.like_sound_volume;
            like_input_sound.value = rec_data.like_sound_loc;

            share_delay.value = rec_data.share_delay;
            share_status_sound.checked = rec_data.share_sound_status == 1 ? true : false;
            share_volume_sound.value = rec_data.share_sound_volume;
            share_input_sound.value = rec_data.share_sound_loc;
    
        }

    } else if (type == "save_sound_follow"){
        
        var status_sound = follow_status_sound.checked ? 1 : 0;

        data = {
            type_id : "save_sound_follow",
            sound: status_sound,
            sound_loc : follow_input_sound.value,
            sound_volume : follow_volume_sound.value,
            delay : like_delay.value 
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_config(data)
        
    } else if (type == "save_sound_like"){
        
        var status_sound = status_sound_like.checked ? 1 : 0;

        data = {
            type_id : "save_sound_like",
            sound: status_sound,
            sound_loc : like_input_sound.value,
            sound_volume : like_volume_sound.value 
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_config(data)
        
    } else if (type == "save_sound_share"){
        
        var status_sound = status_sound_share.checked ? 1 : 0;

        data = {
            type_id : "save_sound_share",
            sound: status_sound,
            sound_loc : share_input_sound.value,
            sound_volume : share_volume_sound.value 
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_config(data)
    }
}

function ttk_modal(button){

    var id = button.getAttribute('data-id');
    var gift_id_inp = document.getElementById('ttk-gift-id');
    gift_id_inp.value = id
    ttk_gift('modal')

}

async function ttk_gift(type_id){

    if (type_id == "get"){

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
                    
                    var gift_name = item.name
                    var gift_name_br = item.name_br
                    var diamonds = item.value
                    
                    var button_config = document.createElement("button");

                    button_config.innerText = "Configurar";
                    button_config.classList.add('bnt','bt-submit')
                    button_config.setAttribute('data-id', `${gift_name}`)
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

            var global_gift_status = document.getElementById('global-gift-status');
            var global_gift_volume = document.getElementById('global-gift-volume');
            var global_gift_sound = document.getElementById('global-gift-sound');

            global_gift_status.checked = rec_data.status == 1 ? true : false;
            global_gift_sound.value = rec_data.sound;
            global_gift_volume.value = rec_data.volume;
        }
        
    } else if (type_id == "modal"){

        var gift_sound = document.getElementById('file-select-sound-gift');
        var gift_status = document.getElementById('gift-sound-status');
        var gift_volume_sound = document.getElementById('audio-volume-ttk-gift');
        var gift_id_inp = document.getElementById('ttk-gift-id');

        data = {
            type_id : "get_gift_info",
            id : gift_id_inp.value
        }

        var data = JSON.stringify(data);

        var gift_data = await window.pywebview.api.tiktok_gift(data);

        if (gift_data){

            gift_rec_data = JSON.parse(gift_data)

            $("#gift-modal").modal("show");

            gift_sound.value = gift_rec_data.audio
            gift_status.checked = gift_rec_data.status == 1 ? true : false;
            gift_volume_sound.value = gift_rec_data.volume;

            document.getElementById('save-gift-notification').setAttribute('onclick',`ttk_gift('save_sound_gift')`)
        }

        
        
    } else if (type_id == "save_sound_gift"){ 

        var gift_sound = document.getElementById('file-select-sound-gift')
        var gift_status = document.getElementById('gift-sound-status')
        var gift_volume_sound = document.getElementById('audio-volume-ttk-gift')

        var gift_status = gift_status.checked ? 1 : 0;

        var gift_id_inp = document.getElementById('ttk-gift-id');

        data = {
            type_id : "save_sound_gift",
            id : gift_id_inp.value,
            status: gift_status,
            sound_loc : gift_sound.value,
            sound_volume : gift_volume_sound.value 
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tiktok_gift(data)
        gift_id_inp.value = ''

    } else if (type_id == "global_gift_save"){

        var global_gift_status = document.getElementById('global-gift-status');
        var global_gift_volume = document.getElementById('global-gift-volume');
        var global_gift_sound = document.getElementById('global-gift-sound');

        data = {
            type_id : "global_gift_save",
            status : global_gift_status.checked ? 1 : 0,
            volume : global_gift_volume.value,
            sound : global_gift_sound.value,
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
    
            status_goal.checked = goal_data.status == 1 ? true : false;
            goal_sound_status.checked = goal_data.status_sound == 1 ? true : false;
    
            document.getElementById('goal').value = goal_data.goal;
            document.getElementById('file-select-ttk-goal-sound').value = goal_data.sound_file;
            document.getElementById('audio-volume-ttk-goal-sound').value = goal_data.sound_volume;

            if (goal_data.goal_add != ""){

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
                sound_volume: goal_sound_volume.value
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
                sound_volume: goal_sound_volume.value
            }
        }

        var data_parse = JSON.stringify(data);
        window.pywebview.api.tiktok_goal(data_parse);

        goal_add_div.hidden = true
        edit_goal_div.hidden = true
        document.getElementById("goal-gift-select").hidden = true;

    } else if (type_id == 'save_html'){

        var iframe = document.getElementById('iframe-bar');

        var goalText = document.getElementById("goal-text");
        var goalTextColorInput = document.getElementById("goal-text-color-text");
        var goalBarColorInput = document.getElementById("goal-bar-color-text");
        var goalBackgroundBarColorInput = document.getElementById("goal-background-bar-color-text");
        var goalBackgroundColorInput = document.getElementById("goal-background-color-text");

        var goalTextColorspan = document.getElementById("goal-text-color-span");
        var goalBarColorspan = document.getElementById("goal-bar-color-span");
        var goalBackgroundBarColorspan = document.getElementById("goal-background-bar-color-span");
        var goalBackgroundColorspan = document.getElementById("goal-background-color-span");

        
        data = {
            type_id : type_id,
            type_goal : goal_html_type.value,
            text_value : goalText.value,
            text_color : goalTextColorInput.value,
            bar_color: goalBarColorInput.value,
            background_bar_color: goalBackgroundBarColorInput.value,
            outer_color : goalBackgroundColorInput.value
        }

        var data_parse = JSON.stringify(data);

        res_html = await window.pywebview.api.tiktok_goal(data_parse);

        iframe.src = `${res_html}ts=${new Date().getTime()}`


    } else if (type_id == 'get_html'){

        var iframe = document.getElementById('iframe-bar');
        
        var goalText = document.getElementById("goal-text");

        var goalTextColorInput = document.getElementById("goal-text-color-text");
        var goalBarColorInput = document.getElementById("goal-bar-color-text");
        var goalBackgroundBarColorInput = document.getElementById("goal-background-bar-color-text");
        var goalBackgroundColorInput = document.getElementById("goal-background-color-text");

        var goalTextColorspan = document.getElementById("goal-text-color-span");
        var goalBarColorspan = document.getElementById("goal-bar-color-span");
        var goalBackgroundBarColorspan = document.getElementById("goal-background-bar-color-span");
        var goalBackgroundColorspan = document.getElementById("goal-background-color-span");

        var GoalLinkInput = document.getElementById("iframe-link");
        
        data = {
            type_id : type_id,
            type_goal : goal_html_type.value
        }
    
        var data_parse = JSON.stringify(data);
        
        var html_data = await window.pywebview.api.tiktok_goal(data_parse);
    
        if (html_data){

            html_data_parse = JSON.parse(html_data)

            document.getElementById('html_editor').hidden = false

            goalText.value = html_data_parse.title_text_value;

            goalTextColorInput.value = html_data_parse.title_text;
            goalBarColorInput.value = html_data_parse.progress_bar;
            goalBackgroundBarColorInput.value = html_data_parse.progress_bar_background;
            goalBackgroundColorInput.value = html_data_parse.outer_bar;

            goalTextColorspan.style.backgroundColor = html_data_parse.title_text;
            goalBarColorspan.style.backgroundColor = html_data_parse.progress_bar;
            goalBackgroundBarColorspan.style.backgroundColor = html_data_parse.progress_bar_background;
            goalBackgroundColorspan.style.backgroundColor = html_data_parse.outer_bar;

            DataIframeLinks = {
                "likes" : "http://127.0.0.1:7000/src/html/goal/likes/iframe.html",
                "follow" : "http://127.0.0.1:7000/src/html/goal/follow/iframe.html",
                "gift" : "http://127.0.0.1:7000/src/html/goal/gift/iframe.html",
                "share" : "http://127.0.0.1:7000/src/html/goal/share/iframe.html",
                "diamonds": "http://127.0.0.1:7000/src/html/goal/diamonds/iframe.html",
                "max_viewer" : "http://127.0.0.1:7000/src/html/goal/max_viewer/iframe.html"
            } 

            iframe.src = `${DataIframeLinks[goal_html_type.value]}?ts=${new Date().getTime()}`

            GoalLinkInput.value = DataIframeLinks[goal_html_type.value]
        }


    } else if (type_id == 'select_event'){
        
        var goal_event = document.getElementById('goal-event');

        if (goal_event.value == 'add'){
            goal_add_div.hidden = false
        } else {
            goal_add_div.hidden = true
        }
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

async function tts_command(type_id){

    var command = document.getElementById('tts-command');
    var delay = document.getElementById('tts-delay');
    var status = document.getElementById('command-tts-status');

    if (type_id == 'get'){

        data = {
            type_id : 'get',
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.tts_command(data);
    
        if (rec) {

            rec_parse = JSON.parse(rec)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;

            $("#user-level-tts").selectpicker('val', rec_parse.user_level);
            $("#user-level-tts").selectpicker("refresh");
    
        }

    } else if (type_id == "save"){
        
        var status = status.checked ? 1 : 0;
        
        var roles = []; 

        $('#user-level-tts :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : 'save',
            status : status,
            command : command.value,
            delay: delay.value,
            roles: roles
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tts_command(data)

    }
}

function show_userdata_modal(){
    $("#userdata-modal").modal("show");
    userdata_js('get')
}

