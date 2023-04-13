
  function getEventCounts(events) {
    const eventCounts = {};

    events.forEach(event => {
      const date = FullCalendar.formatDate(event.start, { timeZone: 'local', year: 'numeric', month: '2-digit', day: '2-digit' });
      eventCounts[date] = (eventCounts[date] || 0) + 1;
    });

    return eventCounts;
  }
  
  function getInitialView() {
    return window.innerWidth <= 576 ? 'listMonth' : 'dayGridMonth';
  }

  document.addEventListener('DOMContentLoaded', function() 
  {
    var calendarEl = document.getElementById('calendar');
  
    var calendar = new FullCalendar.Calendar(calendarEl, 
    {
      themeSystem: 'bootstrap5',
      views: {
        listDay: { buttonText: 'Day' },
        dayGridMonth: { buttonText: 'Month' },
        listYear: { buttonText: 'Year' },
        listMonth: { buttonText: 'All'},
      },
      buttonText: {
            today: 'Today',
      },
      allDayText: '',
      firstDay: 1,
      noEventsText: 'No appointments for this day',
      initialDate: '2023-04-12',
      initialView: getInitialView(),
      navLinks: true, // can click day/week names to navigate views
      selectable: true,
      selectMirror: true,
      select: function(arg) 
      {
        var title = prompt('Event Title:');
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
      
        document.getElementById('deleteEvent').onclick = function() {
          arg.event.remove();
          eventModal.hide();
        };
      },
      editable: false,
      dayMaxEvents: true, // allow "more" link when too many events
      events: [
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-11'
        },
        {
          title: 'Kent Jamila',
          start: '2023-04-15',
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
      }
    });

    calendar.render();

    function updateCalendarOptions() {
      if (window.innerWidth <= 576) {
        calendar.setOption('initialView', 'listMonth');
        calendar.setOption('headerToolbar', {
          left: 'title',
          center: 'listDay,listYear,listMonth',
          right: 'today prev,next'
        });
        
      } else {
        calendar.setOption('initialView', 'dayGridMonth');
        calendar.setOption('headerToolbar', {
          left: 'today prev,next',
          center: 'title',
          right: 'listDay,dayGridMonth,listYear,listMonth'
        });
      }
    }  

    updateCalendarOptions();
  });    
