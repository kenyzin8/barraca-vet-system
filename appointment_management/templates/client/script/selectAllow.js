var dayBeforeEndDate = new Date(selectInfo.end);
dayBeforeEndDate.setDate(dayBeforeEndDate.getDate() - 1);
return FullCalendar.formatDate(selectInfo.start, {
    timeZone: 'local',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
}) === FullCalendar.formatDate(dayBeforeEndDate, {
    timeZone: 'local',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
});