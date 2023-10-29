$.ajax({
    type: 'GET',
    url: '{% url "is_all_my_pets_scheduled" %}',
    dataType: 'json',
    success: function(_response) {
        if (_response.all_scheduled) {
            showError("All of your pets are scheduled, please cancel one of your appointment. You can only have one appointment per pet at a time unless the clinic staff will set an appointment for you. If you don't see your appointment on the calendar, please refresh the page.");
        } else {
            let date = arg.start;
            let dateString = date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');

            $('.day-clicked').text(formatStringDate(dateString));

            let totalAppointmentsForDate = _appointmentCounts[dateString] || 0;

            let availableSlots = dateSlots[dateString] == undefined ?
                (maxAppointments - totalAppointmentsForDate) :
                (dateSlots[dateString] - totalAppointmentsForDate);

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
            
            var morning_count = response.morning_appointment_counts[dateString] ? response.morning_appointment_counts[dateString] : 0;
            var afternoon_count = response.afternoon_appointment_counts[dateString] ? response.afternoon_appointment_counts[dateString] : 0;
            let availableMorningSlots = (morningSlots - morningAppointmentsForDate) - morning_count;
            let availableAfternoonSlots = (afternoonSlots - afternoonAppointmentsForDate) - afternoon_count;

            $('.morning-slots').text(availableMorningSlots + " / " + morningSlots);
            $('.afternoon-slots').text(availableAfternoonSlots + " / " + afternoonSlots);

            if (availableSlots <= 0) {
                $('#add-appointment-day-choice').prop('disabled', true);
            } else {
                $('#add-appointment-day-choice').prop('disabled', false);
            }

            if (_appointmentCounts[dateString] && _appointmentCounts[dateString] >= 8) {
                showError(`${formatStringDate(dateString)} is fully booked. Try another day.`);
                return;
            }

            window.selectedDate = date;

            $('.day-clicked').text(formatStringDate(dateString));

            let disabledDay = disabledDays.find(function(day) {
                return day.date === dateString;
            });

            if (disabledDay) {
                $('#selectedDateToEnable').val(dateString);
                if (disabledDay.timeOfTheDay === 'whole_day') {
                    showError(`You cannot set an appointment on this day. <br><br><span class="fw-700 text-danger">Reason: ${disabledDay.reason}</span>.`);
                } else if (availableSlots <= 0) {
                    showError("This date is full, please select another date.");
                } else {
                    if (disabledDay.timeOfTheDay === 'morning') {
                        $('.availability').text("Afternoon");
                        $('#id_timeOfTheDay option[value="morning"]').hide();
                        $('#id_timeOfTheDay').val('afternoon');
                        $('.morning-slots').text(0 + " / " + morningSlots);
                    } else if (disabledDay.timeOfTheDay === 'afternoon') {
                        $('.availability').text("Morning");
                        $('#id_timeOfTheDay option[value="afternoon"]').hide();
                        $('#id_timeOfTheDay').val('morning');
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
        }
    },
    error: function(response) {
        showError(response);
    }
});