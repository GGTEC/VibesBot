//COMANDOS

function show_commands_div(div_id) {

    if (div_id == "del-commands-div") {
        commands_fun('get_list');
    } else if (div_id == "edit-commands-div") {
        commands_fun('get_list');
    } else if (div_id ==  'default-commands-div'){
        champ_command('get');
    } else if (div_id == 'tts-commands-div'){
        tts_command('get');
    } else if (div_id == 'vote-commands-div'){
        votes('get_commands')
    }
    document.getElementById("commands-div").hidden = true;
    document.getElementById(div_id).hidden = false;
}

function hide_commands_div(div_id, modal) {

    $("#" + modal).modal("hide");
    document.getElementById("commands-div").hidden = false;
    document.getElementById(div_id).hidden = true;

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
            cost: cost.value,
            cost_status: cost_status,
            keys_status: key_status,
            keys: keys_list,
            time_key: time_key.value
        };
    
        var formData = JSON.stringify(data);

        window.pywebview.api.commands_py(formData);

        document.getElementById('new-command').value = '';
        document.getElementById('new-delay').value = '';
        document.getElementById('sound-command').value = '';
        document.getElementById('new-command-response').value = '';

    } else if (type_id == 'edit'){

        var seletor_edit = document.getElementById('type-command-edit');
        var status_command = document.getElementById('command-simple-status');
        var command = document.getElementById('command-select-edit');
        var new_command = document.getElementById('edit-command');
        var sound = document.getElementById('sound-command-edit').value;
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
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status,
            keys_status: key_status,
            keys: keys_list,
            time_key: time_key.value
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
            var edit_level = command_info_parse.edit_level;
            var cost_status = command_info_parse.edit_cost_status;
            var edit_cost = command_info_parse.edit_cost;
            var key_status_r = command_info_parse.edit_keys_status;
            var time_key_r = command_info_parse.edit_time_key;

            var key1 = command_info_parse.edit_keys[0];
            var key2 = command_info_parse.edit_keys[1];
            var key3 = command_info_parse.edit_keys[2];
            var key4 = command_info_parse.edit_keys[3];

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
            [commandData, queueData, giveawayData, playerData].forEach(data => {
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
    var prefix = document.getElementById('command-tts-prefix');
    var cost_status = document.getElementById('command-cost-status-tts'); 
    var cost = document.getElementById('command-cost-tts'); 
 
    if (type_id == 'get'){

        data = {
            type_id : 'get',
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.tts_command(data);
    
        if (rec) {

            rec_parse = JSON.parse(rec)

            command_cost_get('tts',rec_parse.cost_status)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;
            prefix.checked = rec_parse.prefix == 1 ? true : false;

            cost_status.checked = rec_parse.cost_status == 1 ? true : false;

            cost.value = rec_parse.cost;

            $("#user-level-tts").selectpicker('val', rec_parse.user_level);
            $("#user-level-tts").selectpicker("refresh");
    
        }

    } else if (type_id == "save"){
        
        var status = status.checked ? 1 : 0;
        var cost_status = cost_status.checked ? 1 : 0;
        var prefix = prefix.checked ? 1 : 0;
        
        var roles = []; 

        $('#user-level-tts :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : 'save',
            status : status,
            prefix : prefix,
            command : command.value,
            delay: delay.value,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status
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
        
        var roles = []; 

        $('#user-level-champ :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : 'save',
            status : status,
            command_select : command_select.value,
            command : command.value,
            delay: delay.value,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status
        }

        var data = JSON.stringify(data);

        window.pywebview.api.camp_command(data)

        
        document.getElementById('form-div-camp').hidden = true

    } else if (type_id == "get_command"){

        data = {
            command_select : command_select.value,
            type_id : 'get_command',
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


    if (type_id == 'get'){

        document.getElementById("form-div-balance").hidden = false

        data = {
            type_id : 'get',
            command : command_type.value
        }

        var data = JSON.stringify(data);

        var rec = await window.pywebview.api.balance_command(data);
    
        if (rec) {

            rec_parse = JSON.parse(rec)

            command_cost_get('balance',rec_parse.cost_status)

            command.value = rec_parse.command;
            delay.value = rec_parse.delay;
            status.checked = rec_parse.status == 1 ? true : false;
            cost_status.checked = rec_parse.cost_status == 1 ? true : false;
            cost.value = rec_parse.cost;

            $("#user-level-balance").selectpicker('val', rec_parse.user_level);
            $("#user-level-balance").selectpicker("refresh");
    
        }

    } else if (type_id == "save"){
        
        var status = status.checked ? 1 : 0;
        var cost_status = cost_status.checked ? 1 : 0;
        var roles = []; 

        $('#user-level-balance :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : 'save',
            command_type : command_type.value,
            status : status,
            command : command.value,
            delay: delay.value,
            user_level: roles,
            cost: cost.value,
            cost_status: cost_status
        }


        var data = JSON.stringify(data);

        window.pywebview.api.balance_command(data)
        
        document.getElementById("form-div-balance").hidden = true

    } else if (type_id == "change"){

        document.getElementById('form-div-balance').hidden = true;
    }
}
