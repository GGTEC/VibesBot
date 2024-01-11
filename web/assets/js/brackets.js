let completedMatches = 0;
let opponents = 0;



function checkThirdPlaceMatch(matchDataArray) {
    if (matchDataArray.length === 3 && matchDataArray[2].participants.length === 2) {
        const thirdMatchParticipants = matchDataArray[2].participants;
        const firstMatchParticipants = matchDataArray[0].participants;
        const secondMatchParticipants = matchDataArray[1].participants;

        const isThirdMatchParticipantsInFirstAndSecondMatch =
            thirdMatchParticipants.every(participant =>
                firstMatchParticipants.includes(participant) || secondMatchParticipants.includes(participant)
            );

        if (isThirdMatchParticipantsInFirstAndSecondMatch) {
            document.getElementById('thirMatchesnotice').hidden = false
        } else {
            document.getElementById('thirMatchesnotice').hidden = true
        }
    }
}

async function partLength(response) {

    if (Object.keys(response).length > 0) {

        opponents = 0;

        document.getElementById("brackets").innerHTML = ""
    
        const matchDataArray = Object.values(response);
    
        document.getElementById("div-create-champ").hidden = true;
    
        for (const matchKey in matchDataArray) {
    
            const matchData = matchDataArray[matchKey];
    
            opponents += matchData.participants.length;
    
        }
    
        for (const matchData of matchDataArray) {
            createTableAndButtons(matchData);
        }
    
        if (opponents == 2) {
    
            document.getElementById("ClearMatches").hidden = true;
            document.getElementById("EndChamp").hidden = false;
    
        } else {
            document.getElementById("ClearMatches").hidden = false;
            document.getElementById("EndChamp").hidden = true;
        }
    
        checkThirdPlaceMatch(matchDataArray);
    }
    
}

async function createTablePart(users) {

    var dataTableData = [];

    $.each(users, function (index, value) {

        var button_config = document.createElement("button");

        button_config.innerText = "Remover";
        button_config.classList.add('bnt', 'bt-submit')
        button_config.setAttribute('onclick', `removePart('${value.replace("'", "\\'")}')`)

        dataTableData.push([
            value,
            button_config.outerHTML
        ]);


    });


    if ($.fn.DataTable.isDataTable("#campusers_table")) {

        $('#campusers_table').DataTable().clear().draw();
        $('#campusers_table').DataTable().destroy();
    }


    var table = $('#campusers_table').DataTable({
        destroy: true,
        scrollX: true,
        paging: false,
        ordering: false,
        retrieve: false,
        processing: true,
        responsive: false,
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/pt-BR.json'
        },
        columns: [
            { title: 'Usuário' },
            { title: 'Remover' },
        ]
    });


    for (var i = 0; i < dataTableData.length; i++) {
        table.row.add(dataTableData[i]).draw();
    }
}

async function removePart(user) {

    const data_send = {
        type_id: 'remove',
        data: user
    };

    var response_part = await window.pywebview.api.camp_command(JSON.stringify(data_send));

    if (response_part) {

        response_part = JSON.parse(response_part)

        createTablePart(response_part)

    }
}

async function getMatchesLoad() {

    var data_send = {
        type_id: 'get_matches',
        data: 'None'
    };

    var response = await window.pywebview.api.camp_command(JSON.stringify(data_send));

    if (response) {

        response = JSON.parse(response)

        partLength(response)

    }

    var data_send_parti = {
        type_id: 'get_participants',
        data: 'None'
    };

    var response_part = await window.pywebview.api.camp_command(JSON.stringify(data_send_parti));

    if (response_part) {

        response_part = JSON.parse(response_part)

        createTablePart(response_part)

    }

}

async function getMatches() {

    const data_send = {
        type_id: 'start_matches',
        data: 'None'
    };

    const response = await window.pywebview.api.camp_command(JSON.stringify(data_send));

    if (response) {

        partLength(response)

    }

}

async function disableMatch(status, match) {

    const data_send = {
        type_id: 'disable_match',
        status: status,
        match: match
    };

    const response = await window.pywebview.api.camp_command(JSON.stringify(data_send));

    if (response) {

        partLength(response)

    }

}

async function endMatches() {

    completedMatches = 0;
    opponents = 0;

    const data_send = {
        type_id: 'end_matches',
        data: 'None'
    };

    const response = await window.pywebview.api.camp_command(JSON.stringify(data_send));

    if (response) {

        const container = document.getElementById("brackets");

        container.innerHTML = "";

        partLength(response)

    }
}

async function endCamp() {

    completedMatches = 0;
    opponents = 0;

    const data_send = {
        type_id: 'end_champ',
        data: 'None'
    };

    const response = await window.pywebview.api.camp_command(JSON.stringify(data_send));

    if (response) {

        const container = document.getElementById("brackets");

        container.innerHTML = "";

        document.getElementById("div-champ").hidden = true;
        document.getElementById("div-winner").hidden = false;
        document.getElementById("winner-name").innerHTML = response[0].winner;
        document.getElementById("winner-name-2").innerHTML = response[0].second;
        document.getElementById("winner-name-3").innerHTML = response[0].third;

    }
}

function startCamp() {
    document.getElementById("div-create-champ").hidden = false;
    document.getElementById("div-winner").hidden = true;
}

function checkAllMatchesCompleted() {

    const ClearButton = document.getElementById("ClearMatches");

    if (completedMatches == opponents) {
        ClearButton.disabled = false
    } else {
        ClearButton.disabled = true
    }

}

function createTableAndButtons(matchData) {

    const container = document.getElementById("brackets");

    const matchDiv = document.createElement("div");
    matchDiv.className = "match mt-5 bg-dark form-block";

    const matchName = document.createElement("h5");
    matchName.textContent = `Partida ${matchData.match}`;
    matchDiv.appendChild(matchName);

    const table = document.createElement("table");
    table.className = "table";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    const headerCell1 = document.createElement("th");
    headerCell1.textContent = "Participantes";

    const headerCell2 = document.createElement("th");
    headerCell2.textContent = "Ação";

    headerRow.appendChild(headerCell1);
    headerRow.appendChild(headerCell2);

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    for (let j = 0; j < matchData.participants.length; j++) {

        const row = document.createElement("tr");
        const cell1 = document.createElement("td");
        cell1.textContent = matchData.participants[j];
        row.appendChild(cell1);

        const actionCell = document.createElement("td");
        const selectButton = document.createElement("button");
        selectButton.classList.add("btn", "btn-sm", "bt-submit");
        selectButton.textContent = "Vencedor";

        if (matchData.match_status == true && matchData.winner === matchData.participants[j]) {
            selectButton.disabled = true;
            completedMatches += matchData.participants.length;
        }

        selectButton.addEventListener("click", async function () {

            selectButton.disabled = true;

            matchData.match_status = true;
            matchData.winner = matchData.participants[j];
            completedMatches += matchData.participants.length;

            sendDataToBackend('winner', matchData);

            checkAllMatchesCompleted();

        });

        actionCell.appendChild(selectButton);
        row.appendChild(actionCell);

        tbody.appendChild(row);

        if (matchData.participants.length === 1) {
            selectButton.disabled = true
        }
    }

    table.appendChild(tbody);
    matchDiv.appendChild(table);

    if (matchData.participants.length === 1) {
        const noteText = document.createElement("p");
        noteText.className = "small";
        noteText.textContent = "O participante desta partida enfrentará o perdedor da primeira, e em caso de apenas duas partidas, o vencedor da segunda avançará para a final junto com o vencedor da primeira.*";
        matchDiv.appendChild(noteText);
    }

    const disableCheckbox = document.createElement("div");
    disableCheckbox.className = "form-group";
    disableCheckbox.innerHTML = `
        <div class="row mt-3">
            <div class="col">
                <p class="form-check-label">
                    Desabilitar partida
                </p>
            </div>
            <div class="col-2">
                <div class="material-switch bg-white d-flex justify-content-end">
                    <input type="checkbox" id="disableCheckbox_${matchData.match}" />
                    <label class="form-check-label" for="disableCheckbox_${matchData.match}"></label>
                </div>
            </div>
        </div>
    `;

    if (matchData.match_status == 'Disabled') {
        disableCheckbox.querySelector("input").checked = true;
        completedMatches += matchData.participants.length;

        const buttons = matchDiv.querySelectorAll("button");
        buttons.forEach(button => {
            if (buttons.length > 1) {
                button.disabled = true;
            }
        });

    }

    disableCheckbox.querySelector("input").addEventListener("change", function () {

        const checkbox = this;
        matchData.match_status = checkbox.checked;

        const buttons = matchDiv.querySelectorAll("button");
        buttons.forEach(button => {
            if (buttons.length > 1) {
                button.disabled = checkbox.checked;
            }
        });

        if (checkbox.checked) {
            completedMatches += matchData.participants.length;
            disableMatch("Disabled", matchData.match);

        } else {
            completedMatches -= matchData.participants.length;
            disableMatch("false", matchData.match);
        }


        checkAllMatchesCompleted();

    });

    matchDiv.appendChild(disableCheckbox);
    container.appendChild(matchDiv);

    document.getElementById("div-champ").hidden = false;

    checkAllMatchesCompleted();
}

async function sendDataToBackend(type_id, data) {

    completedMatches = 0

    const data_send = {
        type_id: type_id,
        data: data
    };

    if (type_id == 'winner') {

        const response = await window.pywebview.api.camp_command(JSON.stringify(data_send));

        const scrollPosition = document.documentElement.scrollTop || document.body.scrollTop;

        if (response) {

            const container = document.getElementById("brackets");

            container.innerHTML = "";

            partLength(response)

            document.documentElement.scrollTop = document.body.scrollTop = scrollPosition;
        }

    } else {

        window.pywebview.api.camp_command(JSON.stringify(data_send));
    }

}

