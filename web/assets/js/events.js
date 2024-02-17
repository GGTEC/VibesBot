
function append_notice(data){

    var div_events = document.getElementById('div-events');
    var div_events_out = document.getElementById('div-events-w');

    var chatBlockInner = document.getElementById('chat-block-inner');
    var chatBlockOut = document.getElementById('chat-block-out');

    var message_rec = data.message;
    var user_input = data.user_input;

    var chat_data = data.data_show;
    var chat_time = data.data_time;

    var font_size = data.font_size;
    var font_size_chat = data.font_size_chat;

    var colorEvents = data.color_events;
    var dataShowEvents = data.data_show;
    
    var type_message = data.type_event;

    const variableMappings = {
      "command": data.show_commands,
      "music": data.show_music,
      "event": data.show_events,
      "follow": data.show_follow,
      "like": data.show_likes,
      "gift": data.show_gifts,
      "chest": data.show_chest,
      "share": data.show_share,
      "join": data.show_join,
      "goal_start" : data.show_start_goal,
      "goal_end": data.show_end_goal,
    };

    const variableMappingsChat = {
      "command": data.show_commands_chat,
      "music": data.show_music_chat,
      "event": data.show_events_chat,
      "follow": data.show_follow_chat,
      "like": data.show_likes_chat,
      "gift": data.show_gifts_chat,
      "chest": data.show_chest_chat,
      "share": data.show_share_chat,
      "join": data.show_join_chat,
      "goal_start" : data.show_start_goal_chat,
      "goal_end": data.show_end_goal_chat,
    };

    if (variableMappings[type_message] === 1) {

      var time_chat = document.createElement("span");
      time_chat.setAttribute('data-passed',chat_time)
      time_chat.classList.add("event-time-current");
      time_chat.innerHTML = 'Agora';

      var message_span = document.createElement('span');
      message_span.id = "message-chat";
      message_span.style.color = colorEvents;

      message_user_inp = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`

      message_span.innerHTML = user_input == null || user_input == "" ? message_rec : message_user_inp;

      
      message_div = document.createElement('div');

      chat_data == 1 ? message_div.appendChild(time_chat) : null;

      message_div.appendChild(message_span);

      var div_event_create = document.createElement("div");

      div_event_create.id = 'recent-message-block'
      div_event_create.classList.add('event-message', 'chat-block-color');
      div_event_create.style.fontSize = `${font_size}px`;

      div_event_create.appendChild(message_div);

      div_events.insertBefore(div_event_create, div_events.firstChild);

      if(div_events_out){

        div_events_out.insertBefore(div_event_create.cloneNode(true), div_events_out.firstChild);

      }

    }


    if (variableMappingsChat[type_message] === 1) {

      var time_chat = document.createElement("span");
      time_chat.setAttribute('data-passed',chat_time)
      time_chat.classList.add("event-time-current");
      time_chat.innerHTML = 'Agora';

      var message_span = document.createElement('span');
      message_span.id = "message-chat";
      message_span.style.color = colorEvents;

      var message_user_inp = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`

      message_span.innerHTML = user_input == null || user_input == "" ? message_rec : message_user_inp;

      message_div = document.createElement('div');

      dataShowEvents == 1 ? message_div.appendChild(time_chat) : null;

      message_div.appendChild(message_span);

      var div_event_create = document.createElement("div");

      div_event_create.id = 'recent-message-block'
      div_event_create.classList.add('event-message', 'chat-block-color');
      div_event_create.style.fontSize = font_size_chat + 'px';

      div_event_create.appendChild(message_div);

      chatBlockInner.appendChild(div_event_create);
      chatBlockInner.scrollTop = chatBlockInner.scrollHeight;

      
      if (chatBlockOut){

        chatBlockOut.appendChild(div_event_create.cloneNode(true));
        chatBlockOut.scrollTop = chatBlockOut.scrollHeight;
        
      }
    }

}

async function start_event_updatetime(){
  
  while (true){

    var div_event = document.querySelectorAll('.event-time-current');

    for(var i = 0; i < div_event.length; i++ ){

      get_data = div_event[i].getAttribute("data-passed");

      var date = new Date(get_data);
      var now = new Date();

      var difftimeMs = now.getTime() - date.getTime();
      var difftimes = difftimeMs / 1000;

      var days = Math.floor(difftimes / 86400);
      var hours = Math.floor((difftimes % 86400) / 3600);
      var minutes = Math.floor((difftimes % 3600) / 60);

      var chat_time = '';

      if (days >= 1) {
        chat_time += days + 'd';
      } else if (hours >= 1){
        chat_time += hours + 'h';
      } else if (minutes >= 1){
        chat_time += minutes + 'm';
      } else {
        chat_time += 'Agora';
      }

      div_event[i].innerHTML = chat_time

    }
    await sleep(60000)

  }

}

function GetDateEvents(dateString){
  
  var date = new Date(dateString);
  var now = new Date();

  var difftimeMs = now.getTime() - date.getTime();
  var difftimes = difftimeMs / 1000;

  var days = Math.floor(difftimes / 86400);
  var hours = Math.floor((difftimes % 86400) / 3600);
  var minutes = Math.floor((difftimes % 3600) / 60);

  var chat_time = '';

  if (days > 0) {
    chat_time += days + 'd';
  } else if (hours > 1){
    chat_time += hours + 'h';
  } else if (minutes >= 1){
    chat_time += minutes + 'm ';
  } else {
    chat_time += 'agora';
  }

  return chat_time
}

async function start_events_log(div_id) {

  var div_events = document.getElementById(div_id);
  let messagesAddedCount = 0;

  data = {
    type_id : "get"
  }

  var Events = await window.pywebview.api.event_log(JSON.stringify(data));
  
  if (Events) {

    EventsParse = JSON.parse(Events);

    var list = EventsParse['event-list'];

    div_events.innerHTML = "";

    list.forEach((event) => {

      var dateString = event.timestamp;
      var message_rec = event.message;
      var type_message = event.type;
      var user_input = event.user_input;
      
      if (message_rec != null){

        var colorEvents = EventsParse["color-events"];
        var ShowData = EventsParse["data-show-events"];
  
        var showEvents = EventsParse["show-events"];
        var showCommands = EventsParse["show-commands"];
        var showMusic = EventsParse["show-music"];
        var showFollow = EventsParse["show-follow"];
        var showLikes = EventsParse["show-likes"];
        var showGifts = EventsParse["show-gifts"];
        var showChest = EventsParse["show-chest"];
        var showStartGoal = EventsParse["show-goal-start"];
        var showEndGoal = EventsParse["show-goal-end"];
        var showShare = EventsParse["show-share"];
        var showJoin = EventsParse["show-join"];
  
        const variableMappings = {
          "music": showMusic,
          "command": showCommands,
          "event": showEvents,
          "follow": showFollow,
          "like": showLikes,
          "gift": showGifts,
          "chest": showChest,
          "share": showShare,
          "join": showJoin,
          "goal_start" : showStartGoal,
          "goal_end": showEndGoal,
        };

        if (variableMappings[type_message] == 1) {
  
          var message_span = document.createElement('span');
          message_span.id = "message-chat";
          message_span.style.color = colorEvents;
    
          var message_user_inp = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`
        
          message_span.innerHTML = user_input == null || user_input == "" ? message_rec : message_user_inp;
    
          message_div = document.createElement('div');
    
          if (ShowData == 1){
    
            var time_chat = document.createElement("span");
    
            time_chat.setAttribute('data-passed',dateString)
            time_chat.classList.add("event-time-current");
            time_chat.innerHTML = GetDateEvents(dateString);
    
            message_div.appendChild(time_chat);
    
          }
    
          message_div.appendChild(message_span);
    
          var div_event = document.createElement("div");
    
          div_event.id = 'recent-message-block';
          div_event.classList.add('chat-message', 'event-message');
          div_event.style.fontSize = "16px";
    
          div_event.appendChild(message_div);
          div_events.appendChild(div_event);

          messagesAddedCount++;
        }

        if (messagesAddedCount >= 5) {
          return;
        }
      }
          
    });
  }
}


