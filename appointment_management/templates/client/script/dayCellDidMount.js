var date = new Date(info.date);
var today = new Date();
today.setHours(0, 0, 0, 0);

var formattedDate = date.getFullYear() + '-' + (date.getMonth() + 1).toString().padStart(2, '0') + '-' + date.getDate().toString().padStart(2, '0');

var timeOfTheDayElement = document.createElement('div');
timeOfTheDayElement.style.position = 'absolute';
timeOfTheDayElement.style.left = '5px';
timeOfTheDayElement.style.bottom = '0px';
timeOfTheDayElement.style.fontSize = '0.8em';
timeOfTheDayElement.style.zIndex = '1';

var slotElement = document.createElement('div');
slotElement.style.position = 'absolute';
slotElement.style.left = '5px';
slotElement.style.top = '5px';
slotElement.style.fontSize = '0.8em';
slotElement.classList.add('slot-element');

var totalEventCountForDate = _appointmentCounts[formattedDate] || 0;

var slots = dateSlots[formattedDate];

if (slots === undefined) {
    slots = maxAppointments - totalEventCountForDate;
    var plural = slots > 1 ? 's' : '';
    slotElement.textContent = `${slots} slot${plural} left`;
} else {
    var plural = slots > 1 ? 's' : '';
    slotElement.textContent = `${slots - totalEventCountForDate} slot${plural} left`;
}

if (info.el.classList.contains('day-disabled-whole-day')) {
    timeOfTheDayElement.textContent = `Disabled`;
} else if (info.el.classList.contains('day-disabled-morning')) {
    timeOfTheDayElement.textContent = `Afternoon Available`;
} else if (info.el.classList.contains('day-disabled-afternoon')) {
    timeOfTheDayElement.textContent = `Morning Available`;
} else if (info.el.classList.contains('day-full')) {
    timeOfTheDayElement.textContent = `Full`;
}

if (date < today) {
    slotElement.textContent = ``;
}

slotElements[formattedDate] = slotElement;
timeOfTheDayElements[formattedDate] = timeOfTheDayElement;
timeOfDayInfo[formattedDate] = info;

info.el.querySelector('.fc-daygrid-day-top').appendChild(slotElement);
info.el.querySelector('.fc-daygrid-day-top').appendChild(timeOfTheDayElement);