window.addEventListener('pywebviewready',async function() {

  const tooltipTriggerList = document.querySelectorAll('[title]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

  loaded = await window.pywebview.api.loaded();

  if (loaded){

    loaded = JSON.parse(loaded)

    if (loaded.autenticated == "false"){
      
      $('#body-pd').addClass('ps-0');
      $('#loading').addClass('d-none');
      
      $('#loading').addClass('remove-loading')

      $('#auth').removeClass('d-none')

    } else {

      var progressBar_start = document.getElementById("progress-bar-start");
      var progress_span = document.getElementById("progress-span");
      
      progressBar_start.style.width = `0%`;
    
      var functionsCount = 18;
      var functionsExecuted = 0; 

      $('[data-toggle="tooltip"]').tooltip();
      $("input, select, textarea").attr("autocomplete", "off");
      $("input, select, textarea").attr("spellcheck", "false");

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Tooltips, inputs.'

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Start chat.'
  
      var disclosure = await window.pywebview.api.disclosure_py('get','null');
  
      if (disclosure){
          document.getElementById('message-disclosure-send').value = disclosure
  
          progress_span.innerHTML = 'disclosure.'
          functionsExecuted++;
          progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      }
  
      start_selectpicker()
  
      progress_span.innerHTML = 'selectpicker.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_sidebar()
  
      progress_span.innerHTML = 'sidebar.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_scroll()
      start_scroll_event_log()
  
      progress_span.innerHTML = 'scroll.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_resizable()
  
      progress_span.innerHTML = 'resizable.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_update_time_chat()
  
      progress_span.innerHTML = 'auto update time chat.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      start_events_log('div-events')
  
      progress_span.innerHTML = 'get event logs.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      start_event_updatetime()
  
      progress_span.innerHTML = 'auto update time events.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      
      start_color_inputs()
  
  
      $('#main').removeClass('d-none')
      $('#loading').addClass('remove-loading')
  
      setTimeout(function() {
        $('#loading').addClass('d-none');
        
        update_modal('get')
      }, 1000);
  
  
      connectWebSocket_likes();
      connectWebSocket_diamonds();
      connectWebSocket_folows();
      connectWebSocket_specs();
      connectWebSocket_shares();
      connectWebSocket_gifts();

      progress_span.innerHTML = 'ConnectWebsockets.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      

      progress_span.innerHTML = 'remove loading.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      
      progress_span.innerHTML = 'Finish start.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      
  
    }
    
  }

});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function start_selectpicker(){
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

function start_scroll(){

  const scrollToBottomButton = document.querySelector("#scrollBtn");
  const chatWindow = document.getElementById("chat-block-inner");

  scrollToBottomButton.addEventListener("click", () => {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });


  chatWindow.addEventListener("scroll", () => {
    if (chatWindow.scrollTop < chatWindow.scrollHeight - chatWindow.clientHeight) {
      scrollToBottomButton.classList.add("show");
    } else {
      scrollToBottomButton.classList.remove("show");
    }
  });

}

function start_sidebar(){

  const linkname = document.querySelectorAll('.nav_name')

  const showNavbar = (toggleId, navId, bodyId) => {
    const toggle = document.getElementById(toggleId),
        nav = document.getElementById(navId),
        bodypd = document.getElementById(bodyId)

    // Validate that all variables exist
    if (toggle && nav && bodypd) {
        toggle.addEventListener('click', () => {
            // show navbar
            nav.classList.toggle('show_navbar')
            // change icon
            toggle.classList.toggle('bx-x')
            // add padding to body
            bodypd.classList.toggle('body-pd')

            linkname.forEach(name => name.classList.toggle('show_link'))
        })
    }
}

showNavbar('header-toggle', 'nav-bar', 'body-pd')


}

function start_resizable(){

  $('#events-col').resizable({
    handles: 'e',
    resize: function(event, ui) {

      var largura2 = 100 - (ui.size.width / $(this).parent().width() * 100);
  
      var chat_col = $('#chat-col');
      chat_col.css('width', largura2 + '%');
    }
  });

  $('#colapse-recent').resizable({
    handles: 's'
  });
  
}

function start_color_inputs(){

  $("#goal-text-button").click(function(event) {
    ttk_goal('save_html')
  });

  $("#goal-text-color-button").click(function(event) {
    $("#goal-text-color").click();
  });
  
  $("#goal-text-color").change(function(color) {
    $("#goal-text-color-span").css('background-color',$(this).val());
    $("#goal-text-color-text").val($(this).val())
    ttk_goal('save_html')
  });


  $("#goal-bar-color-button").click(function(event) {
    $("#goal-bar-color").click();
  });

  $("#goal-bar-color").change(function(event) {
    $("#goal-bar-color-span").css('background-color',$(this).val());
    $("#goal-bar-color-text").val($(this).val())
    ttk_goal('save_html')
  });


  $("#goal-background-bar-color-button").click(function(event) {
    $("#goal-background-bar-color").click();
  });

  $("#goal-background-bar-color").change(function(event) {
    $("#goal-background-bar-color-span").css('background-color',$(this).val());
    $("#goal-background-bar-color-text").val($(this).val())
    ttk_goal('save_html')
  });


  $("#goal-background-color-button").click(function(event) {
    $("#goal-background-color").click();
  });

  $("#goal-background-color-text").change(function(event) {
    $("#goal-background-color-span").css('background-color',$(this).val());
    $("#goal-background-color-text").val($(this).val())
    ranks_js('save','')
  });


  $("#likes-rank-background-button").click(function(event) {
    $("#likes-rank-background-color").click();
  });

  $("#likes-rank-background-color").change(function(event) {
    $("#likes-rank-background-span").css('background-color',$(this).val());
    $("#likes-rank-background-text").val($(this).val())
  });

  $("#gifts-rank-background-button").click(function(event) {
    $("#gifts-rank-background-color").click();
  });

  $("#gifts-rank-background-color").change(function(event) {
    $("#gifts-rank-background-span").css('background-color',$(this).val());
    $("#gifts-rank-background-text").val($(this).val())
  });


  $("#shares-rank-background-button").click(function(event) {
    $("#shares-rank-background-color").click();
  });

  $("#shares-rank-background-color").change(function(event) {
    $("#shares-rank-background-span").css('background-color',$(this).val());
    $("#shares-rank-background-text").val($(this).val())
  });


  $("#points-rank-background-button").click(function(event) {
    $("#points-rank-background-color").click();
  });

  $("#points-rank-background-color").change(function(event) {
    $("#points-rank-background-span").css('background-color',$(this).val());
    $("#points-rank-background-text").val($(this).val())
  });


}

function update_specs_tiktok(specs){

  if (specs >= 1){
    document.getElementById('tiktok-spec').hidden = false;
    document.getElementById('time-in-live').innerText = 'Online';
    document.getElementById('live-dot').style.color = 'red';
    document.getElementById('text-counter-ttk').innerText = " " + specs;
  } else if (specs == 'disconect'){
    document.getElementById('tiktok-spec').hidden = true;
    document.getElementById('time-in-live').innerText = 'Offline';
    document.getElementById('live-dot').style.color = 'white';
  }

}

function update_carousel_tiktok(type_id,data){
  
  if(type_id == 'update_topspecs'){

    document.getElementById('text-rank-user').innerHTML = data.user
    document.getElementById('avatar-rank').src = data.avatar
    document.getElementById('diamonds-rank').innerHTML = data.diamonds;


  }
};


function toast_notifc(text){

  if (text == 'error'){
    text = 'Ocorreu um erro no salvamento, verifique se os dados estão corretos ou entre em contato com o suporte.'
  } else if (text == 'success') {
    text = 'Sucesso ao salvar'
  }

  Bs5Utils.defaults.toasts.position = 'bottom-right';
  Bs5Utils.defaults.toasts.container = 'toast-container';
  Bs5Utils.defaults.toasts.stacking = true;

  const bs5Utils = new Bs5Utils();

  Bs5Utils.registerStyle('dark-purple', {
    btnClose: ['btn-close-white'],
    main: ['bg-black', 'text-white'],
    border: ['custom-border-modal']
  });

  bs5Utils.Toast.show({
    type: 'dark-purple',
    icon: `<i class="far fa-check-circle fa-lg me-2"></i>`,
    title: 'Notificação',
    subtitle: '',
    buttons : [],
    content: text,
    delay: 5000,
    dismissible: true
});

}

function logout() {
  $("#confirm-logout").modal("show");
}

function confirm_logout(){
  window.pywebview.api.logout_auth()
}

async function disclosure(event,type_id){

  if (type_id == 'save'){

      event.preventDefault()

      var form_disclosure = document.querySelector('#form-disclosure');
      var disclosure = form_disclosure.querySelector('#message-disclosure-send').value;
      var button_copy = document.getElementById("copy-dis");
      var button_save = document.getElementById("submit-message-disclosure");
    
      window.pywebview.api.disclosure_py(type_id,disclosure);
    
      button_copy.disabled = true;
      button_save.disabled = true;
      document.getElementById('message-disclosure-send').value = 'Salvo!';
    
      await sleep(3000)
    
      button_copy.disabled = false;
      button_save.disabled = false;
      
      document.getElementById('message-disclosure-send').value = disclosure;

  } else if (type_id == 'copy'){

      var copyText = document.getElementById("message-disclosure-send");
      var button_copy = document.getElementById("copy-dis");
      var button_save = document.getElementById("submit-message-disclosure");

      var saved_message = copyText.value

      copyText.select(); 
      navigator.clipboard.writeText(copyText.value);

      button_copy.disabled = true;
      button_save.disabled = true;
      document.getElementById('message-disclosure-send').value = 'Copiado para a Clipboard!';


      await sleep(3000)

      button_copy.disabled = false;
      button_save.disabled = false;
      document.getElementById('message-disclosure-send').value = saved_message;
  }
}

async function update_modal(type_id){

  if (type_id == 'get'){

    var status = await window.pywebview.api.update_check('check');

    if(status){
      
      if (status){

        var repoOwner = 'GGTEC'
        var repoName = 'VibesBot'

        fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`)
        .then(response => response.json())
        .then(data => {

          let releasesList = document.querySelector("#update_body");

          if (releasesList != undefined){
            
            releasesList.innerHTML = "";

            const firstRelease = data; // Obter o primeiro item da lista
            
            const converter = new showdown.Converter()

            var html_release = converter.makeHtml(firstRelease.body);

            let releaseEl = document.createElement("div");

            releaseEl.classList.add('version_block')
            releaseEl.innerHTML = `
              <p>Versão: ${firstRelease.tag_name}</p>
              <p class='version_text'>${html_release}</p>
            `;

            releasesList.appendChild(releaseEl);
          }
          
        })
        .catch(error => console.error(error));


        $("#update-modal").modal("show");

      } else {
        document.getElementById('no-update').hidden = false
      }
    }

  } else if (type_id == 'open'){
    window.pywebview.api.update_check('open');
  }
}

async function updateTimeDiff() {

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

async function getFolder(id,type_id) {
  var dosya_path = await window.pywebview.api.select_file_py(type_id);
  if (dosya_path) {
      document.getElementById(id).value = dosya_path;
      if (id == 'file-select-notific'){
          chat_config('save')
      }
  }
}

async function start_scroll_event_log(){

  const div_events_scroll = document.getElementById("div-events");

  const itensPorPagina = 10;
  let paginaAtual = 1;
  
  div_events_scroll.addEventListener("scroll",async function() {
  
    if (div_events_scroll.scrollTop + div_events_scroll.clientHeight >= div_events_scroll.scrollHeight) {
  
      data ={
        "type_id" : 'get'
      };
  
      var Events = await window.pywebview.api.event_log(JSON.stringify(data));
  
      if (Events) {
  
        var EventsParse = JSON.parse(Events);
        var events_list = EventsParse["event-list"].reverse()
  
        const startIndex = paginaAtual * itensPorPagina;
        const endIndex = startIndex + itensPorPagina;
        const items = events_list.slice(startIndex, endIndex);
  
        for (let i = 0; i < items.length; i++) {
  
          var part = items[i].split(" | ");
    
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
          var showGoal = EventsParse["show-goal"];
          var showShare = EventsParse["show-share"];
          var showJoin = EventsParse["show-join"];
  
  
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
            "goal": showGoal,
            "share": showShare,
            "join": showJoin,
          };
      
      
          if (variableMappings[type_message] === 1) {
            div_events_scroll.appendChild(div_event);
          }
          
        }
  
        paginaAtual++;
      }
      
    }
  });
}

async function userdata_modal(type_id,user){

  var usernameElement = document.getElementById("user-edit-username");
  var useridElement = document.getElementById("user-edit-userid");
  var likesElement = document.getElementById("user-edit-likes");
  var giftsElement = document.getElementById("user-edit-gifts");
  var sharesElement = document.getElementById("user-edit-shares");
  var levelElement = document.getElementById("user-edit-roles");
  var pointsElement = document.getElementById("user-edit-points");
  var ButtonElement = document.getElementById("btn-save-useredit");

  if (type_id == 'edit'){
    
    var userdata_parse = await window.pywebview.api.userdata_py('get','None')
      
    if (userdata_parse){
      
      userdata_parse = JSON.parse(userdata_parse)

      data = userdata_parse[user]

      $('#userdata-edit-modal').modal("show")

      await sleep(1000)

      usernameElement.value = data.display_name
      useridElement.value = user
      likesElement.value = data.likes
      giftsElement.value = data.gifts
      sharesElement.value = data.shares
      pointsElement.value = data.points
      ButtonElement.setAttribute("onclick", `userdata_modal('save','${user}')`);

      $('#user-edit-roles').selectpicker('val',data.roles);
      $('#user-edit-roles').selectpicker('refresh')



    }
  } else if (type_id == 'save'){

      var roles = []; 

      $('#user-edit-roles :selected').each(function(i, selected){ 
          roles[i] = $(selected).val(); 
      });

      data = {
        username : usernameElement.value,
        userid : useridElement.value,
        likes : likesElement.value,
        gifts : giftsElement.value,
        shares : sharesElement.value,
        points : pointsElement.value,
        roles: roles
      }

      window.pywebview.api.userdata_py('save',JSON.stringify(data));


  } else if (type_id == 'remove'){


    retunr = await window.pywebview.api.userdata_py('remove',user)

    if (retunr){

      userdata_js('get','null')

    }

}
}

async function userdata_js(type_id,data){

  if (type_id == "get"){

      var userdata_parse = await window.pywebview.api.userdata_py('get','None')
      
      if (userdata_parse){

          userdata_parse = JSON.parse(userdata_parse)

          if ($.fn.DataTable.isDataTable("#userdata_table")) {
              $('#userdata_table').DataTable().clear().draw();
              $('#userdata_table').DataTable().destroy();
          }


          var table = $('#userdata_table').DataTable( {
              pageLength: 8,
              autoWidth: true,
              destroy: true,
              scrollX: true,
              paging: true,
              ordering:  true,
              retrieve : false,
              processing: true,
              responsive: true,
              lengthMenu: [
                  [10, 25, 50, -1],
                  [10, 25, 50, 'All'],
              ],
              language: {
                  url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
              }
          } );


          for (var key in userdata_parse) {

              var removeBtn = document.createElement("button");
              removeBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
              removeBtn.setAttribute("type", "button");
              removeBtn.setAttribute("title", "Remover usuário");
              removeBtn.setAttribute("data-toggle", "tooltip");
              removeBtn.setAttribute("data-bs-placement", "top");
              removeBtn.setAttribute("onclick", `userdata_modal("remove",'${key}')`);

              var removeIcon = document.createElement("i");
              removeIcon.classList.add("fa-solid", "fa-user-xmark");

              removeBtn.appendChild(removeIcon);

              var EditBtn = document.createElement("button");
              EditBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
              EditBtn.setAttribute("type", "button");
              EditBtn.setAttribute("title", "Editar usuário");
              EditBtn.setAttribute("onclick", `userdata_modal('edit','${key}')`);

              var EditIcon = document.createElement("i");
              EditIcon.classList.add("fa-solid", "fa-user-pen");

              EditBtn.appendChild(EditIcon);


              var row = table.row.add([
                userdata_parse[key].display_name,
                key,
                userdata_parse[key].roles,
                userdata_parse[key].points,
                userdata_parse[key].likes,
                userdata_parse[key].shares,
                userdata_parse[key].gifts,
                `${removeBtn.outerHTML}/${EditBtn.outerHTML}`
              ]);

              
            }

      }

  
  } else if (type_id == 'remove'){
      window.pywebview.api.userdata_py(type_id,data)
  }
}

async function getCheckedValue(element) {
  return element.checked ? 1 : 0;
}

var socket_likes;
var socket_gifts;
var socket_specs;
var socket_diamonds;
var socket_follow;
var socket_shares;


function connectWebSocket_likes() {

  var iframe_likes = document.getElementById('iframe-likes');


  if (socket_likes && socket_likes.readyState === WebSocket.OPEN) {
    return;
  }

  socket_likes = new WebSocket("ws://localhost:7688");

  socket_likes.onopen = function(event) {

    message = {
        type: "likes"
    };

    socket_likes.send(JSON.stringify(message))


  };

  socket_likes.onmessage = function(event) {


      if (event.data === 'ping') {

          message = {
              type: "pong"
          };

          socket_likes.send(JSON.stringify(message))

      } else {

        var data_parse = JSON.parse(event.data);

        if (data_parse.type === 'save_html') {

          iframe_likes.innerHTML = "";

          var temp_div = document.createElement('div');
          temp_div.innerHTML = data_parse.html;

          var temp_div_outer = temp_div.querySelector('.progress-outer');
          iframe_likes.appendChild(temp_div_outer)
        

        } else if (data_parse.type === 'update_goal'){

          if (data_parse.type_goal == 'likes'){

            iframe_likes.innerHTML = "";

            var temp_div = document.createElement('div');
            temp_div.innerHTML = data_parse.html;

            var temp_div_outer = temp_div.querySelector('.progress-outer');
            iframe_likes.appendChild(temp_div_outer)

            var bar = iframe_likes.querySelector('#progress-bar');
            var value = iframe_likes.querySelector("#progress-value");

            var value1 = data_parse.current
            var value2 = data_parse.goal

            var percent = (value1 / value2) * 100;

            bar.style.width = percent + "%";

            value.textContent = `${value1}/${value2}`
          }

          }
      }
  };

  socket_likes.onclose = function(error) {
    reconnectWebSocket_likes();
  };
}

function reconnectWebSocket_likes() {
  if (!socket_likes || socket_likes.readyState === WebSocket.CLOSED) {
    setTimeout(function() {connectWebSocket_likes();}, 3000);
  }
}



function connectWebSocket_diamonds() {

  var iframe_diamonds = document.getElementById('iframe-diamonds');

  if (socket_diamonds && socket_diamonds.readyState === WebSocket.OPEN) {
    return;
  }

  socket_diamonds = new WebSocket("ws://localhost:7688");

  socket_diamonds.onopen = function(event) {
    
    message = {
        type: "diamonds"
    };

    socket_diamonds.send(JSON.stringify(message))
  };

  socket_diamonds.onmessage = function(event) {

      if (event.data === 'ping') {

          message = {
              type: "pong"
          };

          socket_diamonds.send(JSON.stringify(message))

      } else {

        var data_parse = JSON.parse(event.data);

        if (data_parse.type === 'save_html') {

          iframe_diamonds.innerHTML = "";

          var temp_div = document.createElement('div');
          temp_div.innerHTML = data_parse.html;

          var temp_div_outer = temp_div.querySelector('.progress-outer');
          iframe_diamonds.appendChild(temp_div_outer)

        } else if (data_parse.type === 'update_goal'){

          if (data_parse.type_goal == 'diamonds'){

              iframe_diamonds.innerHTML = "";

              var temp_div = document.createElement('div');
              temp_div.innerHTML = data_parse.html;

              var temp_div_outer = temp_div.querySelector('.progress-outer');
              iframe_diamonds.appendChild(temp_div_outer)

              var bar = iframe_diamonds.querySelector('#progress-bar');
              var value = iframe_diamonds.querySelector("#progress-value");

              var value1 = data_parse.current
              var value2 = data_parse.goal

              var percent = (value1 / value2) * 100;

              bar.style.width = percent + "%";

              value.textContent = `${value1}/${value2}`
            }

          }
      }
  };

  socket_diamonds.onclose = function(error) {
    reconnectWebSocket_gifts();
  };
}

function reconnectWebSocket_diamonds() {
  if (!socket_diamonds || socket_diamonds.readyState === WebSocket.CLOSED) {
    setTimeout(function() {connectWebSocket_gifts();}, 3000);
  }
}



function connectWebSocket_folows() {

  var iframe_follows = document.getElementById('iframe-follows');

  if (socket_follow && socket_follow.readyState === WebSocket.OPEN) {
    return;
  }

  socket_follow = new WebSocket("ws://localhost:7688");

  socket_follow.onopen = function(event) {
    message = {
        type: "follow"
    };

    socket_follow.send(JSON.stringify(message))
  };

  socket_follow.onmessage = function(event) {

      if (event.data === 'ping') {

          message = {
              type: "pong"
          };

          socket_follow.send(JSON.stringify(message))

      } else {

        var data_parse = JSON.parse(event.data);

        if (data_parse.type === 'save_html') {

          iframe_follows.innerHTML = "";

          var temp_div = document.createElement('div');
          temp_div.innerHTML = data_parse.html;

          var temp_div_outer = temp_div.querySelector('.progress-outer');
          iframe_follows.appendChild(temp_div_outer)

        } else if (data_parse.type === 'update_goal'){

          if (data_parse.type_goal == 'follow'){

              iframe_follows.innerHTML = "";

              var temp_div = document.createElement('div');
              temp_div.innerHTML = data_parse.html;

              var temp_div_outer = temp_div.querySelector('.progress-outer');
              iframe_follows.appendChild(temp_div_outer)

              var bar = iframe_follows.querySelector('#progress-bar');
              var value = iframe_follows.querySelector("#progress-value");

              var value1 = data_parse.current
              var value2 = data_parse.goal

              var percent = (value1 / value2) * 100;

              bar.style.width = percent + "%";

              value.textContent = `${value1}/${value2}`
            }

          }
      }
  };

  socket_follow.onclose = function(error) {
    reconnectWebSocket_folows();
  };
}

function reconnectWebSocket_folows() {
  if (!socket_follow || socket_follow.readyState === WebSocket.CLOSED) {
    setTimeout(function() {connectWebSocket_folows();}, 3000);
  }
}


function connectWebSocket_gifts() {

  var iframe_gifts = document.getElementById('iframe-gifts');

  if (socket_gifts && socket_gifts.readyState === WebSocket.OPEN) {
    return;
  }

  socket_gifts = new WebSocket("ws://localhost:7688");

  socket_gifts.onopen = function(event) {
    message = {
        type: "gift"
    };

    socket_gifts.send(JSON.stringify(message))
  };

  socket_gifts.onmessage = function(event) {

      if (event.data === 'ping') {

          message = {
              type: "pong"
          };

          socket_gifts.send(JSON.stringify(message))

      } else {

        var data_parse = JSON.parse(event.data);

        if (data_parse.type === 'save_html') {

          iframe_gifts.innerHTML = "";

          var temp_div = document.createElement('div');
          temp_div.innerHTML = data_parse.html;

          var temp_div_outer = temp_div.querySelector('.progress-outer');
          iframe_gifts.appendChild(temp_div_outer)

        } else if (data_parse.type === 'update_goal'){

          if (data_parse.type_goal == 'gift'){

            iframe_gifts.innerHTML = "";

              var temp_div = document.createElement('div');
              temp_div.innerHTML = data_parse.html;

              var temp_div_outer = temp_div.querySelector('.progress-outer');
              iframe_gifts.appendChild(temp_div_outer)

              var bar = iframe_gifts.querySelector('#progress-bar');
              var value = iframe_gifts.querySelector("#progress-value");

              var value1 = data_parse.current
              var value2 = data_parse.goal

              var percent = (value1 / value2) * 100;

              bar.style.width = percent + "%";

              value.textContent = `${value1}/${value2}`
            }

          }
      }
  };

  socket_gifts.onclose = function(error) {
    reconnectWebSocket_gifts();
  };
}

function reconnectWebSocket_gifts() {
  if (!socket_gifts || socket_gifts.readyState === WebSocket.CLOSED) {
    setTimeout(function() {connectWebSocket_gifts();}, 3000);
  }
}

function connectWebSocket_specs() {

  var iframe_specs = document.getElementById('iframe-specs');

  if (socket_specs && socket_specs.readyState === WebSocket.OPEN) {
    return;
  }

  socket_specs = new WebSocket("ws://localhost:7688");

  socket_specs.onopen = function(event) {
    message = {
        type: "max_viewer"
    };

    socket_specs.send(JSON.stringify(message))
  };

  socket_specs.onmessage = function(event) {

      if (event.data === 'ping') {

          message = {
              type: "pong"
          };

          socket_specs.send(JSON.stringify(message))

      } else {

        var data_parse = JSON.parse(event.data);

        if (data_parse.type === 'save_html') {

          iframe_specs.innerHTML = "";

          var temp_div = document.createElement('div');
          temp_div.innerHTML = data_parse.html;

          var temp_div_outer = temp_div.querySelector('.progress-outer');
          iframe_specs.appendChild(temp_div_outer)

        } else if (data_parse.type === 'update_goal'){

          if (data_parse.type_goal == 'max_viewer'){

              iframe_specs.innerHTML = "";

              var temp_div = document.createElement('div');
              temp_div.innerHTML = data_parse.html;

              var temp_div_outer = temp_div.querySelector('.progress-outer');
              iframe_specs.appendChild(temp_div_outer)

              var bar = iframe_specs.querySelector('#progress-bar');
              var value = iframe_specs.querySelector("#progress-value");

              var value1 = data_parse.current
              var value2 = data_parse.goal

              var percent = (value1 / value2) * 100;

              bar.style.width = percent + "%";

              value.textContent = `${value1}/${value2}`
            }

          }
      }
  };

  socket_specs.onclose = function(error) {
    reconnectWebSocket_specs();
  };
}

function reconnectWebSocket_specs() {
  if (!socket_specs || socket_specs.readyState === WebSocket.CLOSED) {
    setTimeout(function() {connectWebSocket_specs();}, 3000);
  }
}

function connectWebSocket_shares() {

  var iframe_shares = document.getElementById('iframe-shares');

  if (socket_shares && socket_shares.readyState === WebSocket.OPEN) {
    return;
  }

  socket_shares = new WebSocket("ws://localhost:7688");

  socket_shares.onopen = function(event) {
    message = {
        type: "share"
    };

    socket_shares.send(JSON.stringify(message))
  };

  socket_shares.onmessage = function(event) {

      if (event.data === 'ping') {

          message = {
              type: "pong"
          };

          socket_specs.send(JSON.stringify(message))

      } else {

        var data_parse = JSON.parse(event.data);

        if (data_parse.type === 'save_html') {

          iframe_shares.innerHTML = "";

          var temp_div = document.createElement('div');
          temp_div.innerHTML = data_parse.html;

          var temp_div_outer = temp_div.querySelector('.progress-outer');
          iframe_shares.appendChild(temp_div_outer)

        } else if (data_parse.type === 'update_goal'){

          if (data_parse.type_goal == 'share'){

              iframe_shares.innerHTML = "";

              var temp_div = document.createElement('div');
              temp_div.innerHTML = data_parse.html;

              var temp_div_outer = temp_div.querySelector('.progress-outer');
              iframe_shares.appendChild(temp_div_outer)

              var bar = iframe_shares.querySelector('#progress-bar');
              var value = iframe_shares.querySelector("#progress-value");

              var value1 = data_parse.current
              var value2 = data_parse.goal

              var percent = (value1 / value2) * 100;

              bar.style.width = percent + "%";

              value.textContent = `${value1}/${value2}`
            }

          }
      }
  };

  socket_shares.onclose = function(error) {
    reconnectWebSocket_shares();
  };
}

function reconnectWebSocket_shares() {
  if (!socket_shares || socket_shares.readyState === WebSocket.CLOSED) {
    setTimeout(function() {connectWebSocket_shares();}, 3000);
  }
}


