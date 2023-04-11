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
    const tableRows = document.querySelectorAll('tbody tr');
    const contactNumbers = Array.from(tableRows).map(row => row.children[2].textContent);

    const contactNumbersText = contactNumbers.join(', ');

    const modalBody = document.querySelector('.bulk-modal-body');
    modalBody.innerHTML = `Are you sure you want to send SMS reminders to all clients?<br>Contact Numbers: ${contactNumbersText}`;

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

    const allClientIDs = Array.from(document.querySelectorAll("tbody tr")).map((row) => row.children[0].textContent);

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
}