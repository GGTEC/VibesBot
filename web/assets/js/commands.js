//COMANDOS

function show_commands_div(div_id) {

    if (div_id == "del-commands-div") {
        commands_fun('get_list');
    } else if (div_id == "edit-commands-div") {
        commands_fun('get_list');
    } else if (div_id ==  'tts-commands-div'){
        tts_command('get')
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

        seletor = document.getElementById('command-audio-status');
        div = document.getElementById('command-audio-div');

        var type = seletor.checked ? 'sound' : '';

        var roles = []; 

        $('#user-level-command :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : type_id,
            type: type,
            command: document.getElementById('new-command').value,
            delay: document.getElementById('new-delay').value,
            user_level: roles,
            sound: document.getElementById('sound-command').value,
        };
    
        var formData = JSON.stringify(data);

        window.pywebview.api.commands_py(formData);

        document.getElementById('new-command').value = '';
        document.getElementById('new-delay').value = '';
        document.getElementById('user-level-command').value = '';
        document.getElementById('sound-command').value = '';
        div.hidden = true
        seletor.checked = false

    } else if (type_id == 'edit'){

        var status_command = document.getElementById('command-simple-status');
        var command = document.getElementById('command-select-edit').value
        var sound = document.getElementById('sound-command-edit').value;

        var seletor_edit = document.getElementById('command-audio-status-edit');
        var div_edit = document.getElementById('command-audio-div-edit');

        var type = seletor_edit.checked ? 'sound' : '';

        var status_command = status_command.checked ? 1 : 0;

        var roles = []; 

        $('#user-level-command-edit :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            type_id : type_id,
            type: type,
            command: document.getElementById('command-select-edit').value,
            new_command: document.getElementById('edit-command').value,
            status_command: status_command,
            delay: document.getElementById('edit-delay').value,
            sound: sound,
            user_level: roles,
        };

        var formData = JSON.stringify(data);
        window.pywebview.api.commands_py(formData);

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
                $("#command-select-del").selectpicker("refresh");
                $("#command-select-edit").append('<option style="background: #000; color: #fff;" value="'+ optn +'">'+ optn +'</option>');
                $("#command-select-edit").selectpicker("refresh");
            }
        }

    } else if (type_id == 'get_info'){

        var command = document.getElementById("command-select-edit").value;
        var seletor_edit = document.getElementById('command-audio-status-edit');
        var div_edit = document.getElementById('command-audio-div-edit');

        data = {
            type_id : type_id,
            command : command
        };

        var formData = JSON.stringify(data);

        var command_info_parse = await window.pywebview.api.commands_py(formData);

        if (command_info_parse) {
            
            command_info_parse = JSON.parse(command_info_parse)

            var status_command = command_info_parse.status;
            var command_edit = command_info_parse.edit_command;
            var delay_edit = command_info_parse.edit_delay;
            var sound_edit = command_info_parse.sound;

            if (status_command == 1){
                document.getElementById("command-simple-status").checked = true;
            } else if (status_command == 0){
                document.getElementById("command-simple-status").checked = false;
            }

            if (sound_edit != ""){
                seletor_edit.checked = true
                div_edit.hidden = false
            } else {
                seletor_edit.checked = false
                div_edit.hidden = true
            }


            document.getElementById('sound-command-edit').value = sound_edit;
            document.getElementById("edit-command").value = command_edit;
            document.getElementById("edit-delay").value = delay_edit;

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

                    const item = key;
                    const lastUse = item.last_use != "" ? new Date(item.last_use * 1000).toLocaleString() : "Nunca";
                    const status = item.status != "" ? (item.status === 1 ? "Sim" : "Não") : "Não";
                    const delay = item.delay != "" ? item.delay : "Null";
                    const response = item.response != "" ? item.response : "Sem resposta";
                    const userLevel = item.user_level != "" ? item.user_level : "Null";

                    dataTableData.push([
                        key,
                        type,
                        lastUse,
                        status,
                        delay,
                        response,
                        userLevel
                    ]);
                }
              }
          
              return dataTableData;
            }
          
            const commandData = processCommandList(command_list_parse.commands[0], "Simples");
            const queueData = processCommandList(command_list_parse.commands_queue[0], "Counter");
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
                { title: 'Resposta' },
                { title: 'Nível do usuário' }
              ]
            });
          
            // Adicionar as linhas à tabela
            [commandData, queueData, giveawayData, playerData].forEach(data => {
              data.forEach(row => {
                console.log(data)
                table.row.add(row).draw();
              });
            });
          }
    }
}

function command_audio_status(type_id){

    if(type_id == 'create'){

        var seletor_create = document.getElementById('command-audio-status');
        var div_create = document.getElementById('command-audio-div');

        if (seletor_create.checked){
            div_create.hidden = false;
        } else {
            div_create.hidden = true;
        }

    } else if(type_id == 'edit'){

        var seletor_edit = document.getElementById('command-audio-status-edit');
        var div_edit = document.getElementById('command-audio-div-edit');

        if (seletor_edit.checked){
            div_edit.hidden = false;
        } else {
            div_edit.hidden = true;
        }
    }

}