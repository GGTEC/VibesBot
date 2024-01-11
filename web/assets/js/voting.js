async function votes(type_id) {

    if (type_id == 'save_commands') {

        var command_status = document.getElementById('command-vote-status');
        var command_command = document.getElementById('vote-command');
        var command_delay = document.getElementById('vote-delay');
        var command_cost_status = document.getElementById('command-cost-status-vote');
        var command_cost = document.getElementById('command-cost-vote');

        var command_status = command_status.checked ? 1 : 0;
        var command_cost_status = command_cost_status.checked ? 1 : 0;

        var roles = [];

        $('#user-level-vote :selected').each(function (i, selected) {
            roles[i] = $(selected).val();
        });

        data = {
            type_id: type_id,
            command: command_command.value,
            status: command_status,
            delay: command_delay.value,
            user_level: roles,
            cost: command_cost.value,
            cost_status: command_cost_status
        }

        var formData = JSON.stringify(data);

        window.pywebview.api.votes(formData)

    } else if (type_id == 'get_commands') {

        var command_status = document.getElementById('command-vote-status');
        var command_command = document.getElementById('vote-command');
        var command_delay = document.getElementById('vote-delay');
        var command_cost_status = document.getElementById('command-cost-status-vote');
        var command_cost = document.getElementById('command-cost-vote');

        data = {
            type_id: type_id,
        }

        var parse = await window.pywebview.api.votes(JSON.stringify(data));

        if (parse) {

            parse = JSON.parse(parse)

            command_cost_get('vote', parse.cost_status)

            command_cost_status.checked = parse.cost_status == 1 ? true : false;
            command_status.checked = parse.status == 1 ? true : false;
            command_command.value = parse.command
            command_delay.value = parse.delay
            command_cost.value = parse.cost

            $("#user-level-vote").selectpicker('val', parse.user_level)
            $("#user-level-vote").selectpicker("refresh");

        }


    } else if (type_id == 'get_options') {

        data = {
            type_id: type_id,
        }

        var parse = await window.pywebview.api.votes(JSON.stringify(data));

        if (parse) {

            var parse = JSON.parse(parse)

            createInitialVotes(parse)

        }

        var text_size = document.getElementById('font-bar-votes');

        var BackgroundBarColorOpacity = document.getElementById("vote-background-opacity");
        var TextColorInput = document.getElementById("vote-text-color-text");
        var BarColorInput = document.getElementById("vote-bar-color-text");
        var BackgroundBarColorInput = document.getElementById("vote-background-bar-color-text");
        var BackgroundColorInput = document.getElementById("vote-background-color-text");
        var BackgroundBarBorderColorInput = document.getElementById("vote-background-color-border-text");

        var TextColorspan = document.getElementById("vote-text-color-span");
        var BarColorspan = document.getElementById("vote-bar-color-span");
        var BackgroundBarColorspan = document.getElementById("vote-background-bar-color-span");
        var BackgroundColorspan = document.getElementById("vote-background-color-span");
        var BackgroundBorderColorspan = document.getElementById("vote-background-color-border-span");

        
        data = {
            type_id : 'get_html',
        }
    
        var data_parse = JSON.stringify(data);
        
        var html_data = await window.pywebview.api.votes(data_parse);
    
        if (html_data){

            html_data_parse = JSON.parse(html_data)

            $("#bar-style-votes").selectpicker('val',html_data_parse.style)

            text_size.value = html_data_parse.text_size;
            TextColorInput.value = html_data_parse.text_color;
            BarColorInput.value = html_data_parse.progress_bar;
            BackgroundBarColorInput.value = html_data_parse.progress_bar_background;
            BackgroundColorInput.value = html_data_parse.background_color;
            BackgroundBarBorderColorInput.value = html_data_parse.background_border;

            TextColorspan.style.backgroundColor = html_data_parse.text_color;
            BarColorspan.style.backgroundColor = html_data_parse.progress_bar;
            BackgroundBarColorspan.style.backgroundColor = html_data_parse.progress_bar_background;
            BackgroundBarColorOpacity.value = html_data_parse.progress_bar_background_opacity;
            BackgroundColorspan.style.backgroundColor = html_data_parse.background_color;
            BackgroundBorderColorspan.style.backgroundColor = html_data_parse.background_border;

        }

    } else if (type_id == 'create_options') {

        var option_input = document.getElementById('new-option');

        data = {
            type_id: type_id,
            name: option_input.value,
        }

        var parse = await window.pywebview.api.votes(JSON.stringify(data));

        if (parse) {

            var parse = JSON.parse(parse)

            createInitialVotes(parse)

            $('#vote-modal').modal('hide')
        }


    } else if (type_id == 'end_votes') {

        data = {
            type_id: type_id,
        }

        var parse = await window.pywebview.api.votes(JSON.stringify(data));

        if (parse) {

            var parse = JSON.parse(parse)

            var options = parse.options;
            var votingDiv = document.getElementById('Voting');

            var resultListDiv = document.getElementById('result-list');
            var endedDiv = document.getElementById('Ended');

            if(parse.status == 'Ended'){

                votingDiv.hidden = true
                
                endedDiv.hidden = false;
                resultListDiv.hidden = false
                resultListDiv.innerHTML = '';

                var VotingName = document.createElement('h2');
                VotingName.textContent = `Votação para: "${parse.name}" foi finalizada. `;

                resultListDiv.appendChild(VotingName);

                var winner = Object.keys(options).reduce(function (a, b) {
                    return options[a].votes > options[b].votes ? a : b;
                });
    
                // Create a div for the winner
                var winnerDiv = createResultDiv(winner, true, options);
                resultListDiv.appendChild(winnerDiv);
    
                // Create divs for the remaining options sorted by votes
                var remainingOptions = Object.keys(options).filter(function (option) {
                    return option !== winner;
                }).sort(function (a, b) {
                    return options[b].votes - options[a].votes;
                });
    
                remainingOptions.forEach(function (option) {
                    var optionDiv = createResultDiv(option, false, options);
                    resultListDiv.appendChild(optionDiv);
                });
            }


        }
    } else if (type_id == 'new_votes'){

        var voteName = document.getElementById('new-vote-name');
        var newOption1 = document.getElementById('new-option-1');
        var newOption2 = document.getElementById('new-option-2');

        data = {
            type_id: type_id,
            name: voteName.value,
            option1: newOption1.value,
            option2: newOption2.value,
        }

        var parse = await window.pywebview.api.votes(JSON.stringify(data));

        if (parse) {

            var parse = JSON.parse(parse)

            createInitialVotes(parse)

            $('#new-vote-modal').modal('hide')
        }

    } else if (type_id == 'save_html'){

        var style = document.getElementById('bar-style-votes');
        var text_size = document.getElementById('font-bar-votes');
        var TextColorInput = document.getElementById("vote-text-color-text");
        var BarColorInput = document.getElementById("vote-bar-color-text");
        var BackgroundBarColorInput = document.getElementById("vote-background-bar-color-text");
        var BackgroundBarColorOpacity = document.getElementById("vote-background-opacity");
        var BackgroundColorInput = document.getElementById("vote-background-color-text");
        var BackgroundBarBorderColorInput = document.getElementById("vote-background-color-border-text");

        data = {
            type_id : type_id,
            style : style.value,
            text_color : TextColorInput.value,
            text_size : text_size.value,
            bar_color: BarColorInput.value,
            background_bar_color: BackgroundBarColorInput.value,
            background_bar_color_opacity: BackgroundBarColorOpacity.value,
            background_border: BackgroundColorInput.value,
            background_color : BackgroundBarBorderColorInput.value
        }

        var data_parse = JSON.stringify(data);

        window.pywebview.api.votes(data_parse);

    }

}


function createInitialVotes(parse) {

    var options = parse.options

    var votingDiv = document.getElementById('Voting');
    var endedDiv = document.getElementById('Ended');
    var resultListDiv = document.getElementById('result-list');
    var optionsListDiv = document.getElementById('options-list');
    
    if (parse.status == "Voting") {

        votingDiv.hidden = false;
        endedDiv.hidden = true;
        resultListDiv.hidden = true;
        optionsListDiv.innerHTML = '';
        
        var VotingName = document.createElement('h2');
        VotingName.textContent = `Votação para: ${parse.name}`;

        optionsListDiv.appendChild(VotingName);

        for (var key in options) {

            var option = options[key];
    
            var optionDiv = document.createElement('div');
            optionDiv.classList.add('d-flex', 'flex-column', 'mt-5');
    
            var optionName = document.createElement('p');
            optionName.textContent = `Opção: ${option.name}`;
    
            var optionVotes = document.createElement('p');
            optionVotes.textContent = `Votos: ${option.votes}`;
    
            var progressOuter = document.createElement('div');
            progressOuter.classList.add('progress-outer');
    
            var progressDiv = document.createElement('div');
            progressDiv.classList.add('progress');
            progressDiv.style.height = '10px';
            progressDiv.style.backgroundColor = '#ffffff';
    
            var progressBar = document.createElement('div');
            progressBar.classList.add('progress-bar', 'progress-bar-striped');
            progressBar.id = 'progress-bar';
            progressBar.style.height = '10px';
            progressBar.style.width = (option.votes / getMaxVotes(options) * 100) + '%';
            progressBar.style.backgroundColor = '#3f0365';
    
            progressDiv.appendChild(progressBar);
            progressOuter.appendChild(progressDiv);
    
    
            var removeButton = document.createElement('button');
            removeButton.classList.add('btn', 'bt-submit', 'mt-3');
            removeButton.textContent = 'Remover Opção';
    
            removeButton.addEventListener("click", async function () {
    
                removeOptionVote(key)
    
            });
    
            optionDiv.appendChild(optionName);
            optionDiv.appendChild(optionVotes);
            optionDiv.appendChild(progressOuter);
            optionDiv.appendChild(removeButton);
            optionsListDiv.appendChild(optionDiv);
        }

    } else if (parse.status == "Ended") {

        votingDiv.hidden = true;
        endedDiv.hidden = false;
        resultListDiv.hidden = false;
        resultListDiv.innerHTML = '';

        var VotingName = document.createElement('h2');
        VotingName.textContent = `Votação para: "${parse.name}" foi finalizada. `;

        resultListDiv.appendChild(VotingName);

        var winner = Object.keys(options).reduce(function (a, b) {
            return options[a].votes > options[b].votes ? a : b;
        });

        var winnerDiv = createResultDiv(winner, true, options);
        resultListDiv.appendChild(winnerDiv);

        var remainingOptions = Object.keys(options).filter(function (option) {
            return option !== winner;
        }).sort(function (a, b) {
            return options[b].votes - options[a].votes;
        });

        remainingOptions.forEach(function (option) {
            var optionDiv = createResultDiv(option, false, options);
            resultListDiv.appendChild(optionDiv);
        });

    }

}

function createResultDiv(option, isWinner, options) {

    var resultDiv = document.createElement('div');
    resultDiv.classList.add('result-item','mt-5');

    var optionName = document.createElement('p');
    optionName.textContent = `Opção: ${options[option].name}`;

    var optionVotes = document.createElement('p');
    optionVotes.textContent = `Votos: ${options[option].votes}`;

    var progressOuter = document.createElement('div');
    progressOuter.classList.add('progress-outer');

    var progressDiv = document.createElement('div');
    progressDiv.classList.add('progress');
    progressDiv.style.height = '10px';
    progressDiv.style.backgroundColor = '#ffffff';

    var progressBar = document.createElement('div');
    progressBar.classList.add('progress-bar', 'progress-bar-striped');
    progressBar.id = 'progress-bar';
    progressBar.style.height = '10px';
    progressBar.style.width = (options[option].votes / getMaxVotes(options) * 100) + '%';
    progressBar.style.backgroundColor = '#3f0365';

    progressDiv.appendChild(progressBar)
    progressOuter.appendChild(progressDiv)

    if (isWinner) {

        var optionNameWinner = document.createElement('h3');
        optionNameWinner.textContent = `Ganhador`;
        optionName.style.fontSize = '20px';
        optionVotes.style.fontSize = '17px';
        resultDiv.appendChild(optionNameWinner);
    }

    resultDiv.appendChild(optionName);
    resultDiv.appendChild(optionVotes);
    resultDiv.appendChild(progressOuter);

    return resultDiv;
}

function getMaxVotes(options) {
    return Math.max(...Object.values(options).map(option => option.votes), 0);
}



async function removeOptionVote(key) {

    data = {
        type_id: 'remove_options',
        option: key
    }

    var parse = await window.pywebview.api.votes(JSON.stringify(data));

    if (parse) {

        var parse = JSON.parse(parse)

        createInitialVotes(parse)

    }
}