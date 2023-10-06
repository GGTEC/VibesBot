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
        
        update_modal('get_start')
      }, 1000);
  
      start_carousel()
  
      progress_span.innerHTML = 'start info carroucel.'
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
  $('select').selectpicker({
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

function start_carousel(){

  $('.carousel').flickity({
    contain: true,
    wrapAround: true,
    autoPlay: true,
    prevNextButtons: false,
    pageDots: false,
    setGallerySize: false
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
    ttk_goal('save_html')
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


  } else if(type_id == 'update_follows'){


    var bar = document.getElementById("progress-bar-follow");
    var progressValue = document.getElementById("progress-value-follow");

    var value_perc = (Number(data.goal) / Number(data.total)) * 100;

    bar.style.width = value_perc + "%";
    progressValue.textContent = `${data.total}/${data.goal}`;

  } else if(type_id == 'likes'){

    var bar = document.getElementById("progress-bar-likes");
    var progressValue = document.getElementById("progress-value-likes");
    var progressTitle = document.getElementById("progress-title-likes");
    var progressTitle_user = document.getElementById("progress-title-likes-user");

    var value_perc = (Number(data.goal) / Number(data.total)) * 100;

    bar.style.width = value_perc + "%";
    progressValue.textContent = `${data.total}/${data.goal}`;
    progressTitle_user.innerText = data.user

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
    main: ['bg-dark', 'text-white'],
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
      
      if (status != 'false'){

        var repoOwner = 'GGTEC'
        var repoName = 'RewardEvents'

        fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`)
        .then(response => response.json())
        .then(data => {

          let releasesList = document.querySelector("#update_body");

          if (releasesList != undefined){
            
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

  } else if (type_id == 'get_start'){

    var status = await window.pywebview.api.update_check('check');

    if(status){
      
      if (status != 'false'){

        var repoOwner = 'GGTEC'
        var repoName = 'RewardEvents'

        fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`)
        .then(response => response.json())
        .then(data => {

          let releasesList = document.querySelector("#update_body");

          if (releasesList != undefined){
            
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

function update_div_redeem(data_redem_parse) {

    var image_redeem = document.getElementById("image_redeem");
    var name_redeem = document.getElementById("name_redeem");
    var user_redeem = document.getElementById("user_redeem");

    if (data_redem_parse.redeem_image != 'None'){
      image_redeem.src = data_redem_parse.redeem_image
    }
    name_redeem.innerText = data_redem_parse.redeem_name
    user_redeem.innerText = data_redem_parse.redeem_user
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

function start_scroll_event_log(){

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


async function userdata_js(type_id,data){

  if (type_id == "get"){

      $('#userdata-modal').modal('show')

      var userdata_parse = await window.pywebview.api.userdata_py('get','None')
      
      if (userdata_parse){

          userdata_parse = JSON.parse(userdata_parse)

          console.log(userdata_parse)

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
              removeBtn.setAttribute("onclick", `window.pywebview.api.userdata_py('remove','${userdata_parse[key].display_name}`);

              var removeIcon = document.createElement("i");
              removeIcon.classList.add("fa-solid", "fa-user-xmark");

              removeBtn.appendChild(removeIcon);

              var row = table.row.add([
                userdata_parse[key].display_name,
                userdata_parse[key].roles,
                userdata_parse[key].likes,
                userdata_parse[key].shares,
                userdata_parse[key].gifts,
                removeBtn.outerHTML
              ]);

              
            }

          $('#userdata_table tfoot th').each(function () {
              var title = $(this).text();
              $(this).html('<input type="text" class="form-control bg-dark" placeholder="Procure em ' + title + '" />');
          });

          $('[data-toggle="tooltip"]').tooltip();

      }

  
  } else if (type_id == 'remove'){
      window.pywebview.api.userdata_py(type_id,data)
  }
}

function getCheckedValue(element) {
  return element.checked ? 1 : 0;
}