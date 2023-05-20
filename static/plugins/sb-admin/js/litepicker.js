// Litepicker
// 
// The date pickers in Material Admin Pro
// are powered by the Litepicker plugin.
// Litepicker is a lightweight, no dependencies
// date picker that allows for date ranges
// and other options. For more usage details
// visit the Litepicker docs.
// 
// Litepicker Documentation
// https://wakirin.github.io/Litepicker

window.addEventListener('DOMContentLoaded', event => {
    const urlParams = new URLSearchParams(window.location.search);
    const startDateString = urlParams.get('startDate');
    const endDateString = urlParams.get('endDate');

    const litepickerSingleDate = document.getElementById('litepickerSingleDate');
    if (litepickerSingleDate) {
        new Litepicker({
            element: litepickerSingleDate,
            format: 'MMM DD, YYYY'
        });
    }

    const litepickerDateRange = document.getElementById('litepickerDateRange');
    if (litepickerDateRange) {
        new Litepicker({
            element: litepickerDateRange,
            singleMode: false,
            format: 'MMM DD, YYYY'
        });
    }

    const litepickerDateRange2Months = document.getElementById('litepickerDateRange2Months');
    if (litepickerDateRange2Months) {
        new Litepicker({
            element: litepickerDateRange2Months,
            singleMode: false,
            numberOfMonths: 2,
            numberOfColumns: 2,
            format: 'MMM DD, YYYY'
        });
    }

    let currentYear = new Date().getFullYear();
    let today = new Date();
    let yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    let weekStart = new Date();
    if (weekStart.getDay() === 0) { // if today is Sunday
        weekStart.setDate(weekStart.getDate() - 6); // set to last Monday
    } else {
        weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1); // set to this Monday
    }

    let weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6); // set to Sunday

    let threeMonthsAgoStart = new Date();
    threeMonthsAgoStart.setMonth(threeMonthsAgoStart.getMonth() - 3);
    let threeMonthsAgoEnd = new Date();
    threeMonthsAgoEnd.setDate(threeMonthsAgoEnd.getDate() - 1);
    
    const litepickerRangePlugin = document.getElementById('litepickerRangePlugin');
    if (litepickerRangePlugin) {
        let picker = new Litepicker({
            element: litepickerRangePlugin,
            startDate: new Date(),
            endDate: new Date(),
            singleMode: false,
            numberOfMonths: 2,
            numberOfColumns: 2,
            format: 'MMM DD, YYYY',
            plugins: ['ranges'],
            ranges: {
                customRanges: {
                    'Today': [today, today],
                    'This Week': [weekStart, weekEnd],
                    'This Month': [new Date(currentYear, today.getMonth(), 1), new Date(currentYear, today.getMonth() + 1, 0)],
                    'This Year': [new Date(currentYear, 0, 1), new Date(currentYear, 11, 31)],
                }
            },
            setup: (picker) => {
                picker.on('selected', (date1, date2) => {
                    const newStartDate = date1.format('YYYY-MM-DD');
                    const newEndDate = date2.format('YYYY-MM-DD');

                    // Only update URL and reload page if the dates have changed
                    if (newStartDate !== startDateString || newEndDate !== endDateString) {
                        const url = new URL(window.location.href);
                        url.searchParams.set('startDate', newStartDate);
                        url.searchParams.set('endDate', newEndDate);
                        window.location.href = url;
                    }
                });
            }
        });
        
        if (startDateString && endDateString) {
            let startDate = new Date(startDateString);
            let endDate = new Date(endDateString);
            picker.setDateRange(startDate, endDate);
        }
        
    }
});

