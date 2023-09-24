$("#closeRebookConfirmationAppointmentModal").off("click");
$("#closeIconRebookConfirmationAppointmentModal").off("click");

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

let appointmentsForDate = allAppointments.filter(function(appointment) {
    var _date = new Date(appointment.start);
    var _formattedDate = _date.getFullYear() + '-' + (_date.getMonth() + 1).toString().padStart(2, '0') + '-' + _date.getDate().toString().padStart(2, '0');
    return _formattedDate === dateString;
}).length;

let availableSlots = dateSlots[dateString] != undefined ?
    (dateSlots[dateString] - appointmentsForDate) :
    (maxAppointments - appointmentsForDate);

if (disabledDay && disabledDay.timeOfTheDay === 'whole_day') {
    showError('This date is disabled for the whole day.');
    info.revert();
    return;
} 

if (availableSlots <= 0) {
    showError('This date is full.');
    info.revert();
    return;
}

$('#closeRebookConfirmationAppointmentModal').click(function() {
    info.revert();
});

$('#closeIconRebookConfirmationAppointmentModal').click(function() {
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
        } 
        else {
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
            var select_pet = $("#id_pet-rebook");


            $.ajax({
                url: "{% url 'get_pets' %}",
                data: {
                    'client_id': clientId
                },
                success: function(data) {

                    select_pet.html('');
                    $.each(data, function(index, text) {
                        select_pet.append(
                            $('<option></option>').val(text.id).html(text.name)
                        );
                    });
                    select_pet.val(info.event.extendedProps.pet_id);
                }
            });

            var select_purpose = $("#id_purpose-rebook");
            select_purpose.val(info.event.extendedProps.purpose_id);
            //var select_pet = $("#id_pet-rebook");
            //select_pet.val(info.event.extendedProps.pet_id);

            //var select_timeOfDay = $("#id_timeOfTheDay-rebook");
            // select_timeOfDay.val(info.event.extendedProps.timeOfTheDay_val);
        }
    },
    error: function(error) {
        showError(error.responseJSON.message);
    }
});
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
// } 
// else
// {
//     $('#id_time-rebook option').show();
//     $('#id_time-rebook').val('07:30:00');
// }
