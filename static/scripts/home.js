const menuContainer = document.querySelector(".menu-container");
const menu = document.querySelector(".menu");
const dropdownMenu = document.querySelector(".dropdown-menu");

menu.addEventListener("click", (e) => {
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

function navigateToCreateAccountPage() {
    window.location.replace('/create-account');
};

function navigateToLoginPage() {
    window.location.replace('/login');
}