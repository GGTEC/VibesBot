async function highlighted(type_id){

    if (type_id == 'get'){

        data = {
            type_id : type_id
        }

        var response = await window.pywebview.api.highlighted(JSON.stringify(data));

        if (response){

            response = JSON.parse(response)

            var text = document.getElementById('highlighted-text');
            var show_text_checkbox = document.getElementById('highlighted-text-show');
            
            var background_color = document.getElementById('highlighted-background-color-text');
            var border_color = document.getElementById('highlighted-color-border-text');

            var background_color_span = document.getElementById('highlighted-background-color-span');
            var border_color_span = document.getElementById('highlighted-color-border-span');

            ckeditor.setData(response.text);
            
            show_text_checkbox.checked = response.show_text == 1 ? true : false;
            background_color.value = response.background;
            border_color.value = response.border;

            background_color_span.style.backgroundColor = response.background;
            border_color_span.style.backgroundColor = response.border;

        }
    
    } else if( type_id == 'save_text'){

        var text = document.getElementById('highlighted-text');
        var show_text_checkbox = document.getElementById('highlighted-text-show');
        
        data = {
            type_id : type_id,
            show_text: show_text_checkbox.checked == true ? 1 : 0,
            text : text.innerHTML
        }

        window.pywebview.api.highlighted(JSON.stringify(data));

    } else if ( type_id == "save_style"){

        var background_color = document.getElementById('highlighted-background-color-text');
        var border_color = document.getElementById('highlighted-color-border-text');

        data = {
            type_id : type_id,
            background_color: background_color.value,
            border_color : border_color.value
        }

        window.pywebview.api.highlighted(JSON.stringify(data));

    
    }
}