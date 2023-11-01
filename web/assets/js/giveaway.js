async function giveaway_js(event,type_id) {
    
    if (type_id == 'get_config') {

        var giveaway_name_inp = document.getElementById("giveaway-name");
        var giveaway_user_level = document.getElementById("user-level-giveaway");
        var giveaway_clear = document.getElementById("giveaway-clear-names-end");
        var giveaway_enable = document.getElementById('giveaway-enable');
        var giveaway_mult = document.getElementById('giveaway-mult');

        var giveaway_info = await window.pywebview.api.giveaway_py(type_id,'null');
    
        if (giveaway_info) {
            
            var giveaway_info_parse = JSON.parse(giveaway_info);
    
            giveaway_clear_receive = giveaway_info_parse.giveaway_clear
            giveaway_enable_receive = giveaway_info_parse.giveaway_enable
            giveaway_mult_receive = giveaway_info_parse.giveaway_mult
            
    
            if (giveaway_clear_receive == 1) {
                giveaway_clear.checked = true
            } else if (giveaway_clear_receive == 0) {
                giveaway_clear.checked = false
            }
    
            if (giveaway_enable_receive == 1) {
                giveaway_enable.checked = true
            } else if (giveaway_enable_receive == 0) {
                giveaway_enable.checked = false
            }
    
            if (giveaway_mult_receive == 1) {
                giveaway_mult.checked = true
            } else if (giveaway_mult_receive == 0) {
                giveaway_mult.checked = false
            }
    
            giveaway_name_inp.value = giveaway_info_parse.giveaway_name;
            giveaway_user_level.value = giveaway_info_parse.giveaway_level;

        }

    } else if (type_id == 'get_commands') {
        
        var command_giveaway_select = document.getElementById('command-giveaway-select');

        var command_giveaway_status = document.getElementById('command-giveaway-status');
        var command_giveaway_command = document.getElementById('command-giveaway-command');
        var command_giveaway_delay = document.getElementById('command-giveaway-delay');
        var command_giveaway_cost_status = document.getElementById('command-cost-status-giveaway'); 
        var command_giveaway_cost = document.getElementById('command-cost-giveaway'); 
        var command_giveaway_cost_type = document.getElementById("command-cost-type-giveaway");

        var giveaway_command_edit = document.getElementById('command_giveaway_form');

        var giveaway_command_data = await window.pywebview.api.giveaway_py(type_id,command_giveaway_select.value);

        if (giveaway_command_data){

            var giveaway_parse = JSON.parse(giveaway_command_data);

            giveaway_command_edit.hidden = false

            command_cost_get('giveaway',giveaway_parse.cost_status)

            command_giveaway_status.checked = giveaway_parse.status == 1 ? true : false;
            command_giveaway_cost_status.checked = giveaway_parse.cost_status == 1 ? true : false;
            command_giveaway_command.value = giveaway_parse.command
            command_giveaway_delay.value = giveaway_parse.delay
            command_giveaway_cost.value = giveaway_parse.cost

            $("#command-giveaway-perm").selectpicker('val',giveaway_parse.user_level)
            $("#command-giveaway-perm").selectpicker("refresh");

            $("#command-cost-type-tts").selectpicker('val', giveaway_parse.cost_type);
            $("#command-cost-type-tts").selectpicker("refresh");

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
        
        event.preventDefault();

        var form = document.querySelector("#giveaway-config-form");
        giveaway_clear_check_inp = form.querySelector('input[id="giveaway-clear-names-end"]').checked;
        giveaway_enable_inp = form.querySelector('input[id="giveaway-enable"]').checked;
        giveaway_mult_inp = form.querySelector('input[id="giveaway-mult"]').checked;
    
        if (giveaway_clear_check_inp == true) {
            giveaway_clear_check_value = 1;
        } else {
            giveaway_clear_check_value = 0;
        }
    
        if (giveaway_enable_inp == true) {
            giveaway_enable_value = 1;
        } else {
            giveaway_enable_value = 0;
        }
    
        if (giveaway_mult_inp == true) {
            giveaway_mult_value = 1;
        } else {
            giveaway_mult_value = 0;
        }
    
        data = {
            giveaway_name: form.querySelector('input[id="giveaway-name"]').value,
            giveaway_redeem: form.querySelector('select[id="redeem-select-giveaway"]').value,
            giveaway_user_level: form.querySelector('select[id="user-level-giveaway"]').value,
            giveaway_clear_check: giveaway_clear_check_value,
            giveaway_enable: giveaway_enable_value,
            giveaway_mult: giveaway_mult_value,
        };
    
        var formData = JSON.stringify(data);
    
        window.pywebview.api.giveaway_py(type_id,formData);


    } else if (type_id == 'save_commands'){

        var command_giveaway_select = document.getElementById('command-giveaway-select');

        var command_giveaway_status = document.getElementById('command-giveaway-status');
        var command_giveaway_command = document.getElementById('command-giveaway-command');
        var command_giveaway_delay = document.getElementById('command-giveaway-delay');
        var command_giveaway_cost_status = document.getElementById('command-cost-status-giveaway'); 
        var command_giveaway_cost = document.getElementById('command-cost-giveaway'); 
        var command_giveaway_cost_type = document.getElementById("command-cost-type-giveaway");

        var command_status = command_giveaway_status.checked ? 1 : 0;
        var cost_status = command_giveaway_cost_status.checked ? 1 : 0;

        var roles = []; 

        $('#command-giveaway-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data  = {
            type_command: command_giveaway_select.value,
            command: command_giveaway_command.value,
            status: command_status,
            delay: command_giveaway_delay.value,
            user_level: roles,
            cost: cost.value,
            cost_type: command_giveaway_cost_type.value,
            cost_status: cost_status
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.giveaway_py(type_id,formData);

    } else if (type_id == 'add_user'){

        event.preventDefault();

        var form = document.querySelector("#giveaway-add-user-form");
        var add_name = form.elements[0].value;
        
        data = {
            new_name: add_name,
            user_level: 'mod'
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.giveaway_py(type_id,formData);


    } else if (type_id == 'execute'){
        window.pywebview.api.giveaway_py(type_id,'null');
    } else if (type_id == 'clear_list'){
        window.pywebview.api.giveaway_py(type_id,'null');
    }
}



