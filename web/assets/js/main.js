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
    
      var functionsCount = 20;
      var functionsExecuted = 0; 

      $('[data-toggle="tooltip"]').tooltip();
      $("input, select, textarea").attr("autocomplete", "off");
      $("input, select, textarea").attr("spellcheck", "false");

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Tooltips, inputs.'

      get_version()
      
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Start version.'

      start_scroll_chat_log()

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Start chat.'
      
      anima_status('get')

      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      progress_span.innerHTML = 'Animation status.'

      start_disclosure()

      progress_span.innerHTML = 'Start disclosure.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      start_selectpicker()
  
      progress_span.innerHTML = 'Start Selectpicker.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_sidebar()
  
      progress_span.innerHTML = 'Start Sidebar.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_scroll()
  
      progress_span.innerHTML = 'Start scroll.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

      
      start_scroll_event_log()

      progress_span.innerHTML = 'Start scroll event log.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_resizable()
  
      progress_span.innerHTML = 'Start resizable.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
  
      start_update_time_chat()
  
      progress_span.innerHTML = 'Start Auto update time chat.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      start_events_log('div-events')
  
      progress_span.innerHTML = 'Get event logs.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      start_event_updatetime()
  
      progress_span.innerHTML = 'Start Auto update time events.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      
      start_color_inputs()
  
      connectWebSocket('likes');
      connectWebSocket('diamonds');
      connectWebSocket('follow');
      connectWebSocket('gift');
      connectWebSocket('max_viewer');
      connectWebSocket('share');   
      connectWebSocketVotes('votes')   

      progress_span.innerHTML = 'Start ConnectWebsockets.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
      

      $('#main').removeClass('d-none')
      $('#loading').addClass('remove-loading')
  
      setTimeout(function() {
        
        $('#loading').addClass('d-none');
        
        update_modal('get')

      }, 1000);

      
      progress_span.innerHTML = 'remove loading.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso
  
      
      progress_span.innerHTML = 'Finish start.'
      functionsExecuted++;
      progressBar_start.style.width = `${functionsExecuted * (100 / functionsCount)}%`; //atualize o progresso

        
      const chatWindow = document.getElementById("chat-block-inner");
      chatWindow.scrollTop = chatWindow.scrollHeight;

    }
    
  }

});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function get_version(){

  var version = document.getElementById('number-version');

  var version_rec = await window.pywebview.api.get_version();

  if (version_rec){

    version.innerHTML = version_rec

  }

}
  
async function start_disclosure(){

  var disclosure = await window.pywebview.api.disclosure_py('get','null');
  
  if (disclosure){

      document.getElementById('message-disclosure-send').value = disclosure

  }

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
  
  $("#goal-text-color").on('input', function(event) {
    $("#goal-text-color-span").css('background-color',$(this).val());
    $("#goal-text-color-text").val($(this).val())
  });


  $("#goal-bar-color-button").click(function(event) {
    $("#goal-bar-color").click();
  });

  $("#goal-bar-color").on('input', function(event) {
    $("#goal-bar-color-span").css('background-color',$(this).val());
    $("#goal-bar-color-text").val($(this).val())
  });


  $("#goal-background-bar-color-button").click(function(event) {
    $("#goal-background-bar-color").click();
  });

  $("#goal-background-bar-color").on('input', function(event) {
    $("#goal-background-bar-color-span").css('background-color',$(this).val());
    $("#goal-background-bar-color-text").val($(this).val())
  });

  $("#goal-background-color-button").click(function(event) {
    $("#goal-background-color").click();
  });

  $("#goal-background-border-color").on('input', function(event) {
    $("#goal-background-color-border-span").css('background-color',$(this).val());
    $("#goal-background-color-border-text").val($(this).val())
  });

  $("#goal-background-color-border-button").click(function(event) {
    $("#goal-background-border-color").click();
  });

  $("#goal-background-color").on('input', function(event) {
    $("#goal-background-color-span").css('background-color',$(this).val());
    $("#goal-background-color-text").val($(this).val())
  });



  $("#giveaway-color1-button").click(function(event) {
    $("#giveaway-color1-color").click();
  });

  $("#giveaway-color1-color").on('input', function(event) {
    $("#giveaway-color1-span").css('background-color',$(this).val());
    $("#giveaway-color1-text").val($(this).val())
  });

  $("#giveaway-color2-button").click(function(event) {
    $("#giveaway-color2-color").click();
  });

  $("#giveaway-color2-color").on('input', function(event) {
    $("#giveaway-color2-span").css('background-color',$(this).val());
    $("#giveaway-color2-text").val($(this).val())
  });

  $("#giveaway-pointer-button").click(function(event) {
    $("#giveaway-pointer-color").click();
  });

  $("#giveaway-pointer-color").on('input', function(event) {
    $("#giveaway-pointer-span").css('background-color',$(this).val());
    $("#giveaway-pointer-text").val($(this).val())
  });


  $("#subathon-color1-button").click(function(event) {
    $("#subathon-color1-color").click();
  });

  $("#subathon-color1-color").on('input', function(event) {
    $("#subathon-color1-span").css('background-color',$(this).val());
    $("#subathon-color1-text").val($(this).val())
  });

  $("#subathon-color2-button").click(function(event) {
    $("#subathon-color2-color").click();
  });

  $("#subathon-color2-color").on('input', function(event) {
    $("#subathon-color2-span").css('background-color',$(this).val());
    $("#subathon-color2-text").val($(this).val())
  });



  $("#vote-text-color-button").click(function(event) {
    $("#vote-text-color").click();
  });
  
  $("#vote-text-color").on('input', function(event) {
    $("#vote-text-color-span").css('background-color',$(this).val());
    $("#vote-text-color-text").val($(this).val())
  });

  $("#vote-bar-color-button").click(function(event) {
    $("#vote-bar-color").click();
  });

  $("#vote-bar-color").on('input', function(event) {
    $("#vote-bar-color-span").css('background-color',$(this).val());
    $("#vote-bar-color-text").val($(this).val())
  });


  $("#vote-background-bar-color-button").click(function(event) {
    $("#vote-background-bar-color").click();
  });

  $("#vote-background-bar-color").on('input', function(event) {
    $("#vote-background-bar-color-span").css('background-color',$(this).val());
    $("#vote-background-bar-color-text").val($(this).val())
  });

  $("#vote-background-color-button").click(function(event) {
    $("#vote-background-color").click();
  });

  $("#vote-background-border-color").on('input', function(event) {
    $("#vote-background-color-border-span").css('background-color',$(this).val());
    $("#vote-background-color-border-text").val($(this).val())
  });

  $("#vote-background-color-border-button").click(function(event) {
    $("#vote-background-border-color").click();
  });

  $("#vote-background-color").on('input', function(event) {
    $("#vote-background-color-span").css('background-color',$(this).val());
    $("#vote-background-color-text").val($(this).val())
  });



  $("#rank-font-button").click(function(event) {
    $("#rank-font-color").click();
  });

  $("#rank-font-color").on('input', function(event) {
    $("#rank-font-span").css('background-color',$(this).val());
    $("#rank-font-text").val($(this).val())
  });

  


  $("#rank-background-button").click(function(event) {
    $("#rank-background-color").click();
  });

  $("#rank-background-color").on('input', function(event) {
    $("#rank-background-span").css('background-color',$(this).val());
    $("#rank-background-text").val($(this).val())
  });

  $("#event-background-color-button").click(function(event) {
    $("#event-background-color-select").click();
  });

  $("#event-background-color-select").on('input', function(event) {
    $("#event-background-color-span").css('background-color',$(this).val());
    $("#event-background-color-text").val($(this).val())/
    $(".event_block_overlay").css('background-color',$(this).val());
  });

  $("#event-text-color-button").click(function(event) {
    $("#event-text-color-select").click();
  });

  $("#event-text-color-select").on('input', function(event) {
    $("#event-text-color-span").css('background-color',$(this).val());
    $("#event-text-color-text").val($(this).val());
    $(".event_block_overlay span").css('color',$(this).val());
  });



  $("#highlighted-background-color-button").click(function(event) {
    $("#highlighted-background-color-select").click();
  });

  $("#highlighted-background-color-select").on('input', function(event) {
    $("#highlighted-background-color-span").css('background-color',$(this).val());
    $("#highlighted-background-color-text").val($(this).val())
  });


  $("#highlighted-border-color-button").click(function(event) {
    $("#highlighted-border-color").click();
  });

  $("#highlighted-border-color").on('input', function(event) {
    $("#highlighted-color-border-span").css('background-color',$(this).val());
    $("#highlighted-color-border-text").val($(this).val())
  });

  $("#alerts-text-color-button").click(function(event) {
    $("#alerts-text-color-select").click();
  });

  $("#alerts-text-color-select").on('input', function(event) {
    $("#alerts-text-color-span").css('background-color',$(this).val());
    $("#alerts-text-color-text").val($(this).val())
  });

  $("#alerts-background-color-button").click(function(event) {
    $("#alerts-background-color-select").click();
  });

  $("#alerts-background-color-select").on('input', function(event) {
    $("#alerts-background-color-span").css('background-color',$(this).val());
    $("#alerts-background-color-text").val($(this).val())
  });

  $("#alertsvideo-background-color-button").click(function(event) {
    $("#alertsvideo-background-color-select").click();
  });

  $("#alertsvideo-background-color-select").on('input', function(event) {
    $("#alertsvideo-background-color-span").css('background-color',$(this).val());
    $("#alertsvideo-background-color-text").val($(this).val())
  });


  $("#alertsvideo-text-color-button").click(function(event) {
    $("#alertsvideo-text-color-select").click();
  });

  $("#alertsvideo-text-color-select").on('input', function(event) {
    $("#alertsvideo-text-color-span").css('background-color',$(this).val());
    $("#alertsvideo-text-color-text").val($(this).val())
  });

}

function update_specs_tiktok(specs){

  if (specs >= 1){

    document.getElementById('tiktok-spec').hidden = false;
    document.getElementById('time-in-live').innerText = 'Online';
    document.getElementById('live-dot').style.color = 'red';
    document.getElementById('text-counter-ttk').innerText = " " + specs;

  } else if (specs == 'disconect'){

    document.getElementById('tiktok-spec').hidden = false;
    document.getElementById('time-in-live').innerText = 'Offline';
    document.getElementById('live-dot').style.color = 'white';
    document.getElementById('text-counter-ttk').innerText = " Desconectado";
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

async function disclosure(event, type_id){

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
      
      if (status == true){

        var repoOwner = 'GGTEC'
        var repoName = 'VibesBot'

        fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`)
        .then(response => response.json())
        .then(data => {

          let ReleaseBody = document.querySelector("#update_body");
            
          ReleaseBody.innerHTML = "";

          const firstRelease = data;
          
          const converter = new showdown.Converter()

          var html_release = converter.makeHtml(firstRelease.body);

          let releaseEl = document.createElement("div");

          releaseEl.classList.add('version_block')
          releaseEl.innerHTML = `
            <p>Versão: ${firstRelease.tag_name}</p>
            <p class='version_text'>${html_release}</p>
          `;

          ReleaseBody.appendChild(releaseEl);
          
        })
        .catch(error => console.error(error));


        $("#update-modal").modal("show");

      } else if (status == 'DEV'){

        let ReleaseBody = document.querySelector("#update_body");
        let ReleaseTitle = document.querySelector("#update_title");

        ReleaseTitle.innerHTML = "Versão BETA";
        ReleaseBody.innerHTML = "<h4>Esta Versão BETA não tem suporte direto do desenvolvedor, qualquer bug ou problema relatado já está sendo analizado e será solucionado no próximo update.<h4>";
        
        $("#update-modal").modal("show");

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

async function getFolder(id, type_id) {

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
  
          var dateString = items[i].timestamp;
          var message_rec = items[i].message;
          var user_input = items[i].user_input;
          var type_message = items[i].type;

    
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
    
          div_event.id = 'recent-message-block'
          div_event.classList.add('chat-message','event-message');
          div_event.style.fontSize = "16px";
          
          div_event.appendChild(message_div);
  
          const variableMappings = {
            "command": showCommands,
            "event": showEvents,
            "follow": showFollow,
            "like": showLikes,
            "gifts": showGifts,
            "chest": showChest,
            "goal": showGoal,
            "share": showShare,
            "join": showJoin,
          };
      
          if (variableMappings[type_message] == 1) {

            div_events_scroll.appendChild(div_event);
          }
          
        }
  
        paginaAtual++;
      }
      
    }
  });
}

async function start_scroll_chat_log(){

  const div_chat_scroll = document.getElementById("chat-block-inner");
  
  let messageidx = 0
  let added = true

  async function handleScroll(){
  
    if (div_chat_scroll.scrollTop === 0 && added == true) {

      added = false

      messageidx = div_chat_scroll.childElementCount - 1;

      var messages = await window.pywebview.api.log_chat('get', messageidx);
  
      if (messages) {
        
        if (messages != null ){

          var message_data_parse = JSON.parse(messages);
  
          var show_user_picture = message_data_parse.show_user_picture;
          var user_picture_url =  message_data_parse.profile_pic;
          var chat_color_border =  message_data_parse.chat_color_border;
          var chat_color_name =  message_data_parse.chat_color_name;
          var select_color_border =  message_data_parse.chat_border_select;
          var select_color_name =  message_data_parse.chat_name_select;
          var animation = message_data_parse.chat_animation;
          var chat_newline =  message_data_parse.wrapp_message;
          var text_size =  message_data_parse.font_size;
          var chat_data =  message_data_parse.data_show;
          var chat_time =  message_data_parse.chat_time;
          var type_data =  message_data_parse.type_data;
          var user_rec =  message_data_parse.display_name;
          var user_id =  message_data_parse.userid;
          var username_rec =  message_data_parse.username;
          var message_rec =  message_data_parse.message;
          var badges =  message_data_parse.badges;
          var color_rec = chat_color_name == 1 ? select_color_name : "white";
          var border_color = chat_color_border == 1 ? select_color_border : '#4f016c';
  
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
          username.style.color = `${color_rec}`;
          username.setAttribute('onclick','pywebview.api.open_py("user","'+user_id+'")');
  
          var separator = document.createElement("span");
          separator.innerHTML = ' :';
  
          var span_username = document.createElement("span");
          span_username.classList.add('span_username');
          span_username.title = username_rec
          span_username.setAttribute('data-bs-placement', 'top');
          span_username.setAttribute('data-toggle', 'tooltip');
          span_username.appendChild(username);
  
          if (typeof badges === 'string' && badges.trim() !== '') {
  
              badges = badges.replace(/'/g, '"');
  
              const badgesArray = JSON.parse(badges);
  
              if (Array.isArray(badgesArray)) {
  
                  badgesArray.forEach(badge => {
                      const span = createBadgeSpan(badge.name, badge.first_url, text_size);
                      if (span) {
                          span_username.appendChild(span);
                      }
                  });
  
              } else {
                  console.error('A variável badges não é um array válido.');
              }
              
          } else {
  
              badges.forEach(badge => {
                  const span = createBadgeSpan(badge.name, badge.first_url,text_size);
                  if (span) {
                      span_username.appendChild(span);
                  }
              });
      
          }
  
          span_username.appendChild(separator);
  
          message_rec = twemoji.parse(message_rec);
  
          var span_message = document.createElement("span");
          span_message.id = 'message-chat';
          span_message.innerHTML = message_rec;
          
          var new_line = document.createElement("br");
          
          var div_message_block = document.createElement("div");
  
          var padding_start = show_user_picture == 1 ? "ps-0"  : null;
  
          div_message_block.id = 'chat-message-block'
          div_message_block.classList.add('row','chat-message', 'chat-block-color', animation ,padding_start);
          div_message_block.style.border = "3px solid "+ border_color + "";
  
          var div_message = document.createElement("div");
  
          div_message.id = 'message_block';
          div_message.classList.add('col','ps-0');
          div_message.style.fontSize = text_size + "px";
  
  
          var div_profile_pic = document.createElement("div");
  
          div_profile_pic.id = 'message_pic';
          div_profile_pic.classList.add('col-2');
          
          var img_pic = document.createElement("img"); 
          img_pic.classList.add('img-responsive','w-100','img-fluid');
          img_pic.src = user_picture_url
          img_pic.style.width = '70px'
  
          div_profile_pic.appendChild(img_pic)
          
          chat_data == 1 ? div_message.appendChild(time_chat) : null;
  
          div_message.appendChild(span_username);
  
          chat_newline == 1 ? div_message.appendChild(new_line) : null;
  
          div_message.appendChild(span_message);
  
          show_user_picture == 1 ? div_message_block.appendChild(div_profile_pic) : null;
  
          div_message_block.appendChild(div_message)
          
          var div_chat = document.querySelector('#chat-block-inner div:first-child');
  
          div_chat.parentNode.insertBefore(div_message_block, div_chat);
  
  
          $(".span_username").tooltip()
          
        }

        messageidx++;

        added = true
          
      }
    }
  }

  div_chat_scroll.addEventListener("wheel", handleScroll);

  div_chat_scroll.addEventListener("scroll", handleScroll);
  
}

function copy_username(element){

    var value = element.getAttribute('data-copy-value');

    navigator.clipboard.writeText(value);

}

async function userdata_modal(type_id,user){

  var useridElement = document.getElementById("user-edit-userid");
  var usernameElement = document.getElementById("user-edit-username");
  var displaynameElement = document.getElementById("user-edit-display-name");
  var likesElement = document.getElementById("user-edit-likes");
  var giftsElement = document.getElementById("user-edit-gifts");
  var sharesElement = document.getElementById("user-edit-shares");
  var pointsElement = document.getElementById("user-edit-points");
  var profilePicElement = document.getElementById("user-edit-profile-pic");
  var ButtonElement = document.getElementById("btn-save-useredit");

  var display_name_card = document.getElementById("display-name-card");
  var username_card = document.getElementById("username-card");
  var profile_pic_card = document.getElementById("profile-pic-card");

  var button_copy_username = document.getElementById('copy-username')
  var button_open_profile = document.getElementById('open-profile')


  if (type_id == 'edit'){
    
    var userdata_parse = await window.pywebview.api.userdata_py('load',user)
      
    if (userdata_parse){

      data = userdata_parse

      $('#userdata-edit-modal').modal("show")

      await sleep(1000)

      useridElement.value = data.userid
      displaynameElement.value = data.username
      usernameElement.value = data.display_name
      profilePicElement.value = data.profile_pic
      likesElement.value = data.likes
      giftsElement.value = data.gifts
      sharesElement.value = data.shares
      pointsElement.value = data.points

      display_name_card.innerHTML = data.display_name
      username_card.innerHTML = data.username
      profile_pic_card.src = data.profile_pic

      ButtonElement.setAttribute("onclick", `userdata_modal('save','${data.userid}')`);
      button_open_profile.setAttribute('onclick', 'pywebview.api.open_py("user","'+data.userid+'")')
      button_copy_username.setAttribute('data-copy-value',`${data.username}`)

      $('#user-edit-roles').selectpicker('val',data.roles);
      $('#user-edit-roles').selectpicker('refresh')

    }
    
  } else if (type_id == 'save'){

      var roles = []; 

      $('#user-edit-roles :selected').each(function(i, selected){ 
          roles[i] = $(selected).val(); 
      });

      data = {
        display_name : displaynameElement.value,
        username : usernameElement.value,
        userid : useridElement.value,
        likes : likesElement.value,
        gifts : giftsElement.value,
        shares : sharesElement.value,
        points : pointsElement.value,
        profile_pic : profilePicElement.value,
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

          if ($.fn.DataTable.isDataTable("#userdata_table")) {
              $('#userdata_table').DataTable().clear().draw();
              $('#userdata_table').DataTable().destroy();
          }

          var table = $('#userdata_table').DataTable( {
              pageLength: 8,
              destroy: true,
              scrollX: true,
              paging: true,
              autoWidth: true,
              ordering:  true,
              retrieve : false,
              processing: true,
              responsive: false,
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
              removeBtn.setAttribute("onclick", `userdata_modal("remove",'${userdata_parse[key].userid}')`);
              removeBtn.innerHTML = 'Excluir'

              var EditBtn = document.createElement("button");
              EditBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
              EditBtn.setAttribute("type", "button");
              EditBtn.setAttribute("title", "Editar usuário");
              EditBtn.setAttribute("onclick", `userdata_modal('edit','${userdata_parse[key].userid}')`);
              EditBtn.innerHTML = 'Editar'


              var row = table.row.add([
                userdata_parse[key].display_name,
                userdata_parse[key].username,
                userdata_parse[key].points,
                userdata_parse[key].likes,
                userdata_parse[key].shares,
                userdata_parse[key].gifts,
                `${removeBtn.outerHTML} | ${EditBtn.outerHTML}`
              ]);
              
          }

      }

  
  } else if (type_id == 'remove'){

      var user_removed = await window.pywebview.api.userdata_py(type_id,data)

      if (user_removed){

        var userdata_parse = await window.pywebview.api.userdata_py('get','None')
        
        if (userdata_parse){

            if ($.fn.DataTable.isDataTable("#userdata_table")) {
                $('#userdata_table').DataTable().clear().draw();
                $('#userdata_table').DataTable().destroy();
            }


            var table = $('#userdata_table').DataTable( {
                pageLength: 8,
                destroy: true,
                scrollX: true,
                paging: true,
                autoWidth: true,
                ordering:  true,
                retrieve : false,
                processing: true,
                responsive: false,
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
                removeBtn.setAttribute("onclick", `userdata_modal("remove",'${userdata_parse[key].userid}')`);
                removeBtn.innerHTML = 'Excluir'

                var EditBtn = document.createElement("button");
                EditBtn.classList.add("btn", "bt-submit", "p-1", "m-1");
                EditBtn.setAttribute("type", "button");
                EditBtn.setAttribute("title", "Editar usuário");
                EditBtn.setAttribute("onclick", `userdata_modal('edit','${userdata_parse[key].userid}')`);
                EditBtn.innerHTML = 'Editar'


                var row = table.row.add([
                  userdata_parse[key].display_name,
                  userdata_parse[key].username,
                  userdata_parse[key].points,
                  userdata_parse[key].likes,
                  userdata_parse[key].shares,
                  userdata_parse[key].gifts,
                  `${removeBtn.outerHTML} | ${EditBtn.outerHTML}`
                ]);
                
            }
        }

      }

  } else if (type_id == 'destroy'){

    if ($.fn.DataTable.isDataTable("#userdata_table")) {
      $('#userdata_table').DataTable().clear().draw();
      $('#userdata_table').DataTable().destroy();

  }

  }
}

async function getCheckedValue(element) {
  return element.checked ? 1 : 0;
}

async function anima_status(type_id){

  
  var checkbox = document.getElementById('anima-status');

  const elements = document.querySelectorAll('.background span');

  if (type_id == "save"){

    if (checkbox.checked == false){

      elements.forEach(element => {
        element.style.display = 'none';
      });

    } else {

      elements.forEach(element => {
        element.style.display = 'block';
      });

    }

    window.pywebview.api.animation(type_id,checkbox.checked)

  } else if (type_id == "get"){

    response = await window.pywebview.api.animation(type_id,'None')

    if (response == "False"){

      elements.forEach(element => {
        element.style.display = 'none';
      });

    } else {

      elements.forEach(element => {
        element.style.display = 'block';
      });

    }
  
  }
  
}

function connectWebSocket(type) {

  var iframe_div = document.getElementById('iframe-' + type);
  var iframeConfig = document.getElementById('iframe-' + type + '-config');


  var socket;

  if (socket && socket.readyState === WebSocket.OPEN) {
    return;
  }

  socket = new WebSocket("ws://localhost:7688");

  socket.onopen = function(event) {

    message = {
      type: type
    };

    socket.send(JSON.stringify(message))

  };

  socket.onmessage = function(event) {
    if (event.data === 'ping') {

      message = {
        type: "pong"
      };

      socket.send(JSON.stringify(message))

    } else {

      var data_parse = JSON.parse(event.data);

      if (data_parse.type === 'save_html') {

        iframe_div.innerHTML = "";

        var tempDiv = document.createElement('div');
        tempDiv.innerHTML = data_parse.html;

        var tempDivOuter = tempDiv.querySelector('.progress-outer');

        iframe_div.appendChild(tempDivOuter.cloneNode(true));

        iframeConfig.contentDocument.documentElement.innerHTML = data_parse.html;

      } else if (data_parse.type === 'update_goal') {

        if (data_parse.type_goal === type) {

          iframe_div.innerHTML = "";

          var tempDiv = document.createElement('div');
          tempDiv.innerHTML = data_parse.html;

          var tempDivOuter = tempDiv.querySelector('.progress-outer');

          iframe_div.appendChild(tempDivOuter.cloneNode(true));

          iframeConfig.contentDocument.documentElement.innerHTML = data_parse.html;
        }
      }
    }
  };

  socket.onclose = function(error) {
    reconnectWebSocket(type);
  };

  function reconnectWebSocket(type) {
    if (!socket || socket.readyState === WebSocket.CLOSED) {
      setTimeout(function() {
        connectWebSocket(type);
      }, 3000);
    }
  }
}


function connectWebSocketVotes(type) {

  var iframe_div = document.getElementById('iframe-votes-config');

  var socket;

  if (socket && socket.readyState === WebSocket.OPEN) {
    return;
  }

  socket = new WebSocket("ws://localhost:7688");

  socket.onopen = function(event) {

    message = {
      type: type
    };

    socket.send(JSON.stringify(message))

  };

  socket.onmessage = function(event) {

    if (event.data === 'ping') {

      message = {
        type: "pong"
      };

      socket.send(JSON.stringify(message))

    } else {

      var data_parse = JSON.parse(event.data);

      if (data_parse.type === 'votes') {

        iframe_div.innerHTML = "";

        iframe_div.contentDocument.documentElement.innerHTML = data_parse.html;

      } 
    }
  };

  socket.onclose = function(error) {
    reconnectWebSocket(type);
  };

  function reconnectWebSocket(type) {
    if (!socket || socket.readyState === WebSocket.CLOSED) {
      setTimeout(function() {
        connectWebSocket(type);
      }, 3000);
    }
  }
}
