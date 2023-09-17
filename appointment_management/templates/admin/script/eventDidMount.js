var event = info.event;
var extendedProps = event.extendedProps;

var time = event.start.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    meridiem: 'long'
});

var tooltipContent = `
    ID: ${event.id}<br>
    Time: ${time}<br>
    Client: ${extendedProps.client}<br>
    Pet: ${extendedProps.pet}<br>
    Purpose: ${extendedProps.purpose ? extendedProps.purpose : 'N/A'}
`;

info.el.setAttribute('data-bs-toggle', 'tooltip');
info.el.setAttribute('data-bs-placement', 'left');
info.el.setAttribute('data-bs-html', 'true');
info.el.setAttribute('title', tooltipContent);