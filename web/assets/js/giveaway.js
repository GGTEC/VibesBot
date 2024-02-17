async function giveaway_js(type_id) {
    
    if (type_id == 'get_config') {
        
        var giveaway_name_inp = document.getElementById("giveaway-name");
        var giveaway_clear = document.getElementById("giveaway-clear-names-end");
        var giveaway_enable = document.getElementById('giveaway-enable');
        var giveaway_mult = document.getElementById('giveaway-mult');

        var giveaway_info = await window.pywebview.api.giveaway_py(type_id,'null');
    
        if (giveaway_info) {

            var giveaway_info_parse = JSON.parse(giveaway_info);

            giveaway_clear_receive = giveaway_info_parse.giveaway_clear
            giveaway_enable_receive = giveaway_info_parse.giveaway_enable
            giveaway_mult_receive = giveaway_info_parse.giveaway_mult
            
            giveaway_clear.checked = giveaway_clear_receive === 1 ? true : false;
            giveaway_enable.checked = giveaway_enable_receive === 1 ? true : false;
            giveaway_mult.checked = giveaway_mult_receive === 1 ? true : false;
    
            giveaway_name_inp.value = giveaway_info_parse.giveaway_name;
                

        }

    } else if (type_id == 'get_style' ) {

        var giveaway_color1 = document.getElementById('giveaway-color1-text');
        var giveaway_color1_span = document.getElementById('giveaway-color1-span');
        var giveaway_color2 = document.getElementById('giveaway-color2-text');
        var giveaway_color2_span = document.getElementById('giveaway-color2-span');
        var giveaway_pointer = document.getElementById('giveaway-pointer-text');
        var giveaway_pointer_span = document.getElementById('giveaway-pointer-span');

        var giveaway_info = await window.pywebview.api.giveaway_py('get_config','null');
    
        if (giveaway_info) {

            var giveaway_info_parse = JSON.parse(giveaway_info);

            giveaway_color1.value = giveaway_info_parse.giveaway_color1;
            giveaway_color1_span.style.background = giveaway_info_parse.giveaway_color1;
            giveaway_color2.value = giveaway_info_parse.giveaway_color2;
            giveaway_color2_span.style.background = giveaway_info_parse.giveaway_color2;
            giveaway_pointer.value = giveaway_info_parse.giveaway_pointer;
            giveaway_pointer_span.style.background = giveaway_info_parse.giveaway_pointer;

        }

    } else if (type_id == 'get_command') {
        
        var command_giveaway_select = document.getElementById('command-giveaway-select');

        var command_giveaway_status = document.getElementById('command-giveaway-status');
        var command_giveaway_command = document.getElementById('command-giveaway-command');
        var command_giveaway_delay = document.getElementById('command-giveaway-delay');
        var command_giveaway_cost_status = document.getElementById('command-cost-status-giveaway'); 
        var command_giveaway_cost = document.getElementById('command-cost-giveaway');

        var command_giveaway_whitelistStatus = document.getElementById('whitelist-status-queue');

        var giveaway_command_edit = document.getElementById('command_giveaway_form');

        data = {
            type_id : type_id,
            type_command : command_giveaway_select.value,
            type_command_table: 'giveaway'
        }

        var giveaway_parse = await window.pywebview.api.commands_default_py(data);

        if (giveaway_parse){

            giveaway_command_edit.hidden = false

            command_cost_get('giveaway',giveaway_parse.cost_status)

            command_giveaway_status.checked = giveaway_parse.status == 1 ? true : false;
            command_giveaway_cost_status.checked = giveaway_parse.cost_status == 1 ? true : false;
            command_giveaway_whitelistStatus.checked = giveaway_parse.whitelist_status == 1 ? true : false;
            command_giveaway_command.value = giveaway_parse.command
            command_giveaway_delay.value = giveaway_parse.delay
            command_giveaway_cost.value = giveaway_parse.cost

            $("#command-giveaway-perm").selectpicker('val',giveaway_parse.user_level)
            $("#command-giveaway-perm").selectpicker("refresh");

        }

    } else if (type_id == 'show_names'){


        var name_list_parse = await window.pywebview.api.giveaway_py(type_id,'null');

        if (name_list_parse) {

            name_list_parse = JSON.parse(name_list_parse)

            $("#giveaway-modal").modal("show");
    
            var tbody_give = document.getElementById('giveaway-list-body');
    
            tbody_give.innerHTML = ''
    
            Object.entries(name_list_parse).forEach(([k,v]) => {
    
                tbody_give.innerHTML += '<tr><td style="width: 10px">' + k + '</td><td>' + v + '</td></tr>';
    
            })
            
        }

    } else if (type_id == 'save_config'){
        
        var giveaway_clear_check_inp = document.getElementById('giveaway-clear-names-end').checked;
        var giveaway_enable_inp = document.getElementById('giveaway-enable').checked;
        var giveaway_mult_inp = document.getElementById('giveaway-mult').checked;
        var giveaway_name = document.getElementById('giveaway-name').value;
    
        giveaway_clear_check_value = giveaway_clear_check_inp ? 1 : 0;
        giveaway_enable_value = giveaway_enable_inp ? 1 : 0;
        giveaway_mult_value = giveaway_mult_inp ? 1 : 0;
    
        data = {
            giveaway_name: giveaway_name,
            giveaway_user_level: roles,
            giveaway_clear_check: giveaway_clear_check_value,
            giveaway_enable: giveaway_enable_value,
            giveaway_mult: giveaway_mult_value,
        };
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.giveaway_py(type_id, formData);


    } else if (type_id == 'save_style'){

        var giveaway_color1 = document.getElementById('giveaway-color1-text');
        var giveaway_color2 = document.getElementById('giveaway-color2-text');
        var giveaway_pointer = document.getElementById('giveaway-pointer-text');

        data = {
            giveaway_color1: giveaway_color1.value,
            giveaway_color2: giveaway_color2.value,
            giveaway_pointer: giveaway_pointer.value,
        };
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.giveaway_py(type_id, formData);

    } else if (type_id == 'save_command'){

        var command_giveaway_select = document.getElementById('command-giveaway-select');

        var command_giveaway_status = document.getElementById('command-giveaway-status');
        var command_giveaway_command = document.getElementById('command-giveaway-command');
        var command_giveaway_delay = document.getElementById('command-giveaway-delay');
        var command_giveaway_cost_status = document.getElementById('command-cost-status-giveaway'); 
        var command_giveaway_cost = document.getElementById('command-cost-giveaway');
        var command_giveaway_whitelistStatus = document.getElementById('whitelist-status-queue');

        var command_status = command_giveaway_status.checked ? 1 : 0;
        var cost_status = command_giveaway_cost_status.checked ? 1 : 0;
        var whitelist_status = command_giveaway_whitelistStatus.checked ? 1 : 0;
        
        var giveaway_command_edit = document.getElementById('command_giveaway_form');

        var roles = []; 

        $('#command-giveaway-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data  = {
            type_id : type_id,
            type_command_table: 'giveaway',
            type_command: command_giveaway_select.value,
            command: command_giveaway_command.value,
            status: command_status,
            delay: command_giveaway_delay.value,
            user_level: roles,
            cost: command_giveaway_cost.value,
            cost_status: cost_status,
            whitelist_status: whitelist_status
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.commands_default_py(formData);

        
        giveaway_command_edit.hidden = true

    } else if (type_id == 'add_user'){

        var add_name = document.getElementById('giveaway-add-user').value;
        
        data = {
            new_name: add_name
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.giveaway_py(type_id,formData);


    } else if (type_id == 'execute' || type_id == 'execute_overlay' || type_id == 'clear_list' || type_id == 'update_overlay' ){
        window.pywebview.api.giveaway_py(type_id,'null');
    }
}



