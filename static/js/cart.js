$(document).ready(function() {
    $('.add-to-cart-link').click(function(e) {
        e.preventDefault();

        let link = $(this);
        let product_id = link.data('product-id');
        let quantity = 1;

        $.ajax({
            type: 'POST',
            url: '/add-to-cart/' + product_id + '/' + 'White' + '/' + 'xl' + '/' + quantity + '/',
            data: {
                'product_id': product_id,
                'quantity': quantity,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                location.reload()
            },
            error: function(xhr, status, errorThrown) {
                console.log(errorThrown);
            }
        })
    })
})