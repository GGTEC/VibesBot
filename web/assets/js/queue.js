async function queue_js_create(queue_lists, queue_list_playing, divId) {

    var divContainer = document.getElementById(divId);

    divContainer.innerHTML = "";

    if (divId == "queuelist_table_playing" && queue_list_playing.length != 0){

        currentList = queue_lists

        var dataTableData = [];

        $.each(currentList, function (index, item) {

            dataTableData.push([
                item
            ]);
        });

        var table = document.createElement("table");
        table.classList.add("table");
        
        var thead = table.createTHead();
        var row = thead.insertRow();
        
        var headers = ["Usuário"];
        
        for (var j = 0; j < headers.length; j++) {
        
            var th = document.createElement("th");
            th.textContent = headers[j];
        
            if (headers[j] === "Usuário") {
                th.style.width = "100%";
            }
        
            row.appendChild(th);
        }

        var tbody = table.createTBody();

        for (var i = 0; i < dataTableData.length; i++) {
        
            var tr = tbody.insertRow();
        
            for (var j = 0; j < dataTableData[i].length; j++) {
        
                var cell = tr.insertCell(j);
        
                if (typeof dataTableData[i][j] === 'object') {
        
                    cell.appendChild(dataTableData[i][j]);
        
                } else {
                    cell.textContent = dataTableData[i][j];
                }
            }
        }

        div_match = document.createElement('div')
        div_match.classList.add('d-flex', 'flex-row', 'justify-content-between',  'mt-5', 'mb-3', 'w-100')

        button_match = document.createElement('button')
        button_match.setAttribute('onclick', `queue_js('end_playing','${JSON.stringify({[key] : currentList})}')`);

        button_match.innerText = "Finalizar partida";
        button_match.classList.add('btn', 'bt-submit');
        
        table_title = document.createElement('h4')
        table_title.innerText = "Em partida";

        div_match.appendChild(table_title);
        div_match.appendChild(button_match);

        divContainer.appendChild(div_match);
        divContainer.appendChild(table);

    } else {

        for (var key in queue_lists) {

            var currentList = queue_lists[key];
    
            var dataTableData = [];
    
            $.each(currentList, function (index, item) {
    
                var button_config = document.createElement("button");
    
                if (divId == "queuelist_table_normal"){

                    var queue_remove = "queue_rem";

                } else {

                    var queue_remove = "queue_rem_priority";

                }

                button_config.innerText = "Remover";
                button_config.classList.add('btn', 'bt-submit');
                button_config.setAttribute('onclick', `queue_js('${queue_remove}','${item.replace("'", "\\'")}')`);

                var formGroupDiv = document.createElement("div");
                formGroupDiv.classList.add("form-group", "bg-dark", "form-block", "mt-0", "mb-0", "p-0");
                
                var inputGroupDiv = document.createElement("div");
                inputGroupDiv.classList.add("input-group", "none-flex");
                
                var selectpicker = document.createElement("select");
                selectpicker.classList.add('selectpicker', 'bg-dark');
                selectpicker.setAttribute('data-live-search', 'true');

                var sendButton = document.createElement("button");
                sendButton.innerText = "Mover";
                sendButton.classList.add('btn', 'bt-submit');

                inputGroupDiv.appendChild(selectpicker);
                inputGroupDiv.appendChild(sendButton);
                
                formGroupDiv.appendChild(inputGroupDiv);
                

                for (var queue in queue_lists) {

                    if (queue != key){

                        var option = document.createElement("option");
                        option.text = queue;
                        selectpicker.add(option);
                        
                    }

                }
                
                (function (currentKey) {

                    sendButton.addEventListener('click', function () {

                        var selectedQueue = selectpicker.value;

                        if (divId == "queuelist_table_normal"){

                            var queue_move = "queue_move";

                        } else {

                            var queue_move = "queue_move_priority";

                        }

                        queue_move_js(item.replace("'", "\\'"), currentKey, selectedQueue, queue_move);
                    });
                })(key);
                

                dataTableData.push([
                    item,
                    formGroupDiv,
                    button_config
                ]);

    
            });
    
            var table = document.createElement("table");
            table.classList.add("table");
    
            var thead = table.createTHead();
            var row = thead.insertRow();
    
            var headers = ["Usuário", "Mover", "Remover"];
    
            for (var j = 0; j < headers.length; j++) {
    
                var th = document.createElement("th");
                th.textContent = headers[j];
    
                if (headers[j] === "Usuário") {
                    th.style.width = "100%";
                }
    
                row.appendChild(th);
            }
    
            var tbody = table.createTBody();
    
            for (var i = 0; i < dataTableData.length; i++) {

                var tr = tbody.insertRow();

                for (var j = 0; j < dataTableData[i].length; j++) {
                    
                    var cell = tr.insertCell(j);
    
                    if (typeof dataTableData[i][j] === 'object') {
                        cell.appendChild(dataTableData[i][j]);
                    } else {
                        cell.textContent = dataTableData[i][j];
                    }
                }
            }
    
            div_match = document.createElement('div')
            div_match.classList.add('d-flex', 'flex-row', 'justify-content-between',  'mt-5', 'mb-3', 'w-100')
            
            if (divId == "queuelist_table_normal"){
                var status = "set_playing"
            } else {
                var status = "set_playing_pri"
            }

            button_match = document.createElement('button')
            button_match.setAttribute('onclick', `queue_js('${status}','${JSON.stringify({[key] : currentList})}')`);
    
            button_match.innerText = "Jogando";
            button_match.classList.add('btn', 'bt-submit');

            if (queue_list_playing.length != 0){
                button_match.setAttribute('disabled', true)
            }
            
            
            table_title = document.createElement('h4')
            table_title.innerText = key;
    
            div_match.appendChild(table_title);
            div_match.appendChild(button_match);
    
            divContainer.appendChild(div_match);
            divContainer.appendChild(table);

            $('select').attr('data-container', 'body').selectpicker({
                liveSearch: true,
                showSubtext: true,
                size: 5,
                width: '100%',
                style: 'btn-dark',
                noneResultsText: "Nenhum resultado para {0}",
                liveSearchPlaceholder: "Pesquise o item",
                noneSelectedText : 'Selecione um item'
            });
        }
    }


}


async function queue_js_process(queue_parse) {

    var queue_list = queue_parse.queue
    var queue_list_pri = queue_parse.queue_pri
    var queue_list_playing = queue_parse.queue_playing

    queue_js_create(queue_list_playing, queue_list_playing, 'queuelist_table_playing')
    queue_js_create(queue_list, queue_list_playing, 'queuelist_table_normal')

    if (queue_parse.roles_status == 1){

        document.getElementById('queue-pri-div').hidden = false
        queue_js_create(queue_list_pri, queue_list_playing, 'queuelist_table_pri')

    } else {

        document.getElementById('queue-pri-div').hidden = true

    }
}

async function queue_move_js(name, actual_match, move_to_match, type_id){

    data = {
        user : name,
        actual_match : actual_match,
        move_to_match : move_to_match
    }

    var queue_data = await window.pywebview.api.queue(type_id, data);

    if (queue_data) {

        queue_js_process(JSON.parse(queue_data))

    }

}

async function queue_js(type_id,item){
    
    if (type_id == "queue_add"){

        var add_queue = document.getElementById('add_queue').value;

        var queue_data = await window.pywebview.api.queue(type_id,add_queue);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))

            add_queue = ''
        }

    } else if (type_id == "queue_rem"){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))

        }

    } else if (type_id == "queue_rem_priority"){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))

        }

    } else if (type_id == "clear_queue"){

        var queue_data = await window.pywebview.api.queue(type_id, "None");

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
        }

    } else if (type_id == "clear_queue_pri"){

        var queue_data = await window.pywebview.api.queue(type_id, "None");

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
        }

    } else if (type_id == "queue_add_pri"){

        var add_queue = document.getElementById('add_queue_pri').value;

        var queue_data = await window.pywebview.api.queue(type_id,add_queue);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
            
            add_queue = ''
        }

    } else if (type_id == "queue_rem_pri"){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
    }

    } else if (type_id == "save_config"){

        var role_status = document.getElementById('queue-role-status');
        var queue_pri_status = document.getElementById('queue-pri-status'); 
        var queue_spend_status = document.getElementById('queue-spend-status');
        var queue_limt = document.getElementById('queue-limit');

        queue_pri_status = queue_pri_status.checked == 1 ? true : false;
        role_status = role_status.checked == 1 ? true : false;
        status_spend = queue_spend_status.checked ? 1 : 0;
        queue_limt = queue_limt.value

        var roles = []; 

        $('#queue-role :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data = {
            spend_user : status_spend,
            role_status : role_status,
            roles_queue : roles,
            roles_pri : queue_pri_status,
            limit : queue_limt
        }

        window.pywebview.api.queue(type_id,data);

    } else if (type_id == "get_config"){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_parse = JSON.parse(queue_data)

            var role_status = document.getElementById('queue-role-status');
            var queue_pri_status = document.getElementById('queue-pri-status'); 
            var queue_spend_status = document.getElementById('queue-spend-status');
            var queue_limt = document.getElementById('queue-limit');

            role_status.checked = queue_parse.roles_status == 1 ? true : false;
            queue_pri_status.checked = queue_parse.roles_pri == 1 ? true : false;
            queue_spend_status.checked = queue_parse.spend_user == 1 ? true : false;
            queue_limt.value = queue_parse.limit

            var roles = queue_parse.roles_queue

            $('#queue-role').selectpicker('val', roles);
            $('#queue-role').selectpicker('refresh');

        }

    } else if (type_id == 'get_queue'){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
        }

    } else if (type_id == 'get_command') {

        var command_queue_select = document.getElementById('command-queue-select');

        var command_queue_status = document.getElementById('command-queue-status');
        var command_queue_command = document.getElementById('command-queue-command');
        var command_queue_delay = document.getElementById('command-queue-delay');
        var command_queue_cost_status = document.getElementById('command-cost-status-queue'); 
        var command_queue_cost = document.getElementById('command-cost-queue');

        var command_queue_whitelistStatus = document.getElementById('whitelist-status-queue');

        var queue_command_edit = document.getElementById('command_queue_form');

        data = {
            type_id : type_id,
            type_command : command_queue_select.value,
            type_command_table: 'queue'
        }

        var queue_parse = await window.pywebview.api.commands_default_py(data);

        if (queue_parse){
            
            queue_command_edit.hidden = false       

            command_cost_get('queue',queue_parse.cost_status)

            command_queue_status.checked = queue_parse.status == 1 ? true : false;
            command_queue_cost_status.checked = queue_parse.cost_status == 1 ? true : false;
            command_queue_whitelistStatus.checked = queue_parse.whitelist_status == 1 ? true : false;
            command_queue_command.value = queue_parse.command
            command_queue_delay.value = queue_parse.delay
            command_queue_cost.value = queue_parse.cost

            $("#command-queue-perm").selectpicker('val',queue_parse.user_level)
            $("#command-queue-perm").selectpicker("refresh");

        }

    } else if (type_id == 'save_command') {

        var command_queue_select = document.getElementById('command-queue-select');

        var command_queue_status = document.getElementById('command-queue-status');
        var command_queue_command = document.getElementById('command-queue-command');
        var command_queue_delay = document.getElementById('command-queue-delay');

        var command_queue_cost_status = document.getElementById('command-cost-status-queue'); 
        var command_queue_cost = document.getElementById('command-cost-queue');
        
        var command_queue_whitelistStatus = document.getElementById('whitelist-status-queue');

        var command_status = command_queue_status.checked ? 1 : 0;
        var command_cost_status = command_queue_cost_status.checked ? 1 : 0;
        var whitelist_status = command_queue_whitelistStatus.checked ? 1 : 0;
        
        var roles = []; 

        $('#command-queue-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data  = {
            type_id : type_id,
            type_command: command_queue_select.value,
            type_command_table: 'queue',
            command: command_queue_command.value,
            status: command_status,
            delay: command_queue_delay.value,
            user_level: roles,
            cost: command_queue_cost.value,
            cost_status: command_cost_status,
            whitelist_status : whitelist_status
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.commands_default_py(formData)

        document.getElementById("command_queue_form").hidden = true

    } else if (type_id == 'queue-pri'){

        var queue_pri_status = document.getElementById('queue-pri-status'); 

        if (queue_pri_status.checked){
            document.getElementById('queue-pri-div').hidden = false
        } else {
            document.getElementById('queue-pri-div').hidden = true
        }

        queue_js('save_config', null)

    } else if (type_id == 'hideconfig'){
        document.getElementById("command_queue_form").hidden = true
    } else if (type_id == 'set_playing'){

        var queue_data = await window.pywebview.api.queue(type_id, JSON.parse(item));

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
        }

    } else if (type_id == 'set_playing_pri') {

        var queue_data = await window.pywebview.api.queue(type_id, JSON.parse(item));

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
        }
    } else if (type_id == 'end_playing'){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_js_process(JSON.parse(queue_data))
        }

    } else if (type_id == 'get_ended'){

        var queue_data = await window.pywebview.api.queue(type_id, '');

        if (queue_data) {
            
            queue_data = JSON.parse(queue_data)

            $("#list-queue-ended").modal("show");
        
            var tbody_queue = document.getElementById('table_ended_body');

            tbody_queue.innerHTML = ''

            Object.entries(queue_data.queue_ended).forEach(([k, v]) => {

                var players = v.match;
                var time = v.time;
            
                // Crie uma nova linha
                var row = tbody_queue.insertRow();
            
                // Adicione células à linha
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
            
                // Atribua valores às células
                cell1.textContent = time;
                cell2.textContent = players;

            });

        }

    }

}
