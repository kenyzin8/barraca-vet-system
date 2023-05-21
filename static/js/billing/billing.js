$(document).ready(function() {
    var total = 0;
    var clientInput = $('.selected-client-input');
    var findClientButton = $('.find-client-button');
    var selectedServiceIds = new Set();
    var selectedProductIds = new Set();
    var quantityOnStockSelected = 0;

    // $('#addServiceBtn').hide();

    if(clientInput.val().trim() != '') {
        clientInput.prop('disabled', true);
        findClientButton.css('display', 'none');
    }

    $(document).on('click', '.add-client', function() {
        var clientId = $(this).data('client-id');
        var clientName = $(this).closest('tr').find('.client-value').text();
    
        $('.selected-client-input').val(clientName);
        $('.selected-client-input').addClass('selected-client');
        $('.selected-client-input').data('client-id', clientId);
    
        // Disable the input and show the anchor tag
        $('.selected-client-input').prop('disabled', true);
        $('.remove-client').show();
        // $('#addServiceBtn').show(); // Show the "Add Service" button
    
        $('#addClientModal').modal('hide');
    });
    
    $(document).on('click', '.remove-client', function(e) {
        e.preventDefault();
    
        // Clear the input, enable it, hide the anchor tag, and remove selected-client class
        $('.selected-client-input').val('');
        $('.selected-client-input').prop('disabled', false);
        $('.selected-client-input').removeClass('selected-client');
        $('.selected-client-input').removeData('client-id');
        $('.remove-client').hide();
        // $('#addServiceBtn').hide(); // Hide the "Add Service" button
    });

    // Add service
    $(document).on('click', '.add-service', function() { 
        var serviceId = $(this).data('service-id');

        if (selectedServiceIds.has(serviceId)) {
            $(this).prop('disabled', true);
            return;
        }

        var row = $(this).closest('tr');
        var serviceName = row.find('.service-type').text();
        var serviceFee = row.find('.service-fee').text();
        var serviceRemarks = row.find('.service-remarks').text();

        selectedServiceIds.add(serviceId);

        $(this).prop('disabled', true);

        serviceFee = serviceFee.replace("₱", "").trim();
        serviceFee = serviceFee.replace(/,/g, "").trim();

        total += parseFloat(serviceFee);

        var newRow = `
            <tr class="selected-service" data-service-id="${serviceId}">
                <td>
                    <div class="fw-bold">
                        ${serviceName}
                        <a class="btn btn-datatable btn-icon btn-transparent-dark remove-service" href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="Remove">
                            <i data-feather="delete"></i>
                        </a>
                    </div>
                    <div class="small text-muted d-none d-md-block">${serviceRemarks}</div>
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
    $(document).on('click', '.add-product', function() { 
        var $this = $(this);

        var productId = $(this).data('product-id');
    
        if (selectedProductIds.has(productId)) {
            $this.prop('disabled', true);
            return;
        }
    
        var row = $(this).closest('tr');
        var productName = row.find('.product-name').text();
        var productPrice = row.find('.product-price').text();
        var productType = row.find('.product-type').text();
        var quantityInput = row.find('.product-quantity');
        var quantity = quantityInput.val();
    
        var stockQuantity = row.find('.product-stock-quantity').text();
        stockQuantity = parseFloat(stockQuantity.replace(/,/g, ""));

        if((quantity.split('.')[1] || []).length > 2)
         {
            $('#errorModal .modal-body').text("Only 2 decimal points for the quantity.");
            $('#errorModal').modal('show');
            quantityInput.focus();
            return;
        }

        $.ajax({
            url: '/admin/inventory/check-expiry/' + productId + '/',
            method: 'GET',
            success: function(data) {
                var stockExpiry = data.expiry;
                
                if(stockExpiry != null) {
                    var stockExpiryDate = new Date(stockExpiry);
                    var today = new Date();

                    if(stockExpiryDate < today) {
                        $('#errorModal .modal-body').html("The product is already expired. <a href='/admin/inventory/'>Click here</a> to view the list of product.");
                        $('#errorModal').modal('show');
                        quantityInput.focus();
                        return;
                    }
                }
            }
        });
        

        $.ajax({
            url: '/admin/inventory/check-expiry/' + productId + '/',
            method: 'GET',
            success: function(data) {
                var stockExpiry = data.expiry;
                
                if(stockExpiry != null) {
                    var stockExpiryDate = new Date(stockExpiry);
                    var today = new Date();

                    if(stockExpiryDate < today) {
                        $('#errorModal .modal-body').html("The product is already expired. <br><br><a href='/admin/inventory/'>Click here</a> to view the list of product.");
                        $('#errorModal').modal('show');
                        quantityInput.focus();
                        return;
                    }
                }
                
                $.ajax({
                    url: '/admin/inventory/check-quantity/' + productId + '/',
                    method: 'GET',
                    success: function(data) {
                        var stockQuantity = data.quantity;

                        if(stockQuantity != null) {
                            if(parseFloat(quantity) > stockQuantity) {
                                $('#errorModal .modal-body').text("The entered quantity is greater than the stock quantity.");
                                $('#errorModal').modal('show');
                                quantityInput.focus();
                                return;
                            }
                            else if(parseFloat(quantity) <= 0)
                            {
                                $('#errorModal .modal-body').text("The entered quantity is invalid.");
                                $('#errorModal').modal('show');
                                quantityInput.focus();
                                return;
                            }
                        }

                        selectedProductIds.add(productId);
    
                        $this.prop('disabled', true);
                    
                        productPrice = productPrice.replace("₱", "").trim();
                        productPrice = productPrice.replace(/,/g, "").trim();
                        productPrice = parseFloat(productPrice);
                    
                        total += productPrice * parseFloat(quantity);
                    
                        var price = parseFloat(productPrice) * parseFloat(quantity);
                        var formattedPrice = price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    
                        var newRow = `
                            <tr class="selected-product" data-product-id="${productId}" data-product-quantity="${quantity}">
                                <td>
                                    <div class="fw-bold">
                                        ${productName} x <span class="product-quantity">${quantity}</span>
                                        <a class="btn btn-datatable btn-icon btn-transparent-dark remove-product" href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="Remove">
                                            <i data-feather="delete"></i>
                                        </a>
                                    </div>
                                    <div class="small text-muted d-none d-md-block">${productType}</div>
                                </td>
                                <td class="text-end fw-bold"><!-- empty for spacing --></td>
                                <td class="text-end fw-bold"><!-- empty for spacing --></td>
                                <td class="text-end fw-bold product-price">₱ ${formattedPrice}</td>
                            </tr>
                        `;
                    
                        $('#total-row').before(newRow);
                        $('#addProductModal').modal('hide');
                    
                        $('.total-amount').text('Total Amount: ₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
                    
                        feather.replace();
                    }
                });
            }
        });
    });    

    $(document).on('click', '.remove-service', function(e) {
        e.preventDefault();
    
        var serviceId = $(this).parents('tr').data('service-id');
    
        // Remove the service ID from the set of selected services
        selectedServiceIds.delete(serviceId);
    
        var serviceFee = $(this).parents('tr').find('.service-fee').text();
        serviceFee = serviceFee.replace("₱", "").trim();
        serviceFee = serviceFee.replace(/,/g, "").trim();
        
        total -= parseFloat(serviceFee.replace("₱", "").trim());
        
        $('.total-amount').text('Total Amount: ₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));

        $('.add-service[data-service-id="' + serviceId + '"]').prop('disabled', false);

        $(this).closest('tr').remove();
    });

    $(document).on('click', '.remove-product', function(e) {
        e.preventDefault();
    
        var productId = $(this).parents('tr').data('product-id');

        selectedProductIds.delete(productId);

        var productPrice = $(this).parents('tr').find('.product-price').text();
        productPrice = productPrice.replace("₱", "").trim();
        productPrice = productPrice.replace(/,/g, "").trim();
    
        total -= parseFloat(productPrice.replace("₱", "").trim());
    
        $('.total-amount').text('₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
    
        $('.add-product[data-product-id="' + productId + '"]').prop('disabled', false);
    
        $(this).closest('tr').remove();
    });
});

    $('#paid-button').on('click', function() {
        var clientId = $('.selected-client-input').data('client-id');
        var clientName = $('.selected-client-input').val().trim();
        var serviceIds = [];
        var productIds = [];

        $('.selected-service').each(function() {
            serviceIds.push($(this).data('service-id'));
        });

        $('.selected-product').each(function() {
            productIds.push($(this).data('product-id'));
        });

        if(!clientId && clientName === '')
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
        if (clientId === '') {
            clientId = undefined;
        }
        var fullName = $('.selected-client-input').val();
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

        var data = {
            'full_name': fullName,
            'service_ids': serviceIds,
            'product_ids': productIds,
            'quantities': quantities,
        };

        // Only include client_id in the data if it's not undefined
        if (clientId !== undefined) {
            data.client_id = clientId;
        }

        $.ajax({
            url: '/admin/bill/post/',
            method: 'POST',
            data: data,
            dataType: 'json',
            success: function(data) {
                $('#addBillSuccess').modal('show');
            }
        });
    });

// $(document).ready(function() {
//     function formatBillId(billId) 
//     {
//         let billIdStr = String(billId);
//         while (billIdStr.length < 6) {
//             billIdStr = '0' + billIdStr;
//         }
//         billIdStr = billIdStr.slice(0, 3) + '-' + billIdStr.slice(3);
//         return billIdStr;
//     }

//     let billId = $('.billing-number').text();
//     let billIdModal = $('.billing-number-modal').text();

//     let formattedBillId = formatBillId(billId);
//     let formattedBillIdModal = formatBillId(billIdModal);

//     $('.billing-number').text(formattedBillId);
//     $('.billing-number-modal').text(formattedBillIdModal);
// });

$('#success-add-billing').on('click', function() {
    window.location.href = "/admin/bill/";
});
