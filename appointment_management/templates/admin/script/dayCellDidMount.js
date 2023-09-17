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
//top margin
timeOfTheDayElement.style.marginTop = '5px';

var slotElement = document.createElement('div');
slotElement.style.position = 'absolute';
slotElement.style.left = '5px';
slotElement.style.top = '5px';
slotElement.style.fontSize = '0.8em';

var eventCountForDate = allAppointments.filter(function(event) {
    var _date = new Date(event.start);
    var _formattedDate = _date.getFullYear() + '-' + (_date.getMonth() + 1).toString().padStart(2, '0') + '-' + _date.getDate().toString().padStart(2, '0');
    return _formattedDate === formattedDate;
}).length;

var slots = dateSlots[formattedDate];
// console.log(dateSlots)
// console.log(formattedDate, slots)
if (slots === undefined) {
    slots = maxAppointments - eventCountForDate;
    slotElement.textContent = `${slots}/${maxAppointments}`;
} else {
    slots = slots - eventCountForDate;
    slotElement.textContent = `${slots}/${slots + eventCountForDate}`;
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