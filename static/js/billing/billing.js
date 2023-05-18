$(document).ready(function() {
    var total = 0;
    var clientInput = $('.selected-client-input');
    var findClientButton = $('.find-client-button');

    if(clientInput.val().trim() != '') {
        clientInput.prop('disabled', true);
        findClientButton.css('display', 'none');
    }

    $('.add-client').on('click', function() 
    {
        var clientId = $(this).data('client-id');
        var clientName = $(this).siblings('.client-value').text();
    
        $('.selected-client-input').val(clientName);
        $('.selected-client-input').addClass('selected-client');
        $('.selected-client-input').data('client-id', clientId);

        $('#addClientModal').modal('hide');
    });

    // Add service
    $('.add-service').on('click', function() {
        var serviceId = $(this).data('service-id');
        var serviceName = $(this).siblings('.service-type').text();
        var serviceFee = $(this).siblings('.service-fee').text();

        serviceFee = serviceFee.replace("₱", "").trim();

        total += parseFloat(serviceFee.replace("₱", "").trim());

        var newRow = `
            <tr class="selected-service" data-service-id="${serviceId}">
                <td>
                    <div class="fw-bold">
                        ${serviceName}
                        <a class="btn btn-datatable btn-icon btn-transparent-dark remove-service" href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="Remove">
                            <i data-feather="delete"></i>
                        </a>
                    </div>
                    <div class="small text-muted d-none d-md-block">Without Medicine</div>
                </td>
                <td class="text-end fw-bold"><!-- empty for spacing --></td>
                <td class="text-end fw-bold"><!-- empty for spacing --></td>
                <td class="text-end fw-bold service-fee">₱ ${parseFloat(serviceFee).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
            </tr>
        `;

        $('.tbody-services').append(newRow);
        $('#addServiceModal').modal('hide');

        $('.total-amount').text('Total Amount: ₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));

        feather.replace();
    });

    // Add product
    $('.add-product').on('click', function() {
        var productId = $(this).data('product-id');
        var productName = $(this).siblings('.product-name').text();
        var productPrice = $(this).siblings('.product-price').text();
        var quantity = $(this).siblings('.product-quantity').val();

        productPrice = productPrice.replace("₱", "").trim();
        productPrice = parseFloat(productPrice.replace("₱", "").trim());

        total += productPrice * parseInt(quantity);

        var newRow = `
            <tr class="selected-product" data-product-id="${productId}" data-product-quantity="${quantity}">
                <td>
                    <div class="fw-bold">
                        ${productName} x <span class="product-quantity">${quantity}</span>
                        <a class="btn btn-datatable btn-icon btn-transparent-dark remove-product" href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="Remove">
                            <i data-feather="delete"></i>
                        </a>
                    </div>
                    <div class="small text-muted d-none d-md-block">Without Medicine</div>
                </td>
                <td class="text-end fw-bold"><!-- empty for spacing --></td>
                <td class="text-end fw-bold"><!-- empty for spacing --></td>
                <td class="text-end fw-bold product-price">₱ ${parseFloat(productPrice).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) * parseInt(quantity)}</td>
            </tr>
        `;

        $('#total-row').before(newRow);
        $('#addProductModal').modal('hide');

        $('.total-amount').text('Total Amount: ₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));

        feather.replace();
    });

    $(document).on('click', '.remove-service', function(e) {
        e.preventDefault();

        var serviceFee = $(this).parents('tr').find('.service-fee').text();
        serviceFee = serviceFee.replace("₱", "").trim();
        serviceFee = serviceFee.replace(/,/g, "").trim();
        
        total -= parseFloat(serviceFee.replace("₱", "").trim());
        
        $('.total-amount').text('Total Amount: ₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));

        $(this).closest('tr').remove();
    });

    $(document).on('click', '.remove-product', function(e) {
        e.preventDefault();

        var productPrice = $(this).parents('tr').find('.product-price').text();
        productPrice = productPrice.replace("₱", "").trim();
        productPrice = productPrice.replace(/,/g, "").trim();

        total -= parseFloat(productPrice.replace("₱", "").trim());

        $('.total-amount').text('₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
        
        $(this).closest('tr').remove();
    });
});

$('#paid-button').on('click', function() {
    var clientId = $('.selected-client-input').data('client-id');
    var serviceIds = [];
    var productIds = [];

    $('.selected-service').each(function() {
        serviceIds.push($(this).data('service-id'));
    });

    $('.selected-product').each(function() {
        productIds.push($(this).data('product-id'));
    });

    if(!clientId)
    {
        $('#errorModal .modal-body').text("Client is not selected.");
        $('#errorModal').modal('show');
        return;
    }

    if(serviceIds.length == 0 && productIds.length == 0) {
        $('#errorModal .modal-body').text("At least one service or product should be added.");
        $('#errorModal').modal('show');
        return;
    }

    $('#confirmationModal').modal('show');
});

$('#confirm-paid-button').on('click', function() {
    var clientId = $('.selected-client-input').data('client-id');
    var serviceIds = [];
    var productIds = [];
    var quantities = [];

    $('.selected-service').each(function() {
        serviceIds.push($(this).data('service-id'));
    });

    $('.selected-product').each(function() {
        productIds.push($(this).data('product-id'));
        quantities.push($(this).data('product-quantity'));
    });

    $.ajax({
        url: '/admin/bill/post/',
        method: 'POST',
        data: {
            'client_id': clientId,
            'service_ids': serviceIds,
            'product_ids': productIds,
            'quantities': quantities,
        },
        dataType: 'json',
        success: function(data) {
            $('#addBillSuccess').modal('show');
        }
    });
});

$(document).ready(function() {
    function formatBillId(billId) 
    {
        let billIdStr = String(billId);
        while (billIdStr.length < 6) {
            billIdStr = '0' + billIdStr;
        }
        billIdStr = billIdStr.slice(0, 3) + '-' + billIdStr.slice(3);
        return billIdStr;
    }

    let billId = $('.billing-number').text();
    let billIdModal = $('.billing-number-modal').text();

    let formattedBillId = formatBillId(billId);
    let formattedBillIdModal = formatBillId(billIdModal);

    $('.billing-number').text(formattedBillId);
    $('.billing-number-modal').text(formattedBillIdModal);
});

$('#success-add-billing').on('click', function() {
    window.location.href = "/admin/bill/";
});
