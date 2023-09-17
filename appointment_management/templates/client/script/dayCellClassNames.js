debugCounter++;
const eventCounts = getEventCounts(calendar.getEvents());
const date = FullCalendar.formatDate(info.date, {
    timeZone: 'local',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
});

const parts = date.split('/');
const formattedDate = `${parts[2]}-${parts[0]}-${parts[1]}`;

let timeOfDay = null;
let disableDayObject = disabledDays.find(obj => obj.date == formattedDate);
if (disableDayObject) {
    timeOfDay = disableDayObject.timeOfTheDay;
}

let slots = dateSlots[formattedDate];

if (slots === undefined) {
    slots = maxAppointments;
}

if(timeOfDay === "whole_day")
{
    slots += 1;
}

let totalEventCountForDate = _appointmentCounts[formattedDate] || 0;
//console.log(totalEventCountForDate, formattedDate, slots, eventCounts[date])

if (totalEventCountForDate === slots || eventCounts[date] === slots || slots === 0) {
    return ['day-full'];
} else if (timeOfDay) {
    if (timeOfDay === "morning") {
        return ['day-disabled-morning'];
    } else if (timeOfDay === "afternoon") {
        return ['day-disabled-afternoon'];
    } else if (timeOfDay === "whole_day") {
        return ['day-disabled-whole-day'];
    }
} else {
    return ['day-available'];
}