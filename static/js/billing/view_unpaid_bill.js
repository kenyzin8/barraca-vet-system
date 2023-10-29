$(document).ready(function() {
    $('.service-fee').each(function() {
        var fee = parseFloat($(this).text().replace('₱ ', '').replace(',', ''));
        $(this).text('₱ ' + fee.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
    });

    var total = parseFloat($('.total-amount').text().replace('₱ ', '').replace(',', ''));

    $('.total-amount').text('₱ ' + total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));

    // function formatBillId(billId) {
    //     let billIdStr = String(billId);
    //     while (billIdStr.length < 6) {
    //         billIdStr = '0' + billIdStr;
    //     }
    //     billIdStr = billIdStr.slice(0, 3) + '-' + billIdStr.slice(3);
    //     return billIdStr;
    // }

    // let billId = $('.billing-number').text();

    // let formattedBillId = formatBillId(billId);

    // $('.billing-number').text(formattedBillId);

    $('tr').each(function() {
        var product_price = parseFloat($(this).find('.product-price').text().replace('₱ ', '').replace(',', ''));
        var product_quantity = parseFloat($(this).find('.product-quantity').text());
        var product_totalPrice = product_price * product_quantity;
        if(product_totalPrice || product_price || product_quantity){
            $(this).find('.product-price-multiplied').text('₱ ' + product_totalPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
        }
        else{
            $(this).find('.product-price-multiplied').text('₱ 0');
        }

        var service_fee = parseFloat($(this).find('.service-price').text().replace('₱ ', '').replace(',', ''));
        var service_quantity = parseFloat($(this).find('.service-quantity').text());
        var service_totalPrice = service_fee * service_quantity;
        if(service_totalPrice || service_fee || service_quantity){
            $(this).find('.service-price-multiplied').text('₱ ' + service_totalPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
        }
        else{
            $(this).find('.service-price-multiplied').text('₱ 0');
        }
    });
});
