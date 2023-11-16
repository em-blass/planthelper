document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    if (username === 'admin' && password === 'admin') {
        alert('Login successful!');
        // Redirect to another page or perform some action
        window.location.href = 'welcome.html'; // Redirect to a welcome page
    } else {
        alert('Invalid Credentials');
    }
});
