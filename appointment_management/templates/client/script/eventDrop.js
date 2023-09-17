let date = info.event.start;
let dateString = date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');
let currentDate = new Date();
currentDate.setHours(0, 0, 0, 0);

if (date < currentDate) {
    showError('Cannot rebook appointments to a date in the past.');
    info.revert();
    return;
}

let disabledDay = disabledDays.find(function(day) {
    return day.date === dateString;
});

if (disabledDay && disabledDay.timeOfTheDay === 'whole_day') {
    showError('This date is disabled for the whole day.');
    info.revert();
} else {
    // if (disabledDay) {
    //     if (disabledDay.timeOfTheDay === 'morning') {
    //         $('#id_timeOfTheDay-rebook option[value="morning"]').hide();
    //         $('#id_timeOfTheDay-rebook').val('afternoon');
    //     } else if (disabledDay.timeOfTheDay === 'afternoon') {
    //         $('#id_timeOfTheDay-rebook option[value="afternoon"]').hide();
    //         $('#id_timeOfTheDay-rebook').val('morning');
    //     }
    // } else {
    //     $('#id_timeOfTheDay-rebook option[value="morning"]').show();
    //     $('#id_timeOfTheDay-rebook option[value="afternoon"]').show();
    // }

    // Convert "Thu Sep 21 2023 00:00:00 GMT+0800 (Philippine Standard Time)" into 2023-09-21
    var oldDate = new Date(info.oldEvent.start);
    var oldDateString = oldDate.getFullYear() + '-' + (oldDate.getMonth() + 1).toString().padStart(2, '0') + '-' + oldDate.getDate().toString().padStart(2, '0');

    _appointmentCounts[oldDateString] = _appointmentCounts[oldDateString] - 1;

    $('#closeRebookConfirmationAppointmentModal').click(function() {
        _appointmentCounts[oldDateString] = _appointmentCounts[oldDateString] + 1;
        info.revert();
    });

    $('#closeIconRebookConfirmationAppointmentModal').click(function() {
        _appointmentCounts[oldDateString] = _appointmentCounts[oldDateString] + 1;
        info.revert();
    });

    $.ajax({
        type: 'GET',
        url: '{% url "check_if_full" %}',
        data: {
            'selected_date': dateString,
        },
        success: function(response) {
            if (response.status === 'full') {
                showError('This date is full.');
                info.revert();
            } else {

                $('#clientName-rebook').text(info.event.extendedProps.client);
                $('#oldDate').text(formatStringDate(info.event.extendedProps.current_date));
                $('#newDate').text(formatStringDate(dateString));
                $('#rebookConfirmAppointmentModal').modal('show');

                var start = info.event.start;
                var dateObj = new Date(start.getTime() - (start.getTimezoneOffset() * 60000));
                var date = dateObj.toISOString().slice(0, 10);

                window.info = info;
                window.eventId = info.event.id;
                window.oldDate = info.oldEvent.start;
                window.newDate = date;

                var clientId = info.event.extendedProps.client_id;
                var selectedPetId = info.event.extendedProps.pet_id;
                var select_pet = $("#id_pet-rebook");
                $.ajax({
                    url: "{% url 'client-get-pets' %}",
                    data: {
                        'client_id': clientId,
                        'selected_pet_id': selectedPetId
                    },
                    success: function(data) {
                        select_pet.html('');
                        $.each(data, function(index, text) {
                            select_pet.append(
                                $('<option></option>').val(text.id).html(text.name)
                            );
                        });
                        select_pet.val(selectedPetId);
                    }
                });

                var select_purpose = $("#id_purpose-rebook");
                select_purpose.val(info.event.extendedProps.purpose_id);

                //var select_timeOfDay = $("#id_timeOfTheDay-rebook");
                // select_timeOfDay.val(info.event.extendedProps.timeOfTheDay_val);
            }
        },
        error: function(error) {
            showError(error.responseJSON.message);
        }
    });
}