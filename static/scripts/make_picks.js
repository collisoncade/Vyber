const username = localStorage.getItem('username');

// [MB] Menu Bars 
const menu = document.querySelector(".menu");
const dropdownMenu = document.querySelector(".dropdown-menu");
const menuContainer = document.querySelector(".menu-dropdown-container");

// [P] Pick
const pick = document.querySelector(".pick");

// [PI] Pick Image
const pickImage = document.querySelector(".pick-image");

// [MB]
menu.addEventListener("mouseenter", (e) => {
    e.stopPropagation();
    dropdownMenu.classList.toggle("visible");
});

// [GMS]
const games = document.querySelectorAll('.game');

// [BTNS]
const buttons = document.querySelectorAll('.select-button');

const profileButton = document.querySelector('.profile');
const profileDropdown = document.querySelector('.profile-dropdown');
const profileContainer = document.querySelector('.profile-dropdown-container');

window.addEventListener("click", (e) => {
    if (!menuContainer.contains(e.target)) {
        if (dropdownMenu.classList.contains("visible")) {
            dropdownMenu.classList.toggle("visible");
        }
    }
});

buttons.forEach(button => {
    button.addEventListener('click', function(e) {
        const clickedButton = e.currentTarget;
        const gameId = clickedButton.getAttribute('data-game-id');
        const team = clickedButton.getAttribute('data-team');

        const awayButton = document.getElementById(`away-team-${gameId}`);
        const homeButton = document.getElementById(`home-team-${gameId}`);

        if (!awayButton || !homeButton) {
            console.error('Buttons not found for game ID:', gameId);
            return;
        }

        if (team === 'away-team') {
            awayButton.classList.add('p-away-team-picked');
            homeButton.classList.remove('p-home-team-picked');
            homeButton.classList.add('select-button');
            awayButton.classList.remove('select-button');
        } else if (team === 'home-team') {
            homeButton.classList.add('p-home-team-picked');
            awayButton.classList.remove('p-away-team-picked');
            awayButton.classList.add('select-button');
            homeButton.classList.remove('select-button');
        }
    });
});

profileButton.addEventListener("mouseenter", (e) => {
    e.stopPropagation();
    profileContainer.classList.toggle("visible");
});

profileButton.addEventListener("mouseleave", (e) => {
    profileContainer.classList.remove("visible");
});

function makePick(game_id, pick) {
    return fetch('/make-pick', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ game_id: game_id, pick: pick, username: username})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
}

function logout() {
    localStorage.removeItem('username');
    window.location.replace('/');
}

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