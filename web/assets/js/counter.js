async function counter_js(type_id,event) {
    
    var el_id = "redeem-select-counter";
    var counter_value = document.getElementById('counter-value');


    if (type_id == 'get_counter_config'){

        var response_status = document.getElementById('response-counter-status');
        var response_counter = document.getElementById('counter-response');
        var response_set_counter = document.getElementById('counter-set-response');

        var counter_parse = await window.pywebview.api.counter(type_id,'none');

        if (counter_parse) {
            
            counter_parse = JSON.parse(counter_parse)

            counter_value.value = counter_parse.value_counter;
            response_status.checked = counter_parse.response == 1 ? true : false;

            response_counter.value = counter_parse.response_chat
            response_set_counter.value = counter_parse.response_set_chat

        }

    } else if (type_id == 'get_counter_commands') {

        var command_counter_select = document.getElementById('command-counter-select');

        var command_counter_status = document.getElementById('command-counter-status');
        var command_counter_command = document.getElementById('command-counter-command');
        var command_counter_delay = document.getElementById('command-counter-delay');
        var counter_command_edit = document.getElementById('command_counter_form');

        var counter_parse = await window.pywebview.api.counter(type_id,command_counter_select.value);

        if (counter_parse){

            counter_command_edit.hidden = false

            command_counter_status.checked = counter_parse.status == 1 ? true : false;
            command_counter_command.value = counter_parse.command
            command_counter_delay.value = counter_parse.delay

            $("#command-counter-perm").selectpicker('val',counter_parse.user_level)

        }

    } else if (type_id == 'save_counter_config') {

        var redeem_save = document.getElementById('redeem-select-counter').value;
        var response_status = document.getElementById('response-counter-status');
        var response_counter = document.getElementById('counter-response');
        var response_set_counter = document.getElementById('counter-set-response');

        response_status = response_status.checked ? 1 : 0

        data = {
            redeem : redeem_save,
            response : response_status,
            response_chat : response_counter.value,
            response_set_chat : response_set_counter.value
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.counter(type_id,formData)

    } else if (type_id == 'save_counter_commands') {

        var command_counter_select = document.getElementById('command-counter-select');

        var command_counter_status = document.getElementById('command-counter-status');
        var command_counter_command = document.getElementById('command-counter-command');
        var command_counter_delay = document.getElementById('command-counter-delay');

        var command_status = command_counter_status.checked ? 1 : 0;

        var roles = []; 

        $('#command-counter-perm :selected').each(function(i, selected){ 
            roles[i] = $(selected).val(); 
        });

        data  = {
            type_command: command_counter_select.value,
            command: command_counter_command.value,
            status: command_status,
            delay: command_counter_delay.value,
            user_level: roles
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.counter(type_id,formData)

    } else if (type_id == 'set-counter-value'){

        var form_counter_value = document.querySelector('#counter-set-value');
        var counter_value = form_counter_value.querySelector('#counter-value');

        window.pywebview.api.counter(type_id,counter_value.value)
    }
    

}

function update_counter_value(value){
    var counter_value = document.getElementById('counter-value');
    counter_value.value = value
}