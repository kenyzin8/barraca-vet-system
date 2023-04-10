function getCookie(name) 
{
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') 
    {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) 
        {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) 
            {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function sendSMS(client_ids) {
    const smsData = document.getElementById('sms-data');
    const sendSmsUrl = smsData.getAttribute('data-url');
    const csrftoken = getCookie('csrftoken');
    const sendSMSButton = document.getElementById("sendSMSButton");
    const cancelSMSButton = document.getElementById("cancelSMSButton");
    const smsSendingSpinner = document.getElementById("smsSendingSpinner");
    const closeSMSConfirmationButton = document.getElementById("close-sms-confirmation-button");

    sendSMSButton.disabled = true;
    sendSMSButton.value = "Sending..."
    cancelSMSButton.disabled = true;
    closeSMSConfirmationButton.disabled = true;
    smsSendingSpinner.classList.remove("d-none");

    const xhr = new XMLHttpRequest();
    xhr.open("POST", sendSmsUrl, true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            sendSMSButton.disabled = false;
            sendSMSButton.value = "Yes";
            cancelSMSButton.disabled = false;
            closeSMSConfirmationButton.disabled = false;
            smsSendingSpinner.classList.add("d-none");
            const messageModalBody = document.getElementById("messageModalBody");

            if (xhr.status === 200) {
                messageModalBody.textContent = JSON.parse(xhr.responseText).message;
            } else {
                messageModalBody.textContent = "Error sending SMS.";
            }

            var confirmModal = bootstrap.Modal.getInstance(document.getElementById("confirmationModal"));
            confirmModal.hide();

            var messageModal = new bootstrap.Modal(document.getElementById('messageModal'), {});
            messageModal.show();     
        }
    };


    xhr.send("client_ids=" + JSON.stringify(client_ids));
}

function confirmSendSMS(client_id, first_name, last_name, contact_number) {
    document.getElementById("hiddenClientId").value = client_id;

    document.getElementById("clientName").textContent = first_name + ' ' + last_name;
    document.getElementById("clientPhoneNumber").textContent = contact_number;

    var confirmModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
    confirmModal.show();
}

function confirmSendBulkSMS() {
    var bulkConfirmModal = new bootstrap.Modal(document.getElementById('bulkConfirmationModal'), {});
    bulkConfirmModal.show();
}

function sendBulkSMS() {
    const smsData = document.getElementById("sms-data");
    const sendSmsUrl = smsData.getAttribute("data-url");
    const csrftoken = getCookie("csrftoken");
    const sendBulkSMSButton = document.getElementById("sendBulkSMSButton");
    const cancelBulkSMSButton = document.getElementById("cancelBulkSMSButton");
    const closeBulkSMSButton = document.getElementById("closeBulkSMSButton");
    const bulkSMSSendingSpinner = document.getElementById("bulkSMSSendingSpinner");

    sendBulkSMSButton.disabled = true;
    cancelBulkSMSButton.disabled = true;
    closeBulkSMSButton.disabled = true;
    bulkSMSSendingSpinner.classList.remove("d-none");

    const totalPages = getLastPage();
    let allClientIDs = [];

    function fetchClients(page) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", "?page=" + page, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        const data = JSON.parse(xhr.responseText);
                        const clientIDs = data.clients.map((client) => client.id);
                        resolve(clientIDs);
                    } else {
                        reject();
                    }
                }
            };
            xhr.send();
        });
    }

    Promise.all([...Array(totalPages).keys()].map((_, i) => fetchClients(i + 1)))
        .then((clientIDsArray) => {
            allClientIDs = clientIDsArray.flat();

            const xhr = new XMLHttpRequest();
            xhr.open("POST", sendSmsUrl, true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    sendBulkSMSButton.disabled = false;
                    cancelBulkSMSButton.disabled = false;
                    closeBulkSMSButton.disabled = false;
                    bulkSMSSendingSpinner.classList.add("d-none");

                    const messageModalBody = document.getElementById("messageModalBody");

                    if (xhr.status === 200) {
                        messageModalBody.textContent = JSON.parse(xhr.responseText).message;
                    } else {
                        messageModalBody.textContent = "Error sending SMS.";
                    }

                    const bulkConfirmModal = bootstrap.Modal.getInstance(document.getElementById("bulkConfirmationModal"));
                    bulkConfirmModal.hide();

                    const messageModal = new bootstrap.Modal(document.getElementById("messageModal"), {});
                    messageModal.show();
                }
            };
            xhr.send("client_ids=" + JSON.stringify(allClientIDs));
        })
        .catch(() => {
            sendBulkSMSButton.disabled = false;
            cancelBulkSMSButton.disabled = false;
            closeBulkSMSButton.disabled = false;
            bulkSMSSendingSpinner.classList.add("d-none");
            alert("Error fetching client IDs.");
        });
}


function navigatePage(direction) {
    const tableContainer = document.querySelector(".table-container");
    let currentPage = parseInt(tableContainer.getAttribute("data-page"));

    currentPage += direction;
    tableContainer.setAttribute("data-page", currentPage);

    updateButtonStates(currentPage);

    const xhr = new XMLHttpRequest();
    xhr.open("GET", "?page=" + currentPage, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);

                let tableBody = document.querySelector(".table tbody");
                tableBody.innerHTML = "";

                data.clients.forEach((client) => {
                    let row = document.createElement("tr");

                    row.innerHTML = `
                        <th scope="row">${client.id}</th>
                        <td>${client.first_name} ${client.last_name}</td>
                        <td>${client.contact_number}</td>
                        <td>
                            <button type="button" class="btn btn-primary" onclick="confirmSendSMS('${client.id}', '${client.first_name}', '${client.last_name}', '${client.contact_number}')">
                                Notify
                            </button>
                        </td>
                    `;

                    tableBody.appendChild(row);
                });
            } else {
                currentPage -= direction;
                tableContainer.setAttribute("data-page", currentPage);

                updateButtonStates(currentPage);
            }
        }
    };
    xhr.send();
}

function updateButtonStates(currentPage) {
    const prevButton = document.getElementById("prevPage");
    const nextButton = document.getElementById("nextPage");

    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === getLastPage();
}

function getLastPage() {
    const tableContainer = document.querySelector(".table-container");
    const totalClients = parseInt(tableContainer.getAttribute("data-total"));
    const clientsPerPage = parseInt(tableContainer.getAttribute("data-per-page"));

    return Math.ceil(totalClients / clientsPerPage);
}

document.addEventListener("DOMContentLoaded", function () {
    updateButtonStates(parseInt(document.querySelector(".table-container").getAttribute("data-page")));
});
