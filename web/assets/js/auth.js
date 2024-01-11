async function auth(type_id){

    page_1 = document.getElementById('page-1');
    page_2 = document.getElementById('page-2');
    page_3 = document.getElementById('page-3');
    page_4 = document.getElementById('page-4');

    if (type_id == "next-terms") {

        page_1.hidden = true

        $('#page-1').removeClass('d-flex')

        page_2.hidden = false

    } else if(type_id == "next-error"){
        
        page_2.hidden = true
        page_3.hidden = false

    } else if(type_id == "next-auth"){
        
        page_3.hidden = true
        page_4.hidden = false

    }
}


async function saveauth(event){

    event.preventDefault();

    username = document.getElementById('username');
    sessionid = document.getElementById('sessionid');
    error_status = document.getElementById('send-error');
    
    error_status = error_status.checked ? true : false;

    data = {    
        username : username.value,
        sessionid :sessionid.value,
        error_status : error_status
    }

    authenticated = await window.pywebview.api.tiktok_auth(JSON.stringify(data))

    if (authenticated == true){

        location.reload();

    } else {
        document.getElementById('auth-error').hidden = false;
    }


}

function show_alert(id) {

    var $alert = $(`#${id}`);

    $alert.fadeIn();

    setTimeout(function() {
        $alert.fadeOut();
    }, 5000);
}



function checkinput(input) {

    if (input.value.includes('@')) {
        show_alert('noprefix')
        input.value = input.value.replace('@', '');
    }

    if (isURL(input.value)) {
        show_alert('nolinks')
        input.value = '';
    }
}

function isURL(str) {
    var urlPattern = /^(http|https):\/\/\S+$/;
    return urlPattern.test(str);
}