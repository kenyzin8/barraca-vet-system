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
        var price = parseFloat($(this).find('.product-price').text().replace('₱ ', '').replace(',', ''));
        var quantity = parseFloat($(this).find('.product-quantity').text());
        var totalPrice = price * quantity;
        $(this).find('.product-price-multiplied').text('₱ ' + totalPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
    });
});
