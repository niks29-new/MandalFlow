// ==========================================
// KN STREET CHA RAJA
// Dashboard JS
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    updateGreeting();

    animateCounters();

    revealCards();

});
// ==========================================
// Greeting
// ==========================================

function updateGreeting() {

    const greeting = document.getElementById("greeting");

    if (!greeting) return;

    const hour = new Date().getHours();

    let message = "";

    if (hour < 12) {

        message = "🌅 Good Morning";

    } else if (hour < 17) {

        message = "☀️ Good Afternoon";

    } else {

        message = "🌙 Good Evening";

    }

    greeting.textContent = message;

}
// ==========================================
// Counter Animation
// ==========================================

function animateCounters() {

    const counters = document.querySelectorAll(".premium-card h2");

    counters.forEach(function(counter) {

        const text = counter.textContent.trim();

        // Skip if not a number
        if (!text.match(/\d/)) return;

        // Remove ₹ and commas
        const target = parseInt(
            text.replace(/[₹,]/g, "")
        );

        if (isNaN(target)) return;

        let current = 0;

        const increment = Math.max(1, Math.ceil(target / 80));

        const timer = setInterval(function() {

            current += increment;

            if (current >= target) {

                current = target;

                clearInterval(timer);

            }

            // Currency values
            if (text.includes("₹")) {

                counter.textContent =
                    "₹" + current.toLocaleString();

            }

            // Normal numbers
            else {

                counter.textContent =
                    current.toLocaleString();

            }

        }, 20);

    });

}
// ==========================================
// Reveal Animation
// ==========================================

function revealCards() {

    const cards = document.querySelectorAll(
        ".premium-card, .summary-card, .dashboard-box"
    );

    cards.forEach(function(card, index) {

        card.style.opacity = "0";

        card.style.transform = "translateY(30px)";

        setTimeout(function() {

            card.style.transition =
                "all .6s ease";

            card.style.opacity = "1";

            card.style.transform =
                "translateY(0)";

        }, index * 120);

    });

}

// ==========================================
// Card Hover Effect
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const cards = document.querySelectorAll(
        ".premium-card"
    );

    cards.forEach(function(card){

        card.addEventListener("mouseenter", function(){

            card.style.transform =
                "translateY(-8px) scale(1.02)";

        });

        card.addEventListener("mouseleave", function(){

            card.style.transform =
                "translateY(0) scale(1)";

        });

    });

});

// ==========================================
// Scroll To Top
// ==========================================

window.addEventListener("scroll", function(){

    const fab = document.querySelector(".fab");

    if(!fab) return;

    if(window.scrollY > 150){

        fab.style.boxShadow =
            "0 18px 35px rgba(0,0,0,.30)";

    }else{

        fab.style.boxShadow =
            "0 10px 25px rgba(0,0,0,.20)";

    }

});

// ==========================================
// Console Message
// ==========================================

console.log(
"🕉️ KN STREET CHA RAJA - Dashboard Loaded Successfully"
);