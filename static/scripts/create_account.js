document.addEventListener('DOMContentLoaded', function() {
    var emailInput = document.getElementById('email');
    var usernameInput = document.getElementById('username');
    var passwordInput = document.getElementById('password');
    var registerForm = document.getElementById('register-form');

    console.log('emailInput:', emailInput);
    console.log('usernameInput:', usernameInput);
    console.log('passwordInput:', passwordInput);
    console.log('registerForm:', registerForm);

    var emailFound = false;
    var usernameFound = false;

    usernameInput.addEventListener('input', function() {
        var email = emailInput.value.trim();
        checkEmailExists(email);
    });

    passwordInput.addEventListener('input', function() {
        var username = usernameInput.value.trim();
        checkUsernameExists(username);
    });

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        var email = emailInput.value.trim();
        var username = usernameInput.value.trim();
        var password = passwordInput.value.trim();

        if (!emailFound && !usernameFound) {
            registerUser(email, username, password);
        } else {
            window.location.href = "/create-account";
        }
    });

    function registerUser(email, username, password) {
        fetch('/create-account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: password
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            window.location.replace('/login');
        })
        .catch(error => {
            console.error('Error registering user:', error);
            alert('Registration failed. Please try again.');
        });
    };

    function checkEmailExists(email) {
        fetch('/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok')
            }
            return response.json()
        })
        .then(data => {
            var emailExistence = document.querySelector('.email-existence');
            if (data.exists) {
                emailExistence.textContent = "Email address already being used!";
                emailFound = true;
            } else {
                document.querySelector('.email-existence').style.display = "none";
                emailFound = false;
            }
            emailFound = data.exists;
        })
        .catch(error => console.error('Error checking email:', error));
    }

    function checkUsernameExists(username) {
        fetch('/check-username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok')
            }
            return response.json()
        })
        .then(data => {
            var usernameExistence = document.querySelector('.username-existence');
            if (data.exists) {
                usernameExistence.textContent = "Username already exists!";
            } else {
                usernameExistence.style.display = "none";
            }
            usernameFound = data.exists;
        })
        .catch(error => console.error('Error fethcing users:', error));
    };
});

function navigateToLoginPage() {
    window.location.replace('/login');
}