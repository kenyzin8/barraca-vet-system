function getEventCounts(events) {
  const eventCounts = {};

  events.forEach(event => {
    const date = FullCalendar.formatDate(event.start, { timeZone: 'local', year: 'numeric', month: '2-digit', day: '2-digit' });
    eventCounts[date] = (eventCounts[date] || 0) + 1;
  });

  return eventCounts;
}

function getInitialView() {
  return window.innerWidth <= 576 ? 'listYear' : 'dayGridMonth';
}

document.addEventListener('DOMContentLoaded', function() 
{
  var calendarEl = document.getElementById('calendar');
  var containerEl = document.getElementById('external-events-list');
  new FullCalendar.Draggable(containerEl, {
    itemSelector: '.fc-event',
    eventData: function(eventEl) {
      return {
        title: eventEl.innerText.trim()
      }
    }
  });
  
  var calendar = new FullCalendar.Calendar(calendarEl, 
  {
    themeSystem: 'bootstrap5',
    lazyFetching: true,
    progressiveEventRendering: true,
    views: {
      listDay: { buttonText: 'Day' },
      dayGridMonth: { buttonText: 'Month' },
      multiMonthYear: { buttonText: 'Year' },
      listYear: { buttonText: 'All'},
      listMonth: {buttonText: 'Month'}
    },
    buttonText: {
      today: 'Today',
    },
    allDayText: '',
    firstDay: 1,
    noEventsText: 'No appointments to show',
    initialDate: getCurrentDateString(),
    initialView: getInitialView(),
    navLinks: true, // can click day/week names to navigate views
    selectable: true,
    selectMirror: true,
    editable: true,
    droppable: true,
    dayMaxEvents: true, // allow "more" link when too many events
    hiddenDays: [ 0 ],
    select: function(arg) 
    {
      var title = prompt('Create Appointment:');
      if (title) 
      {
        calendar.addEvent(
          {
            title: title,
            start: arg.start,
            end: arg.end,
            allDay: arg.allDay
          })
      }

      calendar.unselect()
    },
    eventClick: function(arg) 
    {
      var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
      const dateString = arg.event.start;
      const date = new Date(dateString);
      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const day = monthNames[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear();
      
      document.getElementById('eventModalLabel').innerText = day;
      document.getElementById('eventModalBody').innerText = arg.event.title;
      eventModal.show();
    
      // Hide the popover right after showing the modal
      var popover = document.querySelector('.fc-popover');
      if (popover) {
        popover.style.display = 'none';
      }
    
      document.getElementById('deleteEvent').onclick = function() {
        arg.event.remove();
        eventModal.hide();
      };
    },
    events: [
      {
        title: 'Kent Jamila',
        start: '2023-07-11'
      },
      {
        title: 'John Jamila',
        start: '2023-07-11'
      },
      {
        title: 'Susie Jamila',
        start: '2023-07-11'
      },
      {
        title: 'Kharyl Caye Domalogdog',
        start: '2023-07-11'
      },
      {
        title: 'Kotlin Molk',
        start: '2023-07-11'
      },
      {
        title: 'Simon Walker',
        start: '2023-07-11'
      },
      {
        title: 'Yvette Mae Barraca',
        start: '2023-07-11'
      },
      {
        title: 'Erika Mae Barraca',
        start: '2023-07-11'
      },
      {
        title: 'Kent John Jin',
        start: '2023-07-15',
        // display: 'background',
        // color: "red"
      }
    ],
    dayCellClassNames: function (info) 
    {    
      const eventCounts = getEventCounts(calendar.getEvents());
      const date = FullCalendar.formatDate(info.date, { timeZone: 'local', year: 'numeric', month: '2-digit', day: '2-digit' });
      if (eventCounts[date] === 8) 
      {
        return ['day-full'];
      } 
      else 
      {
        return ['day-available'];
      }
    },
    navLinkDayClick: function(date, jsEvent) {
      alert('day clicked ' + date.toISOString());
      jsEvent.preventDefault();
    },
    selectAllow: function(selectInfo) {
      var dayBeforeEndDate = new Date(selectInfo.end);
      dayBeforeEndDate.setDate(dayBeforeEndDate.getDate() - 1);
      return FullCalendar.formatDate(selectInfo.start, { timeZone: 'local', year: 'numeric', month: '2-digit', day: '2-digit' }) === FullCalendar.formatDate(dayBeforeEndDate, { timeZone: 'local', year: 'numeric', month: '2-digit', day: '2-digit' });
    },
    eventDrop: function(info) {
      if (!confirm("Are you sure you want to rebook this client?")) {
        info.revert();
      }
    },
    drop: function(arg) {
      if (!confirm("Are you sure you want to rebook this client?")) {
        arg.revert();
      }
      else
      {
        arg.draggedEl.parentNode.removeChild(arg.draggedEl);
      }
    },
  });

  calendar.render();

  function updateCalendarOptions() {
    if (window.innerWidth <= 576) {
      calendar.setOption('headerToolbar', {
        left: 'title',
        center: 'listMonth,listYear',
        right: 'today prev,next'
      });
      
    } else {
      calendar.setOption('headerToolbar', {
        left: 'today prev,next',
        center: 'title',
        right: 'listDay,dayGridMonth,multiMonthYear,listYear'
      });
    }
  }  

  updateCalendarOptions();

  function getCurrentDateString() {
    const currentDate = new Date();
    const year = currentDate.getFullYear();
    const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed, so add 1
    const day = String(currentDate.getDate()).padStart(2, '0');
  
    return `${year}-${month}-${day}`;
  }
});    