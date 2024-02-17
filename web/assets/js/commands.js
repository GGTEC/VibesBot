//COMANDOS

function show_commands_div(div_id) {

    if (div_id == "del-commands-div") {
        commands_fun('get_list');
    } else if (div_id == "edit-commands-div") {
        commands_fun('get_list');
    } else if (div_id ==  'default-commands-div'){
        champ_command('get');
    } else if (div_id == 'vote-commands-div'){
        votes('get_command')
    }
    document.getElementById("commands-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_commands_div(div_id, modal) {

    $("#" + modal).modal("hide");
    document.getElementById("commands-div").hidden = false;
    document.getElementById(div_id).hidden = true;

}

async function music_commands(type_id){

    if (type_id == 'get_command'){

        var select_command_player = document.getElementById('command-player-edit');

        var form_player = document.getElementById('command_player_form');
        var command_player_command = document.getElementById('command-player-command');
        var command_player_status = document.getElementById('command-player-status');
        var command_player_delay = document.getElementById('command-player-delay');
        var command_player_cost_status = document.getElementById('command-cost-status-player'); 
        var command_player_cost = document.getElementById('command-cost-player');

        var command_player_whitelistStatus = document.getElementById('whitelist-status-player');

        data = {
            type_id : type_id,
            type_command : select_command_player.value,
            type_command_table: 'player'
        }

        var command_data_parse = await window.pywebview.api.commands_default_py(data)

        if (command_data_parse){

            form_player.hidden = false

            command_cost_get('player',command_data_parse.cost_status)

            command_player_command.value = command_data_parse.command
            command_player_status.checked = command_data_parse.status == 1 ? true : false
            command_player_cost_status.checked = command_data_parse.cost_status == 1 ? true : false;
            command_player_whitelistStatus.checked = command_data_parse.whitelist_status == 1 ? true : false;
            command_player_delay.value = command_data_parse.delay
            command_player_cost.value = command_data_parse.cost;

            $("#command-player-perm").selectpicker('val', command_data_parse.user_level);
            $("#command-player-perm").selectpicker("refresh");

        }

    } else if (type_id == 'save_command') {

        var select_command_player = document.getElementById('command-player-edit');

        var form_player = document.getElementById('command_player_form');

        var command_player_command = document.getElementById('command-player-command');
        var command_player_status = document.getElementById('command-player-status');
        var command_player_delay = document.getElementById('command-player-delay');
        var command_player_cost_status = document.getElementById('command-cost-status-player');
        var command_player_cost = document.getElementById('command-cost-player');
        var command_player_whitelistStatus = document.getElementById('whitelist-status-player');

        var roles = []; 

        $('#command-player-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        var whitelist_status = command_player_whitelistStatus.checked ? 1 : 0
        var command_player_cost_status = command_player_cost_status.checked ? 1 : 0
        var command_player_status = command_player_status.checked ? 1 : 0

        data = {
            type_id : type_id,
            type_command : select_command_player.value,
            type_command_table: 'player',
            command: command_player_command.value,
            delay: command_player_delay.value,
            user_level: roles,
            status:command_player_status,
            cost: command_player_cost.value,
            cost_status: command_player_cost_status,
            whitelist_status: whitelist_status
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.commands_default_py(formData);

        document.getElementById("command_player_form").hidden = true

    } else if (type_id == 'hideconfig'){

        document.getElementById("command_player_form").hidden = true

    }
}

async function commands_fun(type_id){

    if (type_id == 'create'){

        
        var seletor_edit = document.getElementById('type-command-create');

        var cost = document.getElementById('command-cost-create'); 
        var cost_status = document.getElementById("command-cost-status-create");
        var cost_status = cost_status.checked ? 1 : 0;

        var key_status_el = document.getElementById('command-keys-status-create')
        var key_status = key_status_el.checked ? 1 : 0;

        var time_key = document.getElementById('time-key');
        var key1 = document.getElementById("key-1-create");
        var key2 = document.getElementById("key-2-create");
        var key3 = document.getElementById("key-3-create");
        var key4 = document.getElementById("key-4-create");

        var keys_list = [key1.value, key2.value, key3.value, key4.value]

        var whitelist_status_che = document.getElementById("whitelist-status");
        
        
        var roles = []; 

        $('#user-level-command :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        var response = document.getElementById('new-command-response').value

        response == null ? response = 'None' : response = response;

        data = {
            type_id : type_id,
            type: seletor_edit.value,
            command: document.getElementById('new-command').value,
            response: response,
            delay: document.getElementById('new-delay').value,
            user_level: roles,
            sound: document.getElementById('sound-command').value,
            volume: document.getElementById('audio-volume-command').value,
            video: document.getElementById('video-command').value,
            video_time: document.getElementById('time-video-command').value,
            whitelist_status :  whitelist_status_che.checked ? 1 : 0,
            cost: cost.value,
            cost_status: cost_status,
            keys_status: key_status,
            keys: keys_list,
            time_key: time_key.value
        };
    
        var formData = JSON.stringify(data);

        window.pywebview.api.commands_py(formData);

        document.getElementById('new-command').value = '';
        document.getElementById('sound-command').value = '';
        document.getElementById('new-command-response').value = '';

    } else if (type_id == 'edit'){

        var seletor_edit = document.getElementById('type-command-edit');
        var status_command = document.getElementById('command-simple-status');
        var command = document.getElementById('command-select-edit');
        var new_command = document.getElementById('edit-command');
        var sound = document.getElementById('sound-command-edit').value;
        var video = document.getElementById('video-command-edit').value;
        var video_time = document.getElementById('time-video-command-edit').value;
        var volume = document.getElementById('audio-volume-command-edit').value;
        var response = document.getElementById('edit-command-response');
        var delay = document.getElementById('edit-delay');

        var time_key = document.getElementById('time-key-edit');

        var cost = document.getElementById('command-cost-edit'); 
        var cost_status = document.getElementById("command-cost-status-edit");

        var key_status_el = document.getElementById('command-keys-status-edit')
        var key_status = key_status_el.checked ? 1 : 0;

        var key1 = document.getElementById("key-1-edit");
        var key2 = document.getElementById("key-2-edit");
        var key3 = document.getElementById("key-3-edit");
        var key4 = document.getElementById("key-4-edit");
        var keys_list = [key1.value, key2.value, key3.value, key4.value]

        var whitelist_status_che_edit = document.getElementById("whitelist-status-edit");
        
        var div = document.getElementById('div-edit-selected');

        var type = seletor_edit.value

        var status_command = status_command.checked ? 1 : 0;
        var cost_status = cost_status.checked ? 1 : 0;

        var roles = []; 

        $('#user-level-command-edit :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        response == null ? response = 'None' : response = response;

        data = {
            type_id : type_id,
            type: type,
            status_command: status_command,
            command: command.value,
            new_command: new_command.value,
            response: response.value,
            delay: delay.value,
            sound: sound,
            volume: volume,
            video: video,
            video_time: video_time,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status,
            keys_status: key_status,
            keys: keys_list,
            time_key: time_key.value,
            whitelist_status :  whitelist_status_che_edit.checked ? 1 : 0,
        };

        var formData = JSON.stringify(data);
        window.pywebview.api.commands_py(formData);

        div.hidden = true

        data = {
            type_id : 'get_list',
        };

        var formData = JSON.stringify(data);

        var list_command_parse = await window.pywebview.api.commands_py(formData);

        if (list_command_parse) {
            
            list_command_parse = JSON.parse(list_command_parse)

            $("#command-select-del").empty();
            $("#command-select-del").selectpicker("refresh");
            $("#command-select-edit").empty();
            $("#command-select-edit").selectpicker("refresh");
    
    
            for (var i = 0; i < list_command_parse.length; i++) {
                var optn = list_command_parse[i];
    
                $("#command-select-del").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-del").selectpicker("refresh");
                $("#command-select-edit").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-edit").selectpicker("refresh");
            }
        }

    } else if (type_id == 'delete'){

        data = {
            type_id : type_id,
            type: '',
            command: document.getElementById('command-select-del').value
        };

        var formData = JSON.stringify(data);
        window.pywebview.api.commands_py(formData);

        $("#command-select-del option:selected").remove();
        $("#command-select-del").selectpicker("refresh");

    } else if (type_id == 'get_list'){

        data = {
            type_id : type_id,
        };

        var formData = JSON.stringify(data);

        var list_command_parse = await window.pywebview.api.commands_py(formData);

        if (list_command_parse) {

            list_command_parse = JSON.parse(list_command_parse)

            $("#command-select-del").empty();
            $("#command-select-del").selectpicker("refresh");
            $("#command-select-edit").empty();
            $("#command-select-edit").selectpicker("refresh");
    
            for (var i = 0; i < list_command_parse.length; i++) {

                var optn = list_command_parse[i];
    
                $("#command-select-del").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-edit").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');

            }

            $("#command-select-del").selectpicker("refresh");
            $("#command-select-edit").selectpicker("refresh");
        }

    } else if (type_id == 'get_info'){

        var seletor_edit = document.getElementById('type-command-edit');
        var status = document.getElementById('command-simple-status');
        var command = document.getElementById('command-select-edit');
        var new_command = document.getElementById('edit-command');
        var sound = document.getElementById('sound-command-edit').value;
        var volume = document.getElementById('audio-volume-command-edit').value;
        var video = document.getElementById('video-command-edit');
        var time_video = document.getElementById('time-video-command-edit');
        var response = document.getElementById('edit-command-response');
        var delay = document.getElementById('edit-delay');

        var cost = document.getElementById('command-cost-edit'); 
        var cost_status_seletor = document.getElementById("command-cost-status-edit");
        
        var key_status = document.getElementById('command-keys-status-edit');

        var key1 = document.getElementById("key-1-edit");
        var key2 = document.getElementById("key-2-edit");
        var key3 = document.getElementById("key-3-edit");
        var key4 = document.getElementById("key-4-edit");

        var time_key = document.getElementById('time-key-edit');

        var div = document.getElementById('div-edit-selected');

        var type = seletor_edit.value

        var roles = []; 

        $('#user-level-command-edit :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : type_id,
            command : command.value
        };

        var formData = JSON.stringify(data);

        var command_info_parse = await window.pywebview.api.commands_py(formData);

        if (command_info_parse) {
            
            command_info_parse = JSON.parse(command_info_parse)

            div.hidden = false
            
            var response = command_info_parse.edit_response;
            var status_command = command_info_parse.status;
            var command_edit = command_info_parse.edit_command;
            var type_edit = command_info_parse.edit_type;
            var delay_edit = command_info_parse.edit_delay;
            var sound_edit = command_info_parse.edit_sound;
            var volume_edit = command_info_parse.edit_volume;
            var video_edit = command_info_parse.edit_video;
            var time_video_edit = command_info_parse.edit_video_time;
            var edit_level = command_info_parse.edit_level;
            var cost_status = command_info_parse.edit_cost_status;
            var edit_cost = command_info_parse.edit_cost;
            var key_status_r = command_info_parse.edit_keys_status;
            var time_key_r = command_info_parse.edit_time_key;
            var whitelist_status_edit = command_info_parse.edit_whitelist_status;

            var key1 = command_info_parse.edit_keys[0];
            var key2 = command_info_parse.edit_keys[1];
            var key3 = command_info_parse.edit_keys[2];
            var key4 = command_info_parse.edit_keys[3];

            var whitelist_status_edit = document.getElementById("whitelist-status-edit");

            whitelist_status_edit.checked = whitelist_status_edit == 1 ? true : false;
            key_status.checked = key_status_r == 1 ? true : false;

            document.getElementById('key_press_edit').hidden = key_status_r == 1 ? false : true;

            status.checked = status_command == 1 ? true : false;
            cost_status_seletor.checked = cost_status == 1 ? true : false;

            cost.value = edit_cost;

            command_cost_get('edit',cost_status)



            document.getElementById('edit-command-response').value = response;
            document.getElementById('sound-command-edit').value = sound_edit;
            document.getElementById('audio-volume-command-edit').value = volume_edit;

            document.getElementById("edit-command").value = command_edit;
            document.getElementById("edit-delay").value = delay_edit;

            video.value = video_edit
            time_video.value = time_video_edit

            $("#key-1-edit").selectpicker('val', key1);
            $("#key-1-edit").selectpicker("refresh");

            $("#key-2-edit").selectpicker('val', key2);
            $("#key-2-edit").selectpicker("refresh");

            $("#key-3-edit").selectpicker('val', key3);
            $("#key-3-edit").selectpicker("refresh");

            $("#key-4-edit").selectpicker('val', key4);
            $("#key-4-edit").selectpicker("refresh");

            time_key.value = time_key_r

            $("#type-command-edit").selectpicker('val', type_edit);
            $("#type-command-edit").selectpicker("refresh");

            $("#user-level-command-edit").selectpicker('val', edit_level);
            $("#user-level-command-edit").selectpicker("refresh");

            command_type_select('edit')

        }
    } else if (type_id == 'command-list'){

        $("#list-comands-modal").modal("show");

        data = {
            type_id : type_id
        };

        var command_list_parse = await window.pywebview.api.commands_py(JSON.stringify(data))

        if (command_list_parse) {
            
            command_list_parse = JSON.parse(command_list_parse);
          
            function processCommandList(commandList, type) {

              const dataTableData = [];
                
              for (const key in commandList) {

                if (commandList.hasOwnProperty(key)) {

                    const item = commandList[key];

                    const lastUse = item.last_use != "" ? new Date(item.last_use * 1000).toLocaleString() : "Nunca";
                    const status = item.status != "" ? (item.status === 1 ? "Ativado" : "Desativado") : "Desativado";
                    const delay = item.delay != "" ? item.delay : "Null";
                    const command = item.hasOwnProperty("command") ? item.command : key
                    const userLevel = item.user_level;

                    let userLevelstring = '';

                    if (Array.isArray(userLevel)) {

                        userLevel.forEach((level, index) => {

                            userLevelstring += level;
                            
                            if (index < userLevel.length - 1) {
                                userLevelstring += ', ';
                            }
                        });
                    } else {
                        userLevelstring = item.user_level;;
                    }


                    dataTableData.push([
                        command,
                        type,
                        lastUse,
                        status,
                        delay,
                        userLevelstring
                    ]);
                }
              }
          
              return dataTableData;
            }

            const commandData = processCommandList(command_list_parse.commands[0], "Simples");
            const queueData = processCommandList(command_list_parse.commands_queue[0], "Fila");
            const giveawayData = processCommandList(command_list_parse.commands_giveaway[0], "Sorteio");
            const playerData = processCommandList(command_list_parse.commands_player[0], "Player");
            const ttsData = processCommandList(command_list_parse.commands_tts[0], "TTS");
            const balanceData = processCommandList(command_list_parse.commands_balance[0], "Saldo");
            const champData = processCommandList(command_list_parse.commands_champ[0], "Campeonato");
            const votesData = processCommandList(command_list_parse.commands_votes[0], "Votos");
            const subathonData = processCommandList(command_list_parse.commands_subathon[0], "Subathon");


            if ($.fn.DataTable.isDataTable("#commandlist_table")) {
              $('#commandlist_table').DataTable().clear().draw();
              $('#commandlist_table').DataTable().destroy();
            }
          
            const table = $('#commandlist_table').DataTable({
              destroy: true,
              scrollX: true,
              paging: true,
              ordering: true,
              retrieve: false,
              processing: true,
              responsive: false,
              lengthMenu: [
                [10, 25, 50, -1],
                [10, 25, 50, 'All'],
              ],
              language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
              },
              columns: [
                { title: 'Comando' },
                { title: 'Tipo' },
                { title: 'Último uso' },
                { title: 'Status' },
                { title: 'Delay' },
                { title: 'Nível do usuário' }
              ]
            });

          
            // Adicionar as linhas à tabela
            [commandData, queueData, giveawayData, playerData, ttsData, balanceData, champData, votesData, subathonData].forEach(data => {
              data.forEach(row => {
                table.row.add(row).draw();
              });
            });
          }
    }
}

function command_type_select(type_id){

    if(type_id == 'create'){

        var seletor_create = document.getElementById('type-command-create');
        var div_audio_create = document.getElementById('command-audio-div');
        var div_video_create = document.getElementById('command-video-div')
        var input_text = document.getElementById('new-command-response-div');    
        var input_aliases = document.getElementById('new-command-response-prefix-div');
        
        if (seletor_create.value == "audio"){

            div_audio_create.hidden = false 
            input_text.hidden = true 
            input_aliases.hidden = true 

        } else if  (seletor_create.value == "audiotext"){

            div_audio_create.hidden = false 
            input_text.hidden = false 
            input_aliases.hidden = false 

        } else if (seletor_create.value == "video"){

            div_video_create.hidden = false 
            input_text.hidden = true 
            input_aliases.hidden = true 

        } else if  (seletor_create.value == "videotext"){

            div_video_create.hidden = false 
            input_text.hidden = false 
            input_aliases.hidden = false 

        } else if  (seletor_create.value == "tts"){

            div_audio_create.hidden = true 
            input_text.hidden = false 
            input_aliases.hidden = false 

        } else if  (seletor_create.value == "text"){

            div_audio_create.hidden = true 
            input_text.hidden = false 
            input_aliases.hidden = false 

        }

    } else if(type_id == 'edit'){

        var seletor_edit = document.getElementById('type-command-edit');
        var div_audio_edit = document.getElementById('command-audio-div-edit');
        var div_video_edit = document.getElementById('command-video-div-edit')
        var input_text = document.getElementById('edit-command-response-div');    
        var input_aliases = document.getElementById('edit-command-response-prefix-div');

        if (seletor_edit.value == "audio"){

            div_audio_edit.hidden = false 
            input_text.hidden = true 
            input_aliases.hidden = true 

        } else if  (seletor_edit.value == "audiotext"){

            div_audio_edit.hidden = false 
            input_text.hidden = false 
            input_aliases.hidden = false 

        } else if (seletor_edit.value == "video"){

            div_video_edit.hidden = false 
            input_text.hidden = true 
            input_aliases.hidden = true 

        } else if  (seletor_edit.value == "videotext"){

            div_video_edit.hidden = false 
            input_text.hidden = false 
            input_aliases.hidden = false 

        } else if  (seletor_edit.value == "tts"){

            div_audio_edit.hidden = true 
            input_text.hidden = false 
            input_aliases.hidden = false 

        } else if  (seletor_edit.value == "text"){

            div_audio_edit.hidden = true 
            input_text.hidden = false 
            input_aliases.hidden = false 

        }
    }

}

function command_edit_status(){

    var div = document.getElementById('div-edit-selected');
    var message = document.getElementById('edit-message-command');

    div.hidden = true;
    message.hidden = false;

}

function command_keys_status(type){

    if (type == 'create'){

        var checkbox = document.getElementById('command-keys-status-create');

        if (checkbox.checked){
            document.getElementById('key_press_create').hidden = false;
        } else {    
            document.getElementById('key_press_create').hidden = true;
        }

    } else if (type == 'edit'){

        var checkbox = document.getElementById('command-keys-status-edit');

        if (checkbox.checked){
            document.getElementById('key_press_edit').hidden = false;
        } else {    
            document.getElementById('key_press_edit').hidden = true;
        }
    }
    

}

async function tts_command(type_id){

    var command = document.getElementById('tts-command');
    var delay = document.getElementById('tts-delay');
    var status = document.getElementById('command-tts-status');
    var cost_status = document.getElementById('command-cost-status-tts'); 
    var cost = document.getElementById('command-cost-tts'); 
    var whitelistStatus = document.getElementById('whitelist-status-tts');

    var prefix = document.getElementById('tts-prefix');
    var emojisFilter = document.getElementById('tts-emojis');
    var wordsFilter = document.getElementById('tts-repetitions-words');
    var lettersFilter = document.getElementById('tts-repetitions-letters');
    var blacklistFilter = document.getElementById('tts-blacklist');

    if (type_id == 'get_command'){

        data = {
            type_id : type_id,
            type_command :'tts',
            type_command_table: 'tts'
        }

        var rec_parse = await window.pywebview.api.commands_default_py(data)
    
        if (rec_parse) {

            command_cost_get('tts',rec_parse.cost_status)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;
            whitelistStatus.checked = rec_parse.whitelist_status == 1 ? true : false;
            cost_status.checked = rec_parse.cost_status == 1 ? true : false;

            cost.value = rec_parse.cost;

            $("#user-level-tts").selectpicker('val', rec_parse.user_level);
            $("#user-level-tts").selectpicker("refresh");
    
        }

    } else if (type_id == "save_command"){
        
        var status = status.checked ? 1 : 0;
        var cost_status = cost_status.checked ? 1 : 0;
        var whitelist_status = whitelistStatus.checked ? 1 : 0;

        
        var roles = []; 

        $('#user-level-tts :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : type_id,
            type_command : 'tts',
            type_command_table: 'tts',
            status : status,
            command : command.value,
            delay: delay.value,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status,
            whitelist_status : whitelist_status
        }

        var data = JSON.stringify(data);

        window.pywebview.api.commands_default_py(data)

    } else if (type_id == "get_config"){

        data = {
            type_id : type_id,
        }

        var data = JSON.stringify(data);

        rec_parse = await window.pywebview.api.tts_command(data)

        if (rec_parse){

            prefix.checked = rec_parse.prefix == 1 ? true : false;
            emojisFilter.checked = rec_parse.emojis_filter == 1 ? true : false;
            wordsFilter.checked = rec_parse.words_filter == 1 ? true : false;
            lettersFilter.checked = rec_parse.letters_filter == 1 ? true : false;
            blacklistFilter.value = rec_parse.blacklist_filter;

        }

    } else if (type_id == "save_config"){

        var prefix = prefix.checked ? 1 : 0;
        var emojisFilter = emojisFilter.checked ? 1 : 0;
        var wordsFilter = wordsFilter.checked ? 1 : 0;
        var lettersFilter = lettersFilter.checked ? 1 : 0;
        var blacklistFilter = blacklistFilter.value;
        
        data = {
            type_id : type_id,
            prefix: prefix,
            emojisFilter: emojisFilter,
            wordsFilter: wordsFilter,
            lettersFilter: lettersFilter,
            blacklistFilter: blacklistFilter
        }

        var data = JSON.stringify(data);

        window.pywebview.api.tts_command(data)
        
    }
}

async function camp_command(type_id){

    var command = document.getElementById('champ-command');
    var delay = document.getElementById('champ-delay');
    var status = document.getElementById('command-champ-status');
    var cost_status = document.getElementById('command-cost-status-champ'); 
    var cost = document.getElementById('command-cost-champ'); 
    var command_select = document.getElementById('command-camp-select');
 
    var whitelistStatus = document.getElementById('whitelist-status-camp');

    if (type_id == 'get'){

        data = {
            type_id : 'get',
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.camp_command(data);
    
        if (rec) {

            rec_parse = JSON.parse(rec)

            command_cost_get('champ',rec_parse.cost_status)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;

            cost_status.checked = rec_parse.cost_status == 1 ? true : false;

            cost.value = rec_parse.cost;

            $("#user-level-champ").selectpicker('val', rec_parse.user_level);
            $("#user-level-champ").selectpicker("refresh");
    
        }

    } else if (type_id == "save"){
        
        var status = status.checked ? 1 : 0;
        var cost_status = cost_status.checked ? 1 : 0;
        var whitelist_status = whitelistStatus.checked ? 1 : 0;
        
        var roles = []; 

        $('#user-level-champ :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : 'save_command',
            type_command : command_select.value,
            type_command_table: 'champ',
            status : status,
            command : command.value,
            delay: delay.value,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status,
            whitelist_status: whitelist_status
        }

        var data = JSON.stringify(data);

        window.pywebview.api.commands_default_py(data)

        
        document.getElementById('form-div-camp').hidden = true

    } else if (type_id == "get_command"){

        data = {
            type_id : type_id,
            type_command : command_select.value,
            type_command_table: 'champ'
        }

        var rec_parse = await window.pywebview.api.commands_default_py(data)
    
        if (rec_parse) {

            command_cost_get('champ',rec_parse.cost_status)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;
            cost_status.checked = rec_parse.cost_status == 1 ? true : false;
            whitelistStatus.checked = rec_parse.whitelist_status == 1 ? true : false;

            cost.value = rec_parse.cost;

            $("#user-level-champ").selectpicker('val', rec_parse.user_level);
            $("#user-level-champ").selectpicker("refresh");

            document.getElementById('form-div-camp').hidden = false
    
        }
    } else if (type_id == "change"){

        document.getElementById('form-div-camp').hidden = true;
    }
}

async function balance_command(type_id){

    var command_type = document.getElementById('command-balance-select');

    var command = document.getElementById('balance-command');
    var delay = document.getElementById('balance-delay');
    var status = document.getElementById('command-balance-status');
    var cost_status = document.getElementById('command-cost-status-balance'); 
    var cost = document.getElementById('command-cost-balance');

    var whitelistStatus = document.getElementById('whitelist-status-balance');

    if (type_id == 'get'){

        data = {
            type_id : "get_command",
            type_command : command_type.value,
            type_command_table: 'balance'
        }

        var rec_parse = await window.pywebview.api.commands_default_py(data);
    
        if (rec_parse) {

            document.getElementById("form-div-balance").hidden = false

            command_cost_get('balance',rec_parse.cost_status)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;
            cost_status.checked = rec_parse.cost_status == 1 ? true : false;
            whitelistStatus.checked = rec_parse.whitelist_status == 1 ? true : false;
            cost.value = rec_parse.cost;

            $("#user-level-balance").selectpicker('val', rec_parse.user_level);
            $("#user-level-balance").selectpicker("refresh");
    
        }

    } else if (type_id == "save"){
        
        var status = status.checked ? 1 : 0;
        var cost_status = cost_status.checked ? 1 : 0;
        var whitelistStatus = whitelistStatus.checked ? 1 : 0;
        var roles = []; 

        $('#user-level-balance :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : 'save_command',
            type_command : command_type.value,
            type_command_table: 'balance',
            status : status,
            command : command.value,
            delay: delay.value,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status,
            whitelist_status: whitelistStatus
        }


        var data = JSON.stringify(data);

        window.pywebview.api.commands_default_py(data)
        
        document.getElementById("form-div-balance").hidden = true

    } else if (type_id == "change"){

        document.getElementById('form-div-balance').hidden = true;
    }
}

function create_table_whitelist(namesArray , command_input_id){

    if ($.fn.DataTable.isDataTable("#whitelist_table")) {
        $('#whitelist_table').DataTable().clear().destroy();
    }

    var table;

    if (namesArray && namesArray.length > 0) {
        table = $('#whitelist_table').DataTable({
            pageLength: 8,
            destroy: true,
            scrollX: true,
            paging: false,
            autoWidth: true,
            ordering: false,
            retrieve: false,
            processing: true,
            responsive: false,
            lengthMenu: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            }
        });

        for (var user of namesArray) {
            var removeBtn = document.createElement("button");
            removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
            removeBtn.setAttribute("type", "button");
            removeBtn.setAttribute("title", "Remover usuário");
            removeBtn.setAttribute("data-toggle", "tooltip");
            removeBtn.setAttribute("data-bs-placement", "top");
            removeBtn.setAttribute("onclick", `whitelist('remove_whitelist','${user}','${command_input_id}')`);
            removeBtn.innerHTML = 'Remover';

            var row = table.row.add([
                user,
                `${removeBtn.outerHTML}`
            ]);
        }
    }

}

async function whitelist(type_id, div_id, command_input_id){

    if (type_id == 'add_whitelist'){

        var user = document.getElementById(div_id);
        var command = document.getElementById(command_input_id);
        
        if (command_input_id == "new-command"){

            var TempInput = document.getElementById("whitelist-command-create-temp");

            var CurrentNames = TempInput.value;
        
            var NewName = user.value;

            if (CurrentNames.trim() !== "") {

                var NewCurrentNames = CurrentNames + "," + NewName;
        
                TempInput.value = NewCurrentNames;

            } else {

                var NewCurrentNames = CurrentNames + NewName;
        
                TempInput.value = NewCurrentNames;

            }

            user.value = ""

        } else {

            data = {
                type_id : 'add_whitelist',
                user : user.value,
                command : command.value
            }
    
            var data = JSON.stringify(data);
    
            var rec = await window.pywebview.api.commands_py(data);
        
            document.getElementById(div_id).value = '';
        }

    } else if (type_id == 'remove_whitelist'){

        var user = document.getElementById(div_id);
        var command = document.getElementById(command_input_id);

        if (command_input_id == "new-command"){

            var TempInput = document.getElementById("whitelist-command-create-temp");

            var CurrentNames = TempInput.value;
    
            var NameToRemove = div_id;

            if (CurrentNames.trim() !== "") {
    
                var namesArray = CurrentNames.split(",");
                
                var indexToRemove = namesArray.indexOf(NameToRemove);

                if (indexToRemove !== -1) {
    
                    namesArray.splice(indexToRemove, 1);
    
                    var NewCurrentNames = namesArray.join(",");
    
                    TempInput.value = NewCurrentNames;

                    create_table_whitelist(namesArray, command_input_id)
    
                } 

            } 

        } else {

            data = {
                type_id : 'remove_whitelist',
                user : div_id,
                command : command.value
            }

            var data = JSON.stringify(data);
    
            var rec = await window.pywebview.api.commands_py(data);
        
            if (rec) {

                if (rec.charAt(rec.length - 1) === ',') {
                    rec = rec.slice(0, -1);
                }

                var namesArray = rec.split(",");
                
                console.log(namesArray)

                create_table_whitelist(namesArray, command_input_id)
    
            } else {
                         
                create_table_whitelist(namesArray, command_input_id)
            }

        }


    } else if (type_id == 'show_whitelist'){

        var user = document.getElementById(div_id);
        var command = document.getElementById(command_input_id);

        $('#command_whitelist').modal('show')

        if (command_input_id == "new-command"){

            var TempInput = document.getElementById("whitelist-command-create-temp");

            var CurrentNames = TempInput.value;

            var namesArray = CurrentNames.split(",");

            create_table_whitelist(namesArray, command_input_id)

        } else {

            data = {
                type_id : 'get_whitelist',
                command : command.value
            }
    
            var data = JSON.stringify(data);
    
            var rec = await window.pywebview.api.commands_py(data);
        
            if (rec) {

                if (rec.charAt(rec.length - 1) === ',') {
                    rec = rec.slice(0, -1);
                }
            
                document.getElementById(div_id).value = '';

                var namesArray = rec.split(",");
                
                create_table_whitelist(namesArray, command_input_id)
    
            } else {
                         
                create_table_whitelist(namesArray, command_input_id)
            }
        }

    }
}

function create_table_blacklist(namesArray , command_input_id){

    if ($.fn.DataTable.isDataTable("#blacklist_table")) {
        $('#blacklist_table').DataTable().clear().destroy();
    }

    var table;

    if (namesArray && namesArray.length > 0) {
        table = $('#blacklist_table').DataTable({
            pageLength: 8,
            destroy: true,
            scrollX: true,
            paging: false,
            autoWidth: true,
            ordering: false,
            retrieve: false,
            processing: true,
            responsive: false,
            lengthMenu: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            }
        });

        for (var user of namesArray) {
            var removeBtn = document.createElement("button");
            removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
            removeBtn.setAttribute("type", "button");
            removeBtn.setAttribute("title", "Remover usuário");
            removeBtn.setAttribute("data-toggle", "tooltip");
            removeBtn.setAttribute("data-bs-placement", "top");
            removeBtn.setAttribute("onclick", `blacklist('remove_blacklist','${user}','${command_input_id}')`);
            removeBtn.innerHTML = 'Remover';

            var row = table.row.add([
                user,
                `${removeBtn.outerHTML}`
            ]);
        }
    }

}

async function blacklist(type_id, div_id, command_input_id){

    if (type_id == 'add_blacklist'){

        var user = document.getElementById(div_id);
        var command = document.getElementById(command_input_id);
        
        if (command_input_id == "new-command"){

            var TempInput = document.getElementById("blacklist-command-create-temp");

            var CurrentNames = TempInput.value;
        
            var NewName = user.value;

            if (CurrentNames.trim() !== "") {

                var NewCurrentNames = CurrentNames + "," + NewName;
        
                TempInput.value = NewCurrentNames;

            } else {

                var NewCurrentNames = CurrentNames + NewName;
        
                TempInput.value = NewCurrentNames;
            }

            user.value = ""

        } else {

            data = {
                type_id : 'add_blacklist',
                user : user.value,
                command : command.value
            }
    
            var data = JSON.stringify(data);
    
            var rec = await window.pywebview.api.commands_py(data);
        
            document.getElementById(div_id).value = '';
        }

    } else if (type_id == 'remove_blacklist'){

        var user = document.getElementById(div_id);
        var command = document.getElementById(command_input_id);

        if (command_input_id == "new-command"){

            var TempInput = document.getElementById("blacklist-command-create-temp");

            var CurrentNames = TempInput.value;
    
            var NameToRemove = div_id;

            if (CurrentNames.trim() !== "") {
    
                var namesArray = CurrentNames.split(",");
                
                var indexToRemove = namesArray.indexOf(NameToRemove);

                if (indexToRemove !== -1) {
    
                    namesArray.splice(indexToRemove, 1);
    
                    var NewCurrentNames = namesArray.join(",");
    
                    TempInput.value = NewCurrentNames;

                    create_table_blacklist(namesArray, command_input_id)
    
                } 
            }
        } else {

            data = {
                type_id : 'remove_blacklist',
                user : div_id,
                command : command.value
            }

            var data = JSON.stringify(data);
    
            var rec = await window.pywebview.api.commands_py(data);
        
            if (rec) {
                
                if (rec.charAt(rec.length - 1) === ',') {
                    rec = rec.slice(0, -1);
                }

                var namesArray = rec.split(",");
                
                create_table_blacklist(namesArray, command_input_id)

    
            } else {
                
                create_table_blacklist([], command_input_id)

            }

        }


    } else if (type_id == 'show_blacklist'){

        var user = document.getElementById(div_id);
        var command = document.getElementById(command_input_id);

        $('#command_blacklist').modal('show')

        if (command_input_id == "new-command"){

            var TempInput = document.getElementById("blacklist-command-create-temp");

            var CurrentNames = TempInput.value;

            var namesArray = CurrentNames.split(",");

            create_table_blacklist(namesArray, command_input_id)

            
        } else {

            data = {
                type_id : 'get_blacklist',
                user : user.value,
                command : command.value
            }
    
            var data = JSON.stringify(data);
    
            var rec = await window.pywebview.api.commands_py(data);
        
            if (rec) {
                
                if (rec.charAt(rec.length - 1) === ',') {
                    rec = rec.slice(0, -1);
                }
            
                document.getElementById(div_id).value = '';

                var namesArray = rec.split(",");
                
                create_table_blacklist(namesArray, command_input_id)

    
            } else {
                
                create_table_blacklist([], command_input_id)

            }
        }

    }

}


function table_whitelistDefault(namesArray, command_type, command_table){

    if ($.fn.DataTable.isDataTable("#whitelist_table")) {
        $('#whitelist_table').DataTable().clear().destroy();
    }

    var table;

    if (namesArray && namesArray.length > 0) {
        table = $('#whitelist_table').DataTable({
            pageLength: 8,
            destroy: true,
            scrollX: true,
            paging: false,
            autoWidth: true,
            ordering: false,
            retrieve: false,
            processing: true,
            responsive: false,
            lengthMenu: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            }
        });

        for (var user of namesArray) {
            var removeBtn = document.createElement("button");
            removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
            removeBtn.setAttribute("type", "button");
            removeBtn.setAttribute("title", "Remover usuário");
            removeBtn.setAttribute("data-toggle", "tooltip");
            removeBtn.setAttribute("data-bs-placement", "top");
            removeBtn.setAttribute("onclick", `whitelistDefault('remove_whitelist','${user}','${command_type}','${command_table}')`);
            removeBtn.innerHTML = 'Remover';

            var row = table.row.add([
                user,
                `${removeBtn.outerHTML}`
            ]);
        }
    }

}

function table_blacklistDefault(namesArray, command_type, command_table){

    if ($.fn.DataTable.isDataTable("#blacklist_table")) {
        $('#blacklist_table').DataTable().clear().destroy();
    }

    var table;

    if (namesArray && namesArray.length > 0) {
        table = $('#blacklist_table').DataTable({
            pageLength: 8,
            destroy: true,
            scrollX: true,
            paging: false,
            autoWidth: true,
            ordering: false,
            retrieve: false,
            processing: true,
            responsive: false,
            lengthMenu: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
            }
        });

        for (var user of namesArray) {
            var removeBtn = document.createElement("button");
            removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
            removeBtn.setAttribute("type", "button");
            removeBtn.setAttribute("title", "Remover usuário");
            removeBtn.setAttribute("data-toggle", "tooltip");
            removeBtn.setAttribute("data-bs-placement", "top");
            removeBtn.setAttribute("onclick", `blacklistDefault('remove_blacklist','${user}','${command_type}','${command_table}')`);
            removeBtn.innerHTML = 'Remover';

            var row = table.row.add([
                user,
                `${removeBtn.outerHTML}`
            ]);
        }
    }

}


async function whitelistDefault(type_id, input_id, command_type, command_table){

    if (type_id == 'add_whitelist'){

        var user = document.getElementById(input_id);
        var command_type = document.getElementById(command_type).value;

        data = {
            type_id : 'add_whitelistDefault',
            user : user.value,
            command_type : command_type,
            command_table : command_table
        }

        var data = JSON.stringify(data);

        window.pywebview.api.commands_py(data);
    
        document.getElementById(input_id).value = '';

    } else if (type_id == 'remove_whitelist'){

        data = {
            type_id : 'remove_whitelistDefault',
            user : input_id,
            command_type : command_type,
            command_table : command_table
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.commands_py(data);
    
        if (rec) {

            if (rec.charAt(rec.length - 1) === ',') {
                rec = rec.slice(0, -1);
            }

            var namesArray = rec.split(",");

            table_whitelistDefault(namesArray, command_type, command_table)

        } else {
                        
            table_whitelistDefault(namesArray,  command_type, command_table)
        }



    } else if (type_id == 'show_whitelist'){

        var command_type = document.getElementById(command_type).value;

        $('#command_whitelist').modal('show')

        data = {
            type_id : 'get_whitelistDefault',
            command_type : command_type,
            command_table : command_table
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.commands_py(data);
    
        if (rec) {

            if (rec.charAt(rec.length - 1) === ',') {
                rec = rec.slice(0, -1);
            }

            var namesArray = rec.split(",");
            
            table_whitelistDefault(namesArray, command_type, command_table)

        } else {
                        
            table_whitelistDefault([], command_type, command_table)
        }

    }
}

async function blacklistDefault(type_id, input_id, command_type, command_table){

    if (type_id == 'add_blacklist'){

        var user = document.getElementById(input_id);
        var command_type = document.getElementById(command_type).value;

        data = {
            type_id : 'add_blacklistDefault',
            user : user.value,
            command_type : command_type,
            command_table : command_table
        }

        var data = JSON.stringify(data);

        window.pywebview.api.commands_py(data);
    
        document.getElementById(input_id).value = '';

    } else if (type_id == 'remove_blacklist'){

        data = {
            type_id : 'remove_blacklistDefault',
            user : input_id,
            command_type : command_type,
            command_table : command_table
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.commands_py(data);
        
        if (rec) {
            
            if (rec.charAt(rec.length - 1) === ',') {
                rec = rec.slice(0, -1);
            }

            var namesArray = rec.split(",");
            
            table_blacklistDefault(namesArray, command_type, command_table)

        } else {
            
            table_blacklistDefault([], command_type, command_table)

        }

    } else if (type_id == 'show_blacklist'){

        var command_type = document.getElementById(command_type).value;

        $('#command_blacklist').modal('show')

        data = {
            type_id : 'get_blacklistDefault',
            command_type : command_type,
            command_table : command_table
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.commands_py(data);
    
        if (rec) {
            
            if (rec.charAt(rec.length - 1) === ',') {
                rec = rec.slice(0, -1);
            }

            var namesArray = rec.split(",");
            
            table_blacklistDefault(namesArray, command_type, command_table)

        } else {
            
            table_blacklistDefault([], command_type, command_table)

        }

    }
    
}