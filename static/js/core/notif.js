function formatDate(dateString) 
{
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };
    return new Date(dateString).toLocaleString('en-US', options);
}

function timeAgo(dateString) 
{
    var now = new Date();
    var past = new Date(dateString);
    
    var secondsAgo = Math.round((now - past) / 1000);
    var minutesAgo = Math.floor(secondsAgo / 60);
    var hoursAgo = Math.floor(minutesAgo / 60);
    
    if (secondsAgo < 60) {
        return "Just now";
    } else if (minutesAgo < 60) {
        return minutesAgo + " minutes ago";
    } else if (hoursAgo < 1) {
        return hoursAgo + " hours ago";
    } else {
        return formatDate(dateString);
    }
}

function updateNotifications() 
{
    $.get('/admin/inventory/get-notifications/', function(data) {
        $('.indicator').text(data.length);

        var notificationsContainer = $('.dropdown-notifications .dropdown-menu');

        notificationsContainer.empty();

        var header = '<h6 class="dropdown-header dropdown-notifications-header"><i class="me-2" data-feather="bell"></i>Alerts Center</h6>';
        notificationsContainer.append(header);

        console.log(data);

        $.each(data, function(i, notification) {
            var timeAgoText = timeAgo(notification.date_created);
            var link = "/admin/inventory/";
        
            if(notification.notification_type == 'critical') {
                link = "/admin/inventory/reorder-list";
            }

            console.log(link);
        
            var item = '<a class="dropdown-item dropdown-notifications-item" href="' + link + '">' +
                '<div class="dropdown-notifications-item-icon bg-danger"><i data-feather="alert-circle"></i></div>' +
                '<div class="dropdown-notifications-item-content">' +
                '<div class="dropdown-notifications-item-content-details">' + timeAgoText + '</div>' +
                '<div class="dropdown-notifications-item-content-text">' + notification.text + '</div>' +
                '</div></a>';
            notificationsContainer.append(item);
        });
        

        var footer = '<a class="dropdown-item dropdown-notifications-footer" href="#!">View All Alerts</a>';
        notificationsContainer.append(footer);

        feather.replace();
    });
}

updateNotifications();

// setInterval(updateNotifications, 10000);