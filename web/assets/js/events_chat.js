function append_notice_chat(data){

  var chatBlockOut = document.getElementById('chat-block-out');

  var message_rec = data.message;
  var user_input = data.user_input;

  var chat_data = data.data_show;
  var chat_time = data.data_time;

  var font_size_chat = data.font_size_chat;

  var colorEvents = data.color_events;
  var type_message = data.type_event;


  const variableMappingsChat = {
    "command": data.show_commands_chat,
    "event": data.show_events_chat,
    "music": data.show_music_chat,
    "follow": data.show_follow_chat,
    "like": data.show_likes_chat,
    "gift": data.show_gifts_chat,
    "chest": data.show_chest_chat,
    "share": data.show_share_chat,
    "join": data.show_join_chat,
    "goal_end": data.show_goal_end_chat,
    "goal_start": data.show_goal_start_chat,
  };

  if (variableMappingsChat[type_message] === 1) {

    var time_chat = document.createElement("span");
    time_chat.setAttribute('data-passed',chat_time)
    time_chat.classList.add("event-time-current");
    time_chat.innerHTML = 'Agora';

    var message_span = document.createElement('span');
    message_span.id = "message-chat";
    message_span.style.color = colorEvents;

    var message_user_inp = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`
    message_span.innerHTML = user_input == "" ? message_rec : message_user_inp;

    message_div = document.createElement('div');

    chat_data == 1 ? message_div.appendChild(time_chat) : null;

    message_div.appendChild(message_span);

    var div_event_create = document.createElement("div");

    div_event_create.id = 'recent-message-block'
    div_event_create.classList.add('event-message', 'chat-block-color');
    div_event_create.style.fontSize = font_size_chat + 'px';

    div_event_create.appendChild(message_div);

    if (chatBlockOut){

      chatBlockOut.appendChild(div_event_create.cloneNode(true));
      chatBlockOut.scrollTop = chatBlockOut.scrollHeight;
      
    }
  }

}
