document.addEventListener("DOMContentLoaded", function() {
    const links = document.querySelectorAll('.add-to-cart-link');
    
    links.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
    
            const productId = this.getAttribute('data-product-id');
            let selectedColor = this.getAttribute('data-color-id');
            let selectedSize = this.getAttribute('data-size-id'); 
            let quantity = 1  
    
            const addToCartUrl = `/add-to-cart/${productId}/${selectedColor}/${selectedSize}/${quantity}`;
    
            // Redirect to the generated URL
            window.location.href = addToCartUrl;
        });
    })
});