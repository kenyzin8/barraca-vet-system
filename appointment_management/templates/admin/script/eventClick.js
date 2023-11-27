
var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
const dateString = arg.event.start;
const date = new Date(dateString);
const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const day = monthNames[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear();

var isDaySentIcon = arg.event.extendedProps.day_sms_reminder == false ? '<i data-feather="x-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="Pending SMS"></i>' : '<i data-feather="check-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="SMS Sent"></i>';
var isWeekSentIcon = arg.event.extendedProps.week_sms_reminder == false ? '<i data-feather="x-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="Pending SMS"></i>' : '<i data-feather="check-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="SMS Sent"></i>';
var isHourSentIcon = arg.event.extendedProps.hour_sms_reminder == false ? '<i data-feather="x-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="Pending SMS"></i>' : '<i data-feather="check-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="SMS Sent"></i>';
var isTodaySentIcon = arg.event.extendedProps.today_sms_reminder == false ? '<i data-feather="x-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="Pending SMS"></i>' : '<i data-feather="check-circle" style="margin-top: 4px;" data-bs-toggle="tooltip" data-bs-placement="right" title="SMS Sent"></i>';

var year = dateString.getFullYear();
var month = (dateString.getMonth() + 1).toString().padStart(2, '0');
var _day = dateString.getDate().toString().padStart(2, '0');

var formattedDate = `${year}-${month}-${_day}`;

let dateIsDisabled = false;

for (let i = 0; i < disabledDays.length; i++) {
    if (disabledDays[i].date === formattedDate) {
        dateIsDisabled = true;
        break;
    }
}

let timeOfDay = arg.event.extendedProps.time;
let [hours, minutes] = timeOfDay.split(":");
let _date = new Date(1970, 0, 1, hours, minutes); 

timeOfDay = _date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });

document.getElementById('btn-create-health-card').onclick = function () {
    var url = "{% url 'admin-add-pet-health-card-treatment-page' %}?pet_id=0";
    url = url.replace('0', arg.event.extendedProps.pet_id);

    window.open(url, '_blank');
}

document.getElementById('btn-create-medical-record').onclick = function () {
    var url = "{% url 'admin-medical-record-page' %}?pet_id=0&symtomps=SYMPTOMS";
    url = url.replace('0', arg.event.extendedProps.pet_id);
    url = url.replace('SYMPTOMS', arg.event.extendedProps.symtomps);
    console.log(url)

    window.open(url, '_blank');
}

document.getElementById('btn-create-prescription').onclick = function () {
    var url = "{% url 'admin-add-pet-medical-prescription-page' %}?pet_id=0";
    url = url.replace('0', arg.event.extendedProps.pet_id);

    window.open(url, '_blank');
}

const timeDetails = dateIsDisabled
    ? `<strong>Time:</strong> ${timeOfDay}`
    : `<strong>Time:</strong> ${timeOfDay} <a id="${arg.event.id}" class="btn btn-datatable btn-icon btn-transparent-dark btn-change-time" href="#!" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit time of the day"><i data-feather="edit"></i></a>`;

const details = [
    `<strong>Client:</strong> ${arg.event.extendedProps.client}`,
    `<strong>Pet:</strong> ${arg.event.extendedProps.pet} <a id="${arg.event.id}" class="btn btn-datatable btn-icon btn-transparent-dark" target="_blank" href="${`{% url 'admin-view-pet-page' 0 %}`.replace('0', arg.event.extendedProps.pet_id)}" data-bs-toggle="tooltip" data-bs-placement="top" title="View pet details"><i data-feather="external-link"></i></a>`,
    timeDetails,
    arg.event.extendedProps.purpose == null ? `<strong>Purpose:</strong> None` : `<strong>Purpose:</strong> ${arg.event.extendedProps.purpose}`,
    arg.event.extendedProps.symtomps == '' ? `<strong>Symtomps:</strong> None` : `<strong>Symtomps:</strong> ${arg.event.extendedProps.symtomps}`,
].join('<br>');

document.getElementById('eventModalLabel').innerText = "#" + arg.event.id + " - " + day;
document.getElementById('eventModalBody').innerHTML = details;
feather.replace();
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})
eventModal.show();

var popover = document.querySelector('.fc-popover');
if (popover) {
    popover.style.display = 'none';
}

var deleteAppointmentModal = new bootstrap.Modal(document.getElementById('deleteAppointmentModal'));

document.getElementById('deleteEvent').onclick = function() {
    eventModal.hide();
    deleteAppointmentModal.show();
};

document.getElementById('yesDeleteAppointmentButton').onclick = function() {
    var reason = document.getElementById('cancel-appointment-reason').value;
    if(reason == ""){
        deleteAppointmentModal.hide();
        showError("Please enter a reason for cancellation.");

        $('#OKErrorModalButton').on('click', function() {
            $('#errorModal').modal('hide');
            deleteAppointmentModal.show();
        });
        return;
    }
    $.ajax({
        type: 'POST',
        url: '{% url "cancel_appointment" %}',
        data: {
            'appointment_id': arg.event.id,
            'reason': $('#cancel-appointment-reason').val(),
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(response) {
            if (response.status === 'Appointment cancelled successfully') {
                // arg.event.remove();
                // eventModal.hide();
                // deleteAppointmentModal.hide();
                // showSuccess(response.status + ".");
                // // var currentView = calendar.view;
                // // localStorage.setItem('calendarDate', currentView.currentStart.toISOString());
                // // location.reload();

                var appointmentDate = new Date(response.appointment_date);

                var index = allAppointments.findIndex((event) => {
                    return Number(event.id) === Number(arg.event.id);
                });

                if (index > -1) {
                    allAppointments.splice(index, 1);
                }

                var info = {
                    event: {
                        id: arg.event.id
                    },
                    oldEvent: {
                        start: response.appointment_date
                    },
                    type: 'mark_done'
                };

                updateSlots(info, appointmentDate, dateSlots, maxAppointments, allAppointments, slotElements);
                arg.event.remove();
                updateTimeOfTheDayCell(response.appointment_date, timeOfDayInfo, timeOfTheDayElements);
                $('#deleteAppointmentModal').modal('hide');
                showSuccess(response.status);
                hideRebookList();

            }
        },
        error: function(error) {
            deleteAppointmentModal.hide();
            showError(error.responseJSON.message);
        }
    });
};

var cancelDeleteAppointmentButton = document.getElementsByClassName('cancelDeleteAppointmentButton');
for (var i = 0; i < cancelDeleteAppointmentButton.length; i++) {
    cancelDeleteAppointmentButton[i].onclick = function() {
        deleteAppointmentModal.hide();
        eventModal.show();
    };
}

document.getElementById('rebookEvent').onclick = function() {
    eventModal.hide();
    $('#rebookConfModal').modal('show');
};

document.getElementById('yesRebookConfButton').onclick = function() {
    $.ajax({
        type: 'POST',
        url: '{% url "add_to_rebook_list" %}',
        data: {
            'appointment_id': arg.event.id,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(response) {
            if (response.status === 'Appointment rebooked successfully') {
                var oldDate = new Date(arg.event.start);
                var oldDateString = oldDate.getFullYear() + '-' + String(oldDate.getMonth() + 1).padStart(2, '0') + '-' + String(oldDate.getDate()).padStart(2, '0');

                var info = {
                    event: {
                        id: arg.event.id
                    },
                    oldEvent: {
                        start: oldDateString
                    }
                };

                var index = allAppointments.findIndex((event) => {
                    return Number(event.id) === Number(arg.event.id);
                });

                if (index > -1) {
                    allAppointments.splice(index, 1);
                }

                updateSlots(info, oldDateString, dateSlots, maxAppointments, allAppointments, slotElements);

                var rebookList = document.getElementById('external-events-list');

                var rebookEvent = document.createElement('div');
                rebookEvent.classList.add('fc-event', 'fc-h-event', 'fc-daygrid-event', 'fc-daygrid-block-event', 'custom-rebook-color');
                rebookEvent.id = arg.event.id;

                rebookEvent.dataset.clientId = arg.event.extendedProps.client_id;
                rebookEvent.dataset.clientName = arg.event.extendedProps.client;
                rebookEvent.dataset.petId = arg.event.extendedProps.pet_id;
                rebookEvent.dataset.petName = arg.event.extendedProps.pet;
                rebookEvent.dataset.purposeId = arg.event.extendedProps.purpose_id;
                rebookEvent.dataset.purposeVal = arg.event.extendedProps.purpose;
                rebookEvent.dataset.timeOfDay = arg.event.extendedProps.timeOfTheDay_val;
                rebookEvent.dataset.daySmsSent = arg.event.extendedProps.day_sms_reminder;
                rebookEvent.dataset.weekSmsSent = arg.event.extendedProps.week_sms_reminder;
                rebookEvent.dataset.contactNumber = arg.event.extendedProps.contact_number;
                rebookEvent.dataset.currentDate = arg.event.extendedProps.current_date;
                rebookEvent.dataset.appointmentSymtomps = arg.event.extendedProps.symtomps == "" ? "None" : arg.event.extendedProps.symtomps;

                console.log(arg.event);

                rebookEvent.onclick = function() {
                    _showAppointmentDetails(arg.event);
                };

                var eventMainDiv = document.createElement('div');
                eventMainDiv.classList.add('fc-event-main');
                eventMainDiv.innerHTML = '#' + arg.event.id + ' - ' + arg.event.extendedProps.client; 
                rebookEvent.appendChild(eventMainDiv);
                rebookList.appendChild(rebookEvent);

                arg.event.remove();
                updateTimeOfTheDayCell(oldDateString, timeOfDayInfo, timeOfTheDayElements);

                eventModal.hide();
                $('#rebookConfModal').modal('hide');
                showSuccess("Appointment #" + arg.event.id + " has been added to rebook list.");
                showRebookList();
                calendar.refetchEvents();
                refreshCalendar();
                // arg.event.remove();
                // eventModal.hide();
                // $('#rebookConfModal').modal('hide');
                // showSuccess(response.status + ".");
                // // var currentView = calendar.view;
                // // localStorage.setItem('calendarDate', currentView.currentStart.toISOString());
                // // location.reload();
            }
        },
        error: function(error) {
            $('#rebookConfModal').modal('hide');
            showError(error.responseJSON.message);
        }
    });
}

var cancelRebookConfButtons = document.getElementsByClassName('cancelRebookConfButton');
for (var i = 0; i < cancelRebookConfButtons.length; i++) {
    cancelRebookConfButtons[i].onclick = function() {
        $('#rebookConfModal').modal('hide');
        eventModal.show();
    };
}

var changeTimeButtons = document.getElementsByClassName("btn-change-time");
for (var i = 0; i < changeTimeButtons.length; i++) {
    changeTimeButtons[i].onclick = function() {
        var appointment_id = this.id;
        var appointment_date = arg.event.start;
        var modal_date_text = document.getElementsByClassName("day-clicked-time-change");

        for(var i = 0; i < modal_date_text.length; i++){
            modal_date_text[i].textContent = appointment_date.toLocaleDateString();
        }

        var modal_appointment_id_text = document.getElementsByClassName("day-clicked-time-change-id");

        for(var i = 0; i < modal_appointment_id_text.length; i++){
            modal_appointment_id_text[i].textContent = appointment_id;
        }
        
        var current_time_of_the_day = arg.event.extendedProps.time;
        var time_of_the_day_change_select = document.getElementById("id_time-change");
        
        $.ajax({
            url: "{% url 'get-busy-times' %}", 
            method: "GET",
            data: {
                service_id: arg.event.extendedProps.purpose_id,
                date: arg.event.extendedProps.current_date
            },
            success: function(response) {
                if (response.status === "success") {
                    const busyTimes = response.busy_times;

                    $('#id_time-change option').show();

                    busyTimes.forEach(function(time) {
                        $("#id_time-change option[value='" + time + "']").hide();
                    });

                    var firstAvailableTime = $('#id_time-change option:visible:first').val();
                    $('#id_time-change').val(firstAvailableTime);
                }
            },
            error: function(error) {
                showError("Failed to fetch busy times:", error);
            }
        });
        
        for (var i = 0; i < time_of_the_day_change_select.options.length; i++) {
            if (time_of_the_day_change_select.options[i].value == current_time_of_the_day) {
                time_of_the_day_change_select.options[i].selected = true;
                break;
            }
        }

        $("#adjustTimeOfTheDayModal").modal("show");

        var submitButton = document.getElementById("yesAdjustTimeOfTheDayModalButton");
        submitButton.onclick = function() {

            var new_time = document.getElementById("id_time-change").value;

            $.ajax({
                type: 'POST',
                url: '{% url "set-time-of-the_day" %}',
                data: {
                    'appointment_id': appointment_id,
                    'new_time': new_time,
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                success: function(response) {
                    $('#adjustTimeOfTheDayModal').modal('hide');

                    var newColor;
                    var newTimeOfDay;
                    var newTimeOfDayVal;
                   
                    if(response.new_time && (response.new_time >= "07:30:00" && response.new_time < "12:00:00")){
                        newTimeOfDayVal = 'morning';
                        newTimeOfDay = 'Morning';
                        newColor = '#3788d8';
                    }
                    else if(response.new_time && (response.new_time >= "12:00:00" && response.new_time < "18:00:00")){
                        newTimeOfDayVal = 'afternoon';
                        newTimeOfDay = 'Afternoon';
                        newColor = 'green';
                    }

                    arg.event.setExtendedProp('timeOfTheDay_val', newTimeOfDayVal);
                    arg.event.setExtendedProp('timeOfTheDay', newTimeOfDay);
                    arg.event.setExtendedProp('time', response.new_time)
                    arg.event.setProp('borderColor', newColor);
                    arg.event.setProp('backgroundColor', newColor);
                    arg.event.setStart(response.date + "T" + response.new_time)
                    
                    sortEventsForDate(calendar, response.date + "T" + response.new_time);

                    for(var i = 0; i < allAppointments.length; i++) {
                        if(allAppointments[i].id == appointment_id) {
                            allAppointments[i].color = newColor;
                            allAppointments[i].extendedProps.timeOfTheDay = newTimeOfDay;
                            allAppointments[i].extendedProps.timeOfTheDay_val = newTimeOfDayVal;
                            allAppointments[i].extendedProps.time = response.new_time;
                            break;
                        }
                    }

                    showSuccess(response.message);
                },
                error: function(error) {
                    $('#adjustTimeOfTheDayModal').modal('hide');
                    showError(error.responseJSON.message);
                }
            });
        };
        eventModal.hide();
    }
}

var cancelAdjustTimeOfTheDayModalButton = document.getElementById('cancelAdjustTimeOfTheDayModalButton');
cancelAdjustTimeOfTheDayModalButton.onclick = function() {
    $("#adjustTimeOfTheDayModal").modal("hide");
    eventModal.show();
};

var cancelRebookConfButtons = document.getElementsByClassName('cancelRebookConfButton');
for (var i = 0; i < cancelRebookConfButtons.length; i++) {
    cancelRebookConfButtons[i].onclick = function() {
        $('#rebookConfModal').modal('hide');
        eventModal.show();
    };
}

document.getElementById('doneEvent').onclick = function() {
    appointmentIdToMarkDone = arg.event.id;
    eventModal.hide();
    $('#doneAppointmentModal').modal('show');
};

document.getElementById('yesDoneAppointmentButton').onclick = function() {
    $.ajax({
        type: 'POST',
        url: '{% url "mark_as_done" %}',
        data: {
            'appointment_id': arg.event.id,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function(response) {
            if (response.status === 'Appointment marked as done successfully.') {
                var appointmentDate = new Date(response.appointment_date);

                var index = allAppointments.findIndex((event) => {
                    return Number(event.id) === Number(arg.event.id);
                });

                if (index > -1) {
                    allAppointments.splice(index, 1);
                }

                var info = {
                    event: {
                        id: arg.event.id
                    },
                    oldEvent: {
                        start: response.appointment_date
                    },
                    type: 'mark_done'
                };

                updateSlots(info, appointmentDate, dateSlots, maxAppointments, allAppointments, slotElements);

                arg.event.remove();

                updateTimeOfTheDayCell(response.appointment_date, timeOfDayInfo, timeOfTheDayElements);

                $('#doneAppointmentModal').modal('hide');
                showSuccess(response.status);
                hideRebookList();
            } else {
                showError(response.message);
            }
        },
        error: function(error) {
            $('#doneAppointmentModal').modal('hide');
            showError(error.responseJSON.message);
        }
    });
};

var cancelDoneAppointmentButton = document.getElementsByClassName('cancelDoneAppointmentButton');
for (var i = 0; i < cancelDoneAppointmentButton.length; i++) {
    cancelDoneAppointmentButton[i].onclick = function() {
        $('#doneAppointmentModal').modal('hide');
        eventModal.show();
    };
}