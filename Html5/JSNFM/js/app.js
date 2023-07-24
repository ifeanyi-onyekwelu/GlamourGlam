(function () {
    "use strict"

    const mobileNavToggler = document.querySelector('.mobile-nav-toggler');
    const nav = document.querySelector('.nav');
    let navBarPresent = false;

    mobileNavToggler.addEventListener('click', e => {
        navBarPresent = !navBarPresent;
        if (navBarPresent) {
            nav.style.display = "block"
        }
        else {
            nav.style.display = "none"
        }
    })

    // Join Us Function
    const join_us_btn = document.querySelector('.join-us');
    const join_us_popup_modal = document.querySelector('.join-us-modal-popup')
    const close_modal_popup = document.querySelector('.close-modal-popup');

    join_us_btn.addEventListener('click', e => {
        join_us_popup_modal.classList.remove('d-none');
    });

    close_modal_popup.addEventListener("click", e => {
        join_us_popup_modal.classList.add("d-none");
    })

    /**
    * Animation on scroll
    */
    window.addEventListener('load', () => {
        AOS.init({
            duration: 1000,
            easing: "ease-in-out",
            once: true,
            mirror: false
        });
    });

    // The hero section slider
    new Swiper('.hero-slider', {
        speed: 600,
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: true
        },
        slidesPerView: 'auto',
        pagination: {
            el: '.swiper-pagination',
            type: 'bullets',
            clickable: true
        },
    });


    // The Blog section slider
    new Swiper('.blog-slider', {
        speed: 600,
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false
        },
        slidesPerView: 'auto',
        pagination: {
            el: '.swiper-pagination',
            type: 'bullets',
            clickable: true
        },
        breakpoints: {
            320: {
                slidesPerView: 1,
                spaceBetween: 40
            },
            480: {
                slidesPerView: 1,
                spaceBetween: 60
            },
            640: {
                slidesPerView: 2,
                spaceBetween: 80
            },
            768: {
                slidesPerView: 1,
                spaceBetween: 80
            },
            992: {
                slidesPerView: 2,
                spaceBetween: 120
            }
        }
    });

    // Initialize and add the map
    let map;

    async function initMap() {
        // The location of Uluru
        const position = { lat: -25.344, lng: 131.031 };
        // Request needed libraries.
        //@ts-ignore
        const { Map } = await google.maps.importLibrary("maps");
        const { AdvancedMarkerView } = await google.maps.importLibrary("marker");

        // The map, centered at Uluru
        map = new Map(document.getElementById("map"), {
            zoom: 4,
            center: position,
            mapId: "DEMO_MAP_ID",
        });

        // The marker, positioned at Uluru
        const marker = new AdvancedMarkerView({
            map: map,
            position: position,
            title: "Uluru",
        });
    }

    initMap();
})()