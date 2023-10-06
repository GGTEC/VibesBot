window.addEventListener('pywebviewready',async function() {

  start_events_log('div-events-w')
  start_event_updatetime()

});


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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

const div_events_w_scroll = document.getElementById("div-events-w");
const itensPorPagina_w = 10;
let paginaAtual_w = 1;

function AddEventsOut(event){


  async function ExecuteAdd(){

    data ={
      "type_id" : 'get'
    };

    var Events = await window.pywebview.api.event_log(JSON.stringify(data));

    if (Events) {

      var EventsParse = JSON.parse(Events);
      var events_list = EventsParse["event-list"].reverse()

      const startIndex_w = paginaAtual_w * itensPorPagina_w;
      const endIndex_w = startIndex_w + itensPorPagina_w;
      const items_w = events_list.slice(startIndex_w, endIndex_w);

      for (let i = 0; i < items_w.length; i++) {

        var part = items_w[i].split(" | ");
  
        var dateString = part[0];
        var type_message = part[1];
        var message_rec = part[2];
        
        if (part.length > 3){
          var user_input =  part[3];
        }else {
          var user_input =  "";
        }
  
        var colorEvents = EventsParse["color-events"];
        var ShowData = EventsParse["data-show-events"];

        var showEvents = EventsParse["show-events"];
        var showCommands = EventsParse["show-commands"];
        var showFollow = EventsParse["show-follow"];
        var showLikes = EventsParse["show-likes"];
        var showGifts = EventsParse["show-gifts"];
        var showChest = EventsParse["show-chest"];
        var showShare = EventsParse["show-share"];
        var showJoin = EventsParse["show-join"];
        var showStartGoal = EventsParse["show-goal-start"];
        var showEndGoal = EventsParse["show-goal-end"];


        var message_span = document.createElement('span');

        message_span.id = "message-chat";
        message_span.style.color = colorEvents;
        
        var message_user_inp = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`

        message_span.innerHTML = user_input == "" ? message_rec : message_user_inp;
        
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
  
        div_event.id = 'recent-message-block'
        div_event.classList.add('chat-message','event-message');
        div_event.style.fontSize = "16px";
  
        div_event.appendChild(message_div);

        const variableMappings = {
          "command": showCommands,
          "event": showEvents,
          "follow": showFollow,
          "likes": showLikes,
          "gifts": showGifts,
          "chest": showChest,
          "share": showShare,
          "join": showJoin,
          "goal_start" : showStartGoal,
          "goal_end": showEndGoal,
        };
    
    
        if (variableMappings[type_message] === 1) {
          div_events_w_scroll.appendChild(div_event);
        }
        
      }

      paginaAtual_w++;
    }
  }

  if (event.type === "scroll"){

    if (div_events_w_scroll.scrollTop + div_events_w_scroll.clientHeight >= div_events_w_scroll.scrollHeight) {

      ExecuteAdd()
    }
  } else if(event.type === "wheel"){

    if (event.deltaY > 0) {

      if (div_events_w_scroll.scrollHeight <= div_events_w_scroll.clientHeight && div_events_w_scroll.scrollTop + div_events_w_scroll.clientHeight >= div_events_w_scroll.scrollHeight) {

        ExecuteAdd()
      }
    }
  }
}

function append_notice_out(data){

  var div_events_out = document.getElementById('div-events-w');

  var message_rec = data.message;
  var user_input = data.user_input;

  var chat_data = data.data_show;
  var chat_time = data.data_time;

  var font_size = data.font_size;

  var colorEvents = data.color_events;
  var showEvents = data.show_events;
  var showCommands = data.show_commands;
  var showFollow = data.show_follow;
  var showLikes = data.show_likes;
  var showGifts = data.show_gifts;
  var showChest = data.show_chest;
  var showShare = data.show_share;
  var showJoin = data.show_join;
  var showStartGoal = data.show_goal_start;
  var showEndGoal = data.show_goal_end;

  var type_message = data.type_event;

  const variableMappings = {
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

  if (variableMappings[type_message] === 1) {


    var time_chat = document.createElement("span");
    time_chat.setAttribute('data-passed',chat_time)
    time_chat.classList.add("event-time-current");
    time_chat.innerHTML = 'Agora';

    var message_span = document.createElement('span');
    message_span.id = "message-chat";
    message_span.style.color = colorEvents;

    message_user_inp = `${message_rec} <br><span class='small events-sub-color'>Mensagem : ${user_input}</span>`

    message_span.innerHTML = user_input == "" ? message_rec : message_user_inp;

    
    message_div = document.createElement('div');

    chat_data == 1 ? message_div.appendChild(time_chat) : null;

    message_div.appendChild(message_span);

    var div_event_create = document.createElement("div");

    div_event_create.id = 'recent-message-block'
    div_event_create.classList.add('event-message', 'chat-block-color');
    div_event_create.style.fontSize = `${font_size}px`;

    div_event_create.appendChild(message_div);

    if(div_events_out){

      div_events_out.insertBefore(div_event_create, div_events_out.firstChild);

    }

  }

}

div_events_w_scroll.addEventListener("wheel",AddEventsOut);
div_events_w_scroll.addEventListener("scroll",AddEventsOut);



