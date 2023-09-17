let currentDate = new Date();
currentDate.setHours(0, 0, 0, 0);

let date = new Date(arg.dateStr + "T00:00:00");

if (date < currentDate) {
    showError('Cannot rebook appointments to a date in the past.');
    return;
}

let disabledDay = disabledDays.find(function(day) {
    return day.date === arg.dateStr;
});

if (disabledDay && disabledDay.timeOfTheDay === 'whole_day') {
    showError('This date is disabled for the whole day.');
} else {
    // if (disabledDay) {
    //     $('#id_time-rebook option').show();

    //     if (disabledDay.timeOfTheDay === 'morning') {
            
    //         $('#id_time-rebook option').each(function() {
    //             const timeValue = $(this).val();
    //             if (timeValue < "12:00:00") {
    //                 $(this).hide();
    //             }
    //         });
    //         $('#id_time-rebook').val('12:00:00');
    //     } else if (disabledDay.timeOfTheDay === 'afternoon') {
    //         $('#id_time-rebook option').each(function() {
    //             const timeValue = $(this).val();
    //             if (timeValue >= "12:00:00") {
    //                 $(this).hide();
    //             }
    //         });
    //         $('#id_time-rebook').val('07:30:00');
    //     }
    // } else {
    //     $('#id_time-rebook option').show();

    //     $('#id_time-rebook').val('07:30:00');
    // }

    $.ajax({
        type: 'GET',
        url: '{% url "check_if_full" %}',
        data: {
            'selected_date': arg.dateStr,
        },
        success: function(response) {
            if (response.status === 'full') {
                showError('This date is full.');
            } else {
                $('#clientName-rebook').text(arg.draggedEl.innerText);
                $('#oldDate').text("From Rebook List");
                $('#newDate').text(arg.dateStr);
                $('#rebookConfirmAppointmentModal').modal('show');

                window.eventId = arg.draggedEl.id;
                window.oldDate = "from_rebook_list";
                window.newDate = arg.dateStr;

                var clientId = arg.draggedEl.dataset.clientId;
                var petId = arg.draggedEl.dataset.petId;
                var purposeId = arg.draggedEl.dataset.purposeId;
                var timeOfDay = arg.draggedEl.dataset.timeOfDay;
                var url = "{% url 'get_pets' %}";

                $.ajax({
                    url: url,
                    data: {
                        'client_id': clientId
                    },
                    success: function(data) {
                        var select = $("#id_pet-rebook");
                        select.html('');
                        $.each(data, function(index, text) {
                            select.append(
                                $('<option></option>').val(text.id).html(text.name)
                            );
                        });
                        select.val(petId)
                    }
                });

                var select_purpose = $("#id_purpose-rebook");
                select_purpose.val(purposeId);

                //var select_timeOfDay = $("#id_timeOfTheDay-rebook");
                // select_timeOfDay.val(timeOfDay);
            }
        },
        error: function(error) {
            showError(error.responseJSON.message);
        }
    });
}