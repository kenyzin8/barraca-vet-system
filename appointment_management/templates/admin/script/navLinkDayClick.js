jsEvent.preventDefault();

if (window.innerWidth <= 576) {
    window.selectedDate = date;
    let dateString = date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');

    $('.day-clicked').text(formatStringDate(dateString));

    let appointmentsForDate = allAppointments.filter(function(appointment) {
        var _date = new Date(appointment.start);
        var _formattedDate = _date.getFullYear() + '-' + (_date.getMonth() + 1).toString().padStart(2, '0') + '-' + _date.getDate().toString().padStart(2, '0');
        return _formattedDate === dateString;
    }).length;

    let availableSlots = dateSlots[dateString] != undefined ?
        (dateSlots[dateString] - appointmentsForDate) :
        (maxAppointments - appointmentsForDate);

    $('.available-slots').text(availableSlots + " / " + (dateSlots[dateString] || maxAppointments));

    if (availableSlots <= 0) {
        $('#add-appointment-day-choice').prop('disabled', true);
        $('#disable-day-choice').prop('disabled', true);
    } else {
        $('#add-appointment-day-choice').prop('disabled', false);
        $('#disable-day-choice').prop('disabled', false);
    }

    // $('.slots').text(dateSlots[dateString] == undefined ? maxAppointments : dateSlots[dateString]);

    let disabledDay = disabledDays.find(function(day) {
        return day.date === dateString;
    });

    if (disabledDay) {
        $('#selectedDateToEnable').val(dateString);
        if (disabledDay.timeOfTheDay === 'whole_day') {
            $('#enableDayModal').modal('show');
        } else {
            if (disabledDay.timeOfTheDay === 'morning') {
                $('.availability').text("Afternoon");
                $('#id_timeOfTheDay option[value="morning"]').hide();
                $('#id_timeOfTheDay').val('afternoon');
            } else if (disabledDay.timeOfTheDay === 'afternoon') {
                $('.availability').text("Morning");
                $('#id_timeOfTheDay option[value="afternoon"]').hide();
                $('#id_timeOfTheDay').val('morning');
            }
            $('#enable-day-choice').removeAttr('hidden');
            $('#disable-day-choice').attr('hidden', true);
            $('#dayChoiceModal').modal('show');
        }
    } else {
        $('.availability').text("Whole Day");
        $('.day-clicked').text(formatStringDate(dateString));
        $('#disable-day-choice').removeAttr('hidden');
        $('#enable-day-choice').attr('hidden', true);

        let currentDate = new Date();
        currentDate.setHours(0, 0, 0, 0);

        if (date < currentDate) {
            showError('Cannot add appointments in the past.');
            return;
        }

        $('#dayChoiceModal').modal('show');
    }
    return;
}

var events = calendar.getEvents();
var dateStr = date.getFullYear() + '-' + 
                ('0' + (date.getMonth()+1)).slice(-2) + '-' + 
                ('0' + date.getDate()).slice(-2);

var eventsOnDate = events.filter(function(event) {
    var _event = event.start.getFullYear() + '-' + 
        ('0' + (event.start.getMonth()+1)).slice(-2) + '-' + 
        ('0' + event.start.getDate()).slice(-2);
    return _event === dateStr;
});

if (eventsOnDate.length === 0) {
    return;
}

$(".appointment-table-title").text(formatDates(date) + ' | Appointments');
$(".appointment-table").removeAttr("hidden");

dataTable.rows.remove([0, 1, 2, 3, 4, 5, 6, 7])

eventsOnDate.forEach(function(event, index) {
    var row = [
        event.id,
        event.extendedProps.client,
        event.extendedProps.pet,
        event.extendedProps.contact_number,
        event.extendedProps.day_sms_reminder == false ? '<span class="badge bg-warning">Pending</span>' : '<span class="badge bg-success">Sent</span>',
        event.extendedProps.week_sms_reminder == false ? '<span class="badge bg-warning">Pending</span>' : '<span class="badge bg-success">Sent</span>',
        "<button type='button' class='btn btn-primary btn-sm lift lift-sm' onclick='confirmSendSMS(\"" +
        event.id + "\", \"" +
        event.extendedProps.client + "\", \"" +
        event.extendedProps.contact_number + "\"" +
        ")'>Notify</button>"
    ];
    dataTable.rows.add(row);
});

calendar.changeView('listDay', date);

$('html, body').animate({
    scrollTop: $(".appointments-list-table").offset().top
}, 800);