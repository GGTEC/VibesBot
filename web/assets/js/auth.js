async function auth(type_id){

    page_1 = document.getElementById('page-1');
    page_2 = document.getElementById('page-2');
    page_3 = document.getElementById('page-3');

    if (type_id == "next-terms") {

        page_1.hidden = true
        $('#page-1').removeClass('d-flex')

        page_2.hidden = false

    } else if(type_id == "next-auth"){
        
        page_2.hidden = true
        page_3.hidden = false

    } else if(type_id == "submit-auth"){
        
        username = document.getElementById('username');
        sessionid = document.getElementById('sessionid');

        data = {
            username : username.value,
            sessionid :sessionid.value,
        }

        authenticated = await window.pywebview.api.tiktok_auth(JSON.stringify(data))

        if (authenticated){

            location.reload();

        }
    }
}