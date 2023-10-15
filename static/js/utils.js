document.addEventListener("DOMContentLoaded", function () {
  const links = document.querySelectorAll(".add-to-cart-link");

  links.forEach((link) => {
    link.addEventListener("click", function (event) {
      event.preventDefault();

      const productId = this.getAttribute("data-product-id");
      let selectedColor = this.getAttribute("data-color-id");
      let selectedSize = this.getAttribute("data-size-id");
      let quantity = 1;
      console.log(selectedSize);
      console.log(selectedColor);

      const addToCartUrl = `/add-to-cart/${productId}/${selectedColor}/${selectedSize}/${quantity}`;

      // Redirect to the generated URL
      window.location.href = addToCartUrl;
    });
  });
});

$(document).ready(function () {
  $("a#add-to-wishlist-button").click(function (e) {
    e.preventDefault();

    let icon = $(this).find(".fa");
    let productId = icon.data("product-id");

    $.ajax({
      type: "POST",
      url: "/product/add-to-wishlist/",
      data: {
        product_id: productId,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
      },
      success: function (data) {
        if (data.added) {
          icon.removeClass("fa-heart-o").addClass("fa-heart");
        } else {
          icon.removeClass("fa-heart").addClass("fa-heart-o");
        }
      },
    });
  });

  updatePrices();

  // Listen for changes in the currency preference
  $("select.currency_preference").on("change", function() {
      updatePrices();
  });

  function updatePrices() {
    var selectedCurrency = $("select.currency_preference").val();
    $(".product__price").each(function () {
      var price = parseFloat(
        $(this).data(selectedCurrency.toLowerCase() + "-price")
      );
      $(this).text(formatPrice(price, selectedCurrency));
    });
  }

  function formatPrice(price, selectedCurrency) {
    // Assuming the currency symbol is "$" for USD, "₦" for NGN, and "€" for EUR
    var currencySymbol = "";
    var decimalPlaces = 2; // You can adjust this to the desired number of decimal places

    if (selectedCurrency === "USD") {
      currencySymbol = "$";
    } else if (selectedCurrency === "NGN") {
      currencySymbol = "₦";
    } else if (selectedCurrency === "EUR") {
      currencySymbol = "€";
    }

    // Format the price with currency symbol and decimal places
    return currencySymbol + price.toFixed(decimalPlaces);
  }

});
