document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    if (username === 'admin' && password === 'admin') {
        alert('Login successful!');
        window.location.href = 'welcome.html';
    } else {
        alert('Invalid Credentials');
    }
});
