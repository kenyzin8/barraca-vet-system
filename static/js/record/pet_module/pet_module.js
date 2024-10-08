var PetModule = {
    max_page: JSON.parse(document.getElementById('CM_max_page').textContent),
    dataRaw: JSON.parse(JSON.parse(document.getElementById('CM_dataRaw').textContent)),
    pets_length: JSON.parse(document.getElementById('CM_pets_length').textContent),
    logged_in_user: JSON.parse(document.getElementById('CM_logged_in_user').textContent),
    print_image: JSON.parse(document.getElementById('CM_print_image').textContent)
};

function showError(message) {
    $("#OKErrorModalButton").off("click");
    $('#errorModal .modal-body').text(message);
    $('#errorModal').modal('show');
}

window.addEventListener('DOMContentLoaded', event => {
    const datatablesSimple = document.getElementById('datatablesSimple');
    
    var max_page = PetModule.max_page;
    var lastIndex = max_page > 25 ? max_page : 50;
    var dataTable_Pet = null;
    if (datatablesSimple) {
        datatablesSimple.style.display = "";
        dataTable_Pet = new simpleDatatables.DataTable(datatablesSimple, {
            paging: true,
            perPageSelect: [5, 10, 25, lastIndex],
            perPage: 10,
            fixedHeight: false,
            sortable: true,
            searchable: true,
            hiddenHeader: false,
        });

        window.dataTable = dataTable_Pet;

        dataTable_Pet.on('datatable.update', () => {
            feather.replace();

            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })

            $('[data-bs-toggle="tooltip"]').tooltip('dispose');
            $('[data-bs-toggle="tooltip"]').tooltip({html: true});
        });

        dataTable_Pet.on('datatable.page', function(page) {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })

            $('[data-bs-toggle="tooltip"]').tooltip('dispose');
            $('[data-bs-toggle="tooltip"]').tooltip({html: true});
        });

        dataTable_Pet.on('datatable.search', function(query, matched) {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })

            $('[data-bs-toggle="tooltip"]').tooltip('dispose');
            $('[data-bs-toggle="tooltip"]').tooltip({html: true});
        });

        dataTable_Pet.on('datatable.sort', function(column, direction) {
            feather.replace();

            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })

            $('[data-bs-toggle="tooltip"]').tooltip('dispose');
            $('[data-bs-toggle="tooltip"]').tooltip({html: true});
        });

        var searchInput = document.querySelector('.datatable-input');
        
        searchInput.addEventListener('search', function(e) {
            if (e.target.value == '') {
                dataTable.search('');
            }
        });

        //initialize bootstrap tooltip
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        })

        $('[data-bs-toggle="tooltip"]').tooltip('dispose');
        $('[data-bs-toggle="tooltip"]').tooltip({html: true});
    }
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function getFormattedDate(date)
{
    var months = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    var day = date.getDate();
    day = day < 10 ? '0' + day : day;

    var monthIndex = date.getMonth();
    var year = date.getFullYear();

    var hours = date.getHours();
    var minutes = date.getMinutes();
    minutes = minutes < 10 ? '0' + minutes : minutes;

    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;

    var strTime = hours + ':' + minutes + ' ' + ampm;
    return formattedDate = months[monthIndex] + ' ' + day + ', ' + year + ' - ' + strTime;
}

function printTable()
{
    if(PetModule.dataRaw.length <= 0){
        showError("There are no pets to print.");
        return;
    }

    var dataRaw = PetModule.dataRaw;

    var font = "font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;"
    var css_gridHeaderStyle = `color: #232323; padding: 0px; border: 0px solid #232323; ${font}`;
    var css_gridStyle = `text-align: center; padding: 0px;border: 0px solid #232323; ${font};`;
    var css_headerStyle = `text-align: center; font-size: 14pt; color: #232323; font-weight: 600; margin-bottom: 20px; ${font}`;
    var headerName = "PET LIST";
    var imgSrc = PetModule.print_image;

    var date = new Date();
    var formattedDate = getFormattedDate(date);

    var header = `
            <div style='display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 0px solid #000;'>
                <div style='width: 70%; display: flex; flex-direction: column; align-items: flex-start;'>
                    <h1 style='${css_headerStyle}; font-family: Roboto;'>${headerName}</h1>
                    <div><span style='font-size:12pt;'><span style='font-size:12pt;font-weight:bold;'>Total Pets:</span> ${PetModule.pets_length}</span></div>
                    <div><span style='font-size:12pt;'><span style='font-size:12pt;font-weight:bold;'>Report Generated:</span> ${formattedDate}</span></div>
                </div>
                <img src='${imgSrc}' style='width: 30%;' />
            </div>
        `;

    var tableContent = dataRaw.map(c => 
    `
    <tr>
        <td>${c.id}</td>
        <td>${c.name}</td>
        <td>${c.species}</td>
        <td>${c.breed}</td>
        <td>${c.color}</td>
        <td>${c.gender}</td>
        <td>${c.birthday}</td>
        <td>${c.weight}</td>
        <td>${c.owner}</td>
        <td>${c.status}</td>
    </tr>
    `).join('');

    var completeHTML = `
        ${header}
        <table>
            <thead class="first-thead">
                <tr>
                    <th class="table-header">ID</th>
                    <th class="table-header">Name</th>
                    <th class="table-header">Species</th>
                    <th class="table-header">Breed</th>
                    <th class="table-header">Color</th>
                    <th class="table-header">Gender</th>
                    <th class="table-header">Birthday</th>
                    <th class="table-header">Weight (kg)</th>
                    <th class="table-header">Owner</th>
                    <th class="table-header">Status</th>
                </tr>
            </thead>
            <tbody class="first-tbody">
                ${tableContent}
            </tbody>
        </table>
        <div style="width: 100%; display: flex; justify-content: space-between; margin-top:70px;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <span style="font-size:9pt;font-weight:600;">‎</span>
                <span style='font-size:12pt;font-weight:600;'>‎</span>
                <span style="font-size:9pt;font-weight:600;">‎</span>
                <span style="font-size:9pt;font-weight:600;">‎</span>
                <span style='font-size:9pt;font-weight:600;'>‎</span>
                <span style='font-size:9pt;font-weight:600;'>‎</span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <span style='font-size:9pt;font-weight:600;'>Prepared by</span>
                <span style='font-size:12pt;font-weight:600;'>${PetModule.logged_in_user}</span>
                <span style="font-size:9pt;font-weight:600;">‎</span>
                <span style='font-size:9pt;font-weight:600;'>____________________________</span>
                <span style='font-size:9pt;font-weight:600;'>Date Signed</span>
            </div>
        </div>
    `;
    printJS({
        printable: completeHTML,
        type: 'raw-html',
        gridHeaderStyle: css_gridHeaderStyle,
        font_size: "15pt",
        documentTitle: 'Original Copy',
        showModal: true,
        header: header,
        gridStyle: css_gridStyle,
        modalMessage: 'Generating pet list report, this might take a while...',
        style: `
        @page { 
            size: auto;  
            margin: 5mm; 
        }
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif !important;
            color: #232323;
            margin: 45px 70px 45px 70px; 
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .first-thead th, .first-tbody td {
            padding: 8px 12px;
            text-align: center; 
            border-top: 0px solid black;
            border-bottom: 1px solid black;
        }

        .first-thead th, .first-tbody td {
            padding-bottom: 12px !important;
            padding-top: 12px !important;
            font-size:8pt;
        }
        
        .second-tbody td {
            border: none; 
            padding: 2px 2px;
            padding-top: 12px !important;
        }        
    `,
    });
}