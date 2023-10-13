let date = arg.start;
window.selectedDate = date;
let dateString = date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');

let calendarApi = arg.view.calendar;

let eventsOnSelectedDay = calendarApi.getEvents().filter(event => {
    return event.extendedProps.current_date === dateString;
});

window.eventsOnSelectedDay = eventsOnSelectedDay;

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

let morningAppointmentsForDate = allAppointments.filter(function(appointment) {
    let _date = new Date(appointment.start);
    let _formattedDate = _date.getFullYear() + '-' + (_date.getMonth() + 1).toString().padStart(2, '0') + '-' + _date.getDate().toString().padStart(2, '0');
    return _formattedDate === dateString && appointment.extendedProps.timeOfTheDay_val === "morning";
}).length;

let afternoonAppointmentsForDate = allAppointments.filter(function(appointment) {
    let _date = new Date(appointment.start);
    let _formattedDate = _date.getFullYear() + '-' + (_date.getMonth() + 1).toString().padStart(2, '0') + '-' + _date.getDate().toString().padStart(2, '0');
    return _formattedDate === dateString && appointment.extendedProps.timeOfTheDay_val === "afternoon";
}).length;

let morningSlots = maxAppointments / 2;
let afternoonSlots = maxAppointments / 2;

for(let i = 0; i < response.date_slots.length; i++) {
    if(response.date_slots[i].date == dateString) {
        morningSlots = response.date_slots[i].morning_slots;
        afternoonSlots = response.date_slots[i].afternoon_slots;
    }
}

let availableMorningSlots = morningSlots - morningAppointmentsForDate;
let availableAfternoonSlots = afternoonSlots - afternoonAppointmentsForDate;

$('.morning-slots').text(availableMorningSlots + " / " + morningSlots);
$('.afternoon-slots').text(availableAfternoonSlots + " / " + afternoonSlots);

if (availableSlots <= 0) {
    $('#add-appointment-day-choice').prop('disabled', true);
    $('#disable-day-choice').prop('disabled', true);
    $('#enable-day-choice').prop('disabled', true);
    $('#adjust-slot-choice').prop('disabled', true);
} else {
    $('#add-appointment-day-choice').prop('disabled', false);
    $('#disable-day-choice').prop('disabled', false);
    $('#enable-day-choice').prop('disabled', false);
    $('#adjust-slot-choice').prop('disabled', false);
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
            // $('#id_timeOfTheDay option[value="morning"]').hide();
            // $('#id_timeOfTheDay').val('afternoon');
            $('.morning-slots').text(0 + " / " + morningSlots);
        } else if (disabledDay.timeOfTheDay === 'afternoon') {
            $('.availability').text("Morning");
            // $('#id_timeOfTheDay option[value="afternoon"]').hide();
            // $('#id_timeOfTheDay').val('morning');
            $('.afternoon-slots').text(0 + " / " + afternoonSlots);
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