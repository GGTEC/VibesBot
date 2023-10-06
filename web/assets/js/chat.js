function pass_message(message_to){

    if (message_to.startsWith('/me')){

        message_ret = message_to.replace("/me", "<i>");
        message_ret = message_ret + "</i>";

        return message_ret

    } else if (message_to.startsWith('\x01ACTION')){  

        message_ret = message_to.replace("\x01ACTION", "<i>");
        message_ret = message_ret.replace("\x01", "</i>");

        return message_ret

    } else {

        return message_to

    }
}


async function chat_config(type_config){

    var slider_font = document.getElementById('slider-font');
    var rangevalue_config = document.getElementById('rangevalue_config');

    var chat_color_name = document.getElementById('chat-color-name');
    var select_color_name = document.getElementById('select-color-name');

    var chat_color_border = document.getElementById('chat-color-border');
    var select_color_border = document.getElementById('select-color-border');

    var data_show = document.getElementById('data-show');
    var type_data = document.getElementById('select-time-mode');
    var time_format = document.getElementById('time-format');

    var chat_newline = document.getElementById('chat-newline');

    var gift_role = document.getElementById('gift_role');
    var like_role = document.getElementById('like_role');
    var share_role = document.getElementById('share_role');

    rangevalue_config.innerHTML = slider_font.value + 'px';


    if (type_config == 'save'){

        chat_color_name = chat_color_name.checked ? 1 : 0;
        chat_color_border = chat_color_border.checked ? 1 : 0;

        data_show = data_show.checked ? 1 : 0;
        chat_newline = chat_newline.checked ? 1 : 0;

        data = {
            chat_color_name : chat_color_name,
            chat_name_select :select_color_name.value, 
            chat_color_border: chat_color_border,
            chat_border_select: select_color_border.value,
            data_show : data_show,
            type_data : type_data.value,
            time_format : time_format.value,
            font_size : slider_font.value,
            wrapp_message : chat_newline,
            gift_role : gift_role.value,
            like_role : like_role.value,
            share_role: share_role.value,
        }

        var formData = JSON.stringify(data);
        window.pywebview.api.chat_config(formData,type_config);
        
    } else if (type_config == 'get'){

        var chat_data_parse = await window.pywebview.api.chat_config('null',type_config)

        if (chat_data_parse){

            chat_data_parse = JSON.parse(chat_data_parse)

            chat_color_name.checked = chat_data_parse.chat_color_name == 1 ? true : false;
            chat_color_border.checked = chat_data_parse.chat_color_border == 1 ? true : false;

            data_show.checked = chat_data_parse.data_show == 1 ? true : false;
            
            chat_newline.checked = chat_data_parse.wrapp_message == 1 ? true : false;
            
            slider_font.value = chat_data_parse.font_size;
            rangevalue_config.innerHTML = chat_data_parse.font_size + 'px';
            time_format.value = chat_data_parse.time_format;

            gift_role.value = chat_data_parse.gift_role;
            like_role.value = chat_data_parse.like_role;
            share_role.value = chat_data_parse.share_role;

            $("#select-color-name").selectpicker('val', chat_data_parse.chat_name_select);
            $("#select-color-boder").selectpicker('val', chat_data_parse.chat_border_select);

            $("#select-time-mode").selectpicker('val', chat_data_parse.type_data);

        }

    }
}

async function start_update_time_chat() {

    while (true){
        let dateTimeObjs = [];

        let messageTimeElements = document.querySelectorAll(".message-time");

        messageTimeElements.forEach(function(element) {
            let dateString = element.getAttribute("data-time");
            dateTimeObjs.push(new Date(dateString));
        });

        //Data e hora atual
        let now = new Date();
        messageTimeElements.forEach(function(element, index) {
            let dateTimeObj = dateTimeObjs[index];
            //Calculando a diferença entre as datas
            let delta = now - dateTimeObj;
            let minutes = Math.floor(delta / (1000 * 60));
            let hours = Math.floor(delta / (1000 * 60 * 60));
            let seconds = Math.floor(delta / 1000);
            if(hours < 1){
                if(minutes < 1){
                    element.innerHTML = seconds + " segundos";
                }else{
                    element.innerHTML = minutes + " minutos";
                }
            }else {
                element.innerHTML = hours + " horas";
            }
        });

        await sleep(5000)
    }
}

function createBadgeSpan(name, imageUrl,text_size) {
    
    if (!imageUrl) {
        return null; // Retorna null se ambos forem vazios
    }

    const div = document.createElement('div');
    div.style.display = 'inline-block'
    div.style.marginLeft = '2px';


    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.style.width = `${text_size - 2}px`;  
        img.style.verticalAlign = 'middle';
        img.style.marginRight = '2px';
        div.appendChild(img);
    }

    if (name && name !== "Moderator") {
        const span = document.createElement('span');
        span.style.fontSize = `${text_size - 2}px`;  
        span.textContent = name;
        div.appendChild(span);
    }   
    
    
    return div;
}

function append_message(message_data_parse){
    
    var div_chat = document.getElementById('chat-block-inner');

    var type_message = message_data_parse.type

    if (type_message == 'PRIVMSG'){
        
        if (div_chat != null){

            var chat_color_border = message_data_parse.chat_color_border;
            var chat_color_name = message_data_parse.chat_color_name;
            var select_color_border = message_data_parse.select_color_border;
            var select_color_name = message_data_parse.select_color_name;
            var chat_newline = message_data_parse.wrapp_message;
            var text_size = message_data_parse.font_size;
            var chat_data = message_data_parse.data_show;
            var chat_time = message_data_parse.chat_time;
            var type_data = message_data_parse.type_data;
            var user_rec = message_data_parse.display_name;
            var user_id = message_data_parse.user_id;
            var message_rec = message_data_parse.message;
            var badges = message_data_parse.badges;

    
            color_rec = chat_color_name === 1 ? select_color_name : "white";
            border_color = chat_color_border === 1 ? select_color_border : '#4f016c';
            
            var div = document.createElement("div");
    
            if (type_data == 'passed'){

                let date = new Date(chat_time);
                let formattedDate = date.toLocaleDateString() + " " + date.toLocaleTimeString();
                var time_chat = document.createElement("span");
                time_chat.id = 'time_chat';
                time_chat.setAttribute("data-time", chat_time);
                time_chat.setAttribute("title", formattedDate);
                time_chat.classList.add("message-time");
                time_chat.innerHTML = 'Agora';
    
            } else if (type_data == 'current'){

                var time_chat = document.createElement("span");
                time_chat.id = 'time_chat';
                time_chat.classList.add("message-time-current");
                time_chat.innerHTML = chat_time;

            }

            var username = document.createElement("span");
            username.id = 'user-chat';
            username.innerHTML = user_rec;
            username.setAttribute('onclick','pywebview.api.open_py("user","'+user_id+'")');

            var separator = document.createElement("span");
            separator.innerHTML = ' :';

            var span_username = document.createElement("span");
            span_username.style.color = color_rec;
            span_username.style.cursor = 'pointer';

            span_username.appendChild(username);

            badges.forEach(badge => {
                const span = createBadgeSpan(badge.name, badge.first_url,text_size);
                if (span) {
                    span_username.appendChild(span);
                }
            });

            span_username.appendChild(separator);

    
            message_rec = twemoji.parse(message_rec);

            var span_message = document.createElement("span");
            span_message.id = 'message-chat';
            span_message.innerHTML = message_rec;
            
            var new_line = document.createElement("br");
    
            div.id = 'chat-message-block'
            div.classList.add('chat-message', 'chat-block-color');
            div.style.fontSize = text_size + "px";
            div.style.border = "3px solid "+ border_color + "";

            chat_data == 1 ? div.appendChild(time_chat) : null;
    
            div.appendChild(span_username);
    
            chat_newline == 1 ? div.appendChild(new_line) : null;
    
            div.appendChild(span_message);

            div_chat.appendChild(div);

            div_chat.scrollTop = div_chat.scrollHeight;
            if (div_chat.childNodes.length > 100) {
                div_chat.removeChild(div_chat.firstChild);
            }
        }
    }

}

function append_message_out(message_data_parse){

    var div_chat_out = document.getElementById('chat-block-out');

    var type_message = message_data_parse.type

    if (type_message == 'PRIVMSG'){

        var chat_color_border = message_data_parse.chat_color_border;
        var chat_color_name = message_data_parse.chat_color_name;
        var select_color_border = message_data_parse.select_color_border;
        var select_color_name = message_data_parse.select_color_name;
        var chat_newline = message_data_parse.wrapp_message;
        var text_size = message_data_parse.font_size;
        var chat_data = message_data_parse.data_show;
        var chat_time = message_data_parse.chat_time;
        var type_data = message_data_parse.type_data;
        var user_rec = message_data_parse.display_name;
        var user_id = message_data_parse.user_id;
        var message_rec = message_data_parse.message;
        var badges = message_data_parse.badges;
        
        color_rec = chat_color_name === 1 ? select_color_name : "white";
        border_color = chat_color_border === 1 ? select_color_border : '#4f016c';
        
        var div = document.createElement("div");

        if (type_data == 'passed'){

            let date = new Date(chat_time);
            let formattedDate = date.toLocaleDateString() + " " + date.toLocaleTimeString();
            var time_chat = document.createElement("span");
            time_chat.id = 'time_chat';
            time_chat.setAttribute("data-time", chat_time);
            time_chat.setAttribute("title", formattedDate);
            time_chat.classList.add("message-time");
            time_chat.innerHTML = 'Agora';

        } else if (type_data == 'current'){

            var time_chat = document.createElement("span");
            time_chat.id = 'time_chat';
            time_chat.classList.add("message-time-current");
            time_chat.innerHTML = chat_time;
            
        }

        var username = document.createElement("span");
        username.id = 'user-chat';
        username.innerHTML = user_rec;
        username.setAttribute('onclick','pywebview.api.open_py("user","'+user_id+'")');

        var separator = document.createElement("span");
        separator.innerHTML = ' :';

        var span_username = document.createElement("span");
        span_username.style.color = color_rec;
        span_username.style.cursor = 'pointer';

        span_username.appendChild(username);

        badges.forEach(badge => {
            const span = createBadgeSpan(badge.name, badge.first_url,text_size);
            if (span) {
                span_username.appendChild(span);
            }
        });

        span_username.appendChild(separator);


        message_rec = twemoji.parse(message_rec);

        var span_message = document.createElement("span");
        span_message.id = 'message-chat';
        span_message.innerHTML = message_rec;
        
        var new_line = document.createElement("br");

        div.id = 'chat-message-block'
        div.classList.add('chat-message', 'chat-block-color');
        div.style.fontSize = text_size + "px";
        div.style.border = "3px solid "+ border_color + "";

        chat_data == 1 ? div.appendChild(time_chat) : null;

        div.appendChild(span_username);

        chat_newline == 1 ? div.appendChild(new_line) : null;

        div.appendChild(span_message);

        if (div_chat_out != null){
            div_chat_out.appendChild(div);
            div_chat_out.scrollTop = div_chat_out.scrollHeight;
            if (div_chat_out.childNodes.length > 100) {
                div_chat_out.removeChild(div_chat_out.firstChild);
            }
        }

    }

}

function slider_font() {
    slider = document.getElementById('slider-font');
    output = document.getElementById('rangevalue_config');
    $('.chat-message ').css("font-size", slider.value + "px");
    output.innerHTML = slider.value
};

