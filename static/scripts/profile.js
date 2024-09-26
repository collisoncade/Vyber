// [MB] Menu Bars 
const menu = document.querySelector(".menu");
const dropdownMenu = document.querySelector(".dropdown-menu");
const menuContainer = document.querySelector(".menu-dropdown-container");

// [SD] Season dropdown
const seasonSelect = document.querySelector(".season-select");
const seasonDropdown = document.querySelector(".season-dropdown");
const seasonContainer = document.querySelector(".season-dropdown-container");

// [WD] Week dropdown
const weekSelect = document.querySelector(".week-select");
const weekDropdown = document.querySelector(".week-dropdown");
const weekContainer = document.querySelector(".week-dropdown-container");

// [MB]
menu.addEventListener("mouseenter", (e) => {
    e.stopPropagation();
    dropdownMenu.classList.toggle("visible");
});

window.addEventListener("click", (e) => {
    if (!menuContainer.contains(e.target)) {
        if (dropdownMenu.classList.contains("visible")) {
            dropdownMenu.classList.toggle("visible");
        }
    }
});

// [SD]
seasonSelect.addEventListener("mouseenter", (e) => {
    e.stopPropagation();
    seasonDropdown.classList.toggle("visible");
});

seasonContainer.addEventListener("mouseleave", (e) => {
    seasonDropdown.classList.remove("visible");
})

window.addEventListener("click", (e) => {
    if (!seasonContainer.contains(e.target)) {
        if (seasonDropdown.classList.contains("visible")) {
            seasonDropdown.classList.toggle("visible");
        }
    }
});

// [WD]
weekSelect.addEventListener("mouseenter", (e) => {
    e.stopPropagation();
    weekDropdown.classList.toggle("visible");
});

weekContainer.addEventListener("mouseleave", (e) => {
    weekDropdown.classList.remove("visible");
})

window.addEventListener("click", (e) => {
    if (!weekContainer.contains(e.target)) {
        if (weekDropdown.classList.contains("visible")) {
            weekDropdown.classList.toggle("visible");
        }
    }
});

// Verify user upon page loading
document.addEventListener('DOMContentLoaded', function() {
    var token = localStorage.getItem('token');
    if (!token) {
        window.location.replace('/login');
        return;
    }

    fetch('/verify-user', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => {
        if (!response.ok) {
            window.location.replace('/login');
        }
        return response.json();
    })
    .catch(error => console.error('Error during verification', error));
});