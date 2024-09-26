var usernameInput = document.getElementById('username');
var passwordInput = document.getElementById('password');
var loginForm = document.getElementById('login-form');

passwordInput.addEventListener('input', function() {
    var username = usernameInput.value.trim();
    checkUsernameExists(username);
});

loginForm.addEventListener('submit', function(e) {
    e.preventDefault();

    var username = usernameInput.value.trim();
    var password = passwordInput.value.trim();

    fetch('/log-user-in', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Login failed');
        }
        return response.json();
    })
    .then(data => {
        localStorage.setItem('username', username)
        localStorage.setItem('token', data.token);
        window.location.replace('/profile');
    })
    .catch(error => console.error('Error:', error));
});

function checkUsernameExists(username) {
    return fetch('/check-username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        var usernameExistence = document.querySelector('.username-existence');
        if (!data.exists) {
            usernameExistence.textContent = "No user found!";
        } else {
            usernameExistence.style.display = "none";
        }
    })
    .catch(error => console.error('Error fetching users:', error));
};

function navigateToCreateAccountPage() {
    window.location.href = '/create-account';
}