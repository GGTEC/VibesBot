async function queue_js(type_id,item){
    
    if (type_id == "get"){

        var queue_data = await window.pywebview.api.queue(type_id,'none');

        if (queue_data) {

            queue_parse = JSON.parse(queue_data)

            var queue_list = queue_parse.queue

            var dataTableData = [];

            $.each(queue_list, function(index, value) {

                var button_config = document.createElement("button");

                button_config.innerText = "Remover";
                button_config.classList.add('bnt','bt-submit')
                button_config.setAttribute('onclick', `queue_js('queue_rem','${value}')`)

                dataTableData.push([
                    value,
                    button_config.outerHTML
                ]);

            });


            if ($.fn.DataTable.isDataTable("#queuelist_table")) {

                $('#queuelist_table').DataTable().clear().draw();
                $('#queuelist_table').DataTable().destroy();
            }
            

            var table = $('#queuelist_table').DataTable( {
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
                    { title: 'Usuário' },
                    { title: 'Remover' },
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }

        }

    } else if (type_id == "queue_add"){

        var add_queue = document.getElementById('add_queue').value;

        var queue_data = await window.pywebview.api.queue(type_id,add_queue);

        if (queue_data) {
            
            queue_list = JSON.parse(queue_data)

            var dataTableData = [];

            $.each(queue_list, function(index, value) {

                var button_config = document.createElement("button");

                button_config.innerText = "Remover";
                button_config.classList.add('bnt','bt-submit')
                button_config.setAttribute('onclick', `queue_js('queue_rem','${value}')`)

                dataTableData.push([
                    value,
                    button_config.outerHTML
                ]);

            });


            if ($.fn.DataTable.isDataTable("#queuelist_table")) {

                $('#queuelist_table').DataTable().clear().draw();
                $('#queuelist_table').DataTable().destroy();
            }
            

            var table = $('#queuelist_table').DataTable( {
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
                    { title: 'Usuário' },
                    { title: 'Remover' },
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }
            
            add_queue = ''
    }

    } else if (type_id == "queue_rem"){

        var queue_data = await window.pywebview.api.queue(type_id,item);

        if (queue_data) {

            queue_list = JSON.parse(queue_data)

            var dataTableData = [];

            $.each(queue_list, function(index, value) {

                var button_config = document.createElement("button");

                button_config.innerText = "Remover";
                button_config.classList.add('bnt','bt-submit')
                button_config.setAttribute('onclick', `queue_js('queue_rem','${value}')`)

                dataTableData.push([
                    value,
                    button_config.outerHTML
                ]);

            });


            if ($.fn.DataTable.isDataTable("#queuelist_table")) {

                $('#queuelist_table').DataTable().clear().draw();
                $('#queuelist_table').DataTable().destroy();
            }
            

            var table = $('#queuelist_table').DataTable( {
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
                    { title: 'Usuário' },
                    { title: 'Remover' },
                ]
            } );

            for (var i = 0; i < dataTableData.length; i++) {
                table.row.add(dataTableData[i]).draw();
            }

    }

    } else if (type_id == 'get_commands') {

        var command_queue_select = document.getElementById('command-queue-select');

        var command_queue_status = document.getElementById('command-queue-status');
        var command_queue_command = document.getElementById('command-queue-command');
        var command_queue_delay = document.getElementById('command-queue-delay');
        var command_queue_cost_status = document.getElementById('command-cost-status-queue'); 
        var command_queue_cost = document.getElementById('command-cost-queue'); 
        var command_queue_cost_type = document.getElementById("command-cost-type-queue");

        var queue_command_edit = document.getElementById('command_queue_form');

        var queue_parse = await window.pywebview.api.queue(type_id,command_queue_select.value);

        if (queue_parse){

            queue_parse = JSON.parse(queue_parse)
            
            queue_command_edit.hidden = false       

            command_cost_get('queue',queue_parse.cost_status)

            command_queue_cost_status.checked = queue_parse.cost_status == 1 ? true : false;
            command_queue_status.checked = queue_parse.status == 1 ? true : false;
            command_queue_command.value = queue_parse.command
            command_queue_delay.value = queue_parse.delay
            command_queue_cost.value = queue_parse.cost

            $("#command-queue-perm").selectpicker('val',queue_parse.user_level)
            $("#command-queue-perm").selectpicker("refresh");

            $("#command-cost-type-queue").selectpicker('val', queue_parse.cost_type);
            $("#command-cost-type-queue").selectpicker("refresh");

        }

    } else if (type_id == 'save_commands') {

        var command_queue_select = document.getElementById('command-queue-select');

        var command_queue_status = document.getElementById('command-queue-status');
        var command_queue_command = document.getElementById('command-queue-command');
        var command_queue_delay = document.getElementById('command-queue-delay');

        var command_queue_cost_status = document.getElementById('command-cost-status-queue'); 
        var command_queue_cost = document.getElementById('command-cost-queue'); 
        var command_queue_cost_type = document.getElementById("command-cost-type-queue");

        var command_status = command_queue_status.checked ? 1 : 0;
        var command_cost_status = command_queue_cost_status.checked ? 1 : 0;
        
        var roles = []; 

        $('#command-queue-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data  = {
            type_command: command_queue_select.value,
            command: command_queue_command.value,
            status: command_status,
            delay: command_queue_delay.value,
            user_level: roles,
            cost: command_queue_cost.value,
            cost_type: command_queue_cost_type.value,
            cost_status: command_cost_status
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.queue(type_id,formData)

    }
}
