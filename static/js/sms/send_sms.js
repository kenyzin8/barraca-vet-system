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

function sendSMS(phone_number, appointment_id) {
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

    xhr.send("phone_numbers=" + JSON.stringify(phone_number) + 
    "&appointment_id=" + appointment_id);

}

function confirmSendSMS(appointment_id, client, contact_number) {
    document.getElementById("hiddenClientPhone").value = contact_number;
    document.getElementById("hiddenAppointmentID").value = appointment_id;

    document.getElementById("clientName").textContent = client;
    document.getElementById("clientPhoneNumber").textContent = contact_number;

    var confirmModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
    confirmModal.show();
}

function confirmSendBulkSMS() {
    const tableRows = document.querySelectorAll('.appointments-list-table tbody tr');
    const contactNames = Array.from(tableRows).map(row => row.children[1].textContent);
    const contactNumbers = Array.from(tableRows).map(row => row.children[2].textContent);

    const contacts = contactNames.map((name, i) => `${name} (${contactNumbers[i]})`);
    const contactsText = contacts.join(' <br> ');

    const modalBody = document.querySelector('.bulk-modal-body');
    modalBody.innerHTML = `Are you sure you want to send SMS reminders to all clients?<br><br><b>Contact List:</b> <br>${contactsText}`;

    const bulkConfirmModal = new bootstrap.Modal(document.getElementById('bulkConfirmationModal'), {});
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

    const allPhoneNumbers = Array.from(document.querySelectorAll(".appointments-list-table tbody tr")).map((row) => row.children[2].textContent);
    const allAppointmentIDs = Array.from(document.querySelectorAll(".appointments-list-table tbody tr")).map((row) => row.children[0].textContent);
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
    xhr.send("phone_numbers=" + JSON.stringify(allPhoneNumbers) + "&appointment_id=" + JSON.stringify(allAppointmentIDs));
}