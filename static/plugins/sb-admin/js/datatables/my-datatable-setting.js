
window.addEventListener('DOMContentLoaded', event => {
    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        let dataTable = new simpleDatatables.DataTable(datatablesSimple, {
            paging: true,
            perPageSelect: [5, 10, 25, 50],
            perPage: 10,
            fixedHeight: true,
            sortable: true,
            searchable: true,
            hiddenHeader: false,
        });

        dataTable.on('datatable.update', () => {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        dataTable.on('datatable.page', function(page) {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        dataTable.on('datatable.search', function(query, matched) {
            feather.replace();

            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        dataTable.on('datatable.sort', function(column, direction) {
            feather.replace();
            
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            })
        });

        var searchInput = document.querySelector('.datatable-input');
        
        searchInput.addEventListener('search', function(e) {
            if (e.target.value == '') {
                dataTable.search('');
            }
        });
    }
});