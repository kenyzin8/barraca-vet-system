var ClientModule = {
    max_page: JSON.parse(document.getElementById('CM_max_page').textContent),
    dataRaw: JSON.parse(JSON.parse(document.getElementById('CM_dataRaw').textContent)),
    clients_length: JSON.parse(document.getElementById('CM_clients_length').textContent),
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
    
    var lastIndex = ClientModule.max_page > 25 ? ClientModule.max_page : 50;
    
    if (datatablesSimple) {
        datatablesSimple.style.display = "";
        let dataTable = new simpleDatatables.DataTable(datatablesSimple, {
            paging: true,
            perPageSelect: [5, 10, 25, lastIndex],
            perPage: 10,
            fixedHeight: false,
            sortable: true,
            searchable: true,
            hiddenHeader: false,
            columns: [
            {
                select: 6,
                filter: ["Walk-In Registered", "Online Registered"]
            }
            ],
        });

        window.dataTable = dataTable;

        dataTable.on('datatable.update', () => {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        dataTable.on('datatable.page', function(page) {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        dataTable.on('datatable.search', function(query, matched) {
            feather.replace();

            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        dataTable.on('datatable.sort', function(column, direction) {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
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

function printTable(tableID) 
{
    if(ClientModule.dataRaw.length <= 0) {
        showError("There are no clients to print.");
        return;
    }

    var font = "font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;"
    var css_gridHeaderStyle = `color: #232323; padding: 0px; border: 0px solid #232323; ${font}`;
    var css_gridStyle = `text-align: center; padding: 0px;border: 0px solid #232323; ${font};`;
    var css_headerStyle = `text-align: center; font-size: 14pt; color: #232323; font-weight: 600; margin-bottom: 20px; ${font}`;
    var headerName = "CLIENT LIST";
    var imgSrc = ClientModule.print_image;

    var date = new Date();
    var formattedDate = getFormattedDate(date);

    var header = `
            <div style='display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 0px solid #000;'>
                <div style='width: 70%; display: flex; flex-direction: column; align-items: flex-start;'>
                    <h1 style='${css_headerStyle}; font-family: Roboto;'>${headerName}</h1>
                    <div><span style='font-size:12pt;'><span style='font-size:12pt;font-weight:bold;'>Total Clients:</span> ${ClientModule.clients_length}</span></div>
                    <div><span style='font-size:12pt;'><span style='font-size:12pt;font-weight:bold;'>Report Generated:</span> ${formattedDate}</span></div>
                </div>
                <img src='${imgSrc}' style='width: 30%;' />
            </div>
        `;

    var tableContent = ClientModule.dataRaw.map(c => 
    `
    <tr>
        <td>${c.id}</td>
        <td>${c.name}</td>
        <td>${c.gender}</td>
        <td style="font-size:12px;">${c.address}</td>
        <td>${c.contact_number}</td>
        <td>${c.total_pets}</td>
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
                    <th class="table-header">Gender</th>
                    <th class="table-header">Address</th>
                    <th class="table-header">Phone</th>
                    <th class="table-header">Total Pets</th>
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
                <span style='font-size:12pt;font-weight:600;'>${ClientModule.logged_in_user}</span>
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
        modalMessage: 'Generating client list report, this might take a while...',
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
            font-size: 11pt;
        }

        .second-tbody td {
            border: none; 
            padding: 2px 2px;
            padding-top: 12px !important;
        }        
    `,
    });
}