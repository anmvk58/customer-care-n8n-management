$(function () {
    const $overlay = $('#loading-overlay');
    if ($overlay.length) {
        // Nếu tài nguyên chưa load xong, đợi sự kiện load
        if (document.readyState !== 'complete') {
            $(window).on('load', function () {
            $overlay.fadeOut(500);
            });
        } else {
            // Nếu đã load xong rồi, ẩn ngay
            $overlay.fadeOut(500);
        }
    }
});


// Login JS
const days = 7;
const expires = new Date(Date.now() + days * 86400000).toUTCString();
const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        const payload = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            payload.append(key, value);
        }

        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: payload.toString()
            });

            if (response.ok) {
                // Handle success (e.g., redirect to dashboard)
                const data = await response.json();
                // Delete any cookies available
                logout();
                // Save token to cookie
                document.cookie = `access_token=${data.access_token}; path=/; expires=${expires}`;

                window.location.href = '/'; // Change this to your desired redirect page
            } else {
                // Handle error
                const errorData = await response.json();
//                alert(`Error: ${errorData.detail}`);
                pushNotification('Authentication Error', errorData.detail, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            pushNotification('Authentication Error', 'Lỗi thông tin đăng nhập không hợp lệ', 'error');
        }
    });
}

// Register JS
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.password2) {
//            alert("Passwords do not match");
            pushNotification('Registration Error', "Passwords do not match", 'error');
            return;
        }

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.firstname,
            last_name: data.lastname,
            role: data.role,
            phone_number: data.phone_number,
            password: data.password
        };

        try {
            const response = await fetch('/auth', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {

                pushNotification('Registration Success', 'Chuyển sang trang đăng nhập trong 3s', 'success');
                setTimeout(function() {
                    window.location.href = '/auth/login-page';
                }, 3000);
            } else {
                // Handle error
                const errorData = await response.json();
                pushNotification('Registration Error', errorData.message, 'error');
//                alert(`Error: ${errorData.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            pushNotification('Registration Error', 'Có lỗi xảy ra khi đăng ký', 'error');
        }
    });
}


// Helper function to get a cookie by name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// Function logout (remove access token from cookies)
function logout() {
    // Get all cookies
    const cookies = document.cookie.split(";");

    // Iterate through all cookies and delete each one
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        // Set the cookie's expiry date to a past date to delete it
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
    }

    // Redirect to the login page
    window.location.href = '/auth/login-page';
};

// Function allow push notification from any where
function pushNotification(title, message, type) {
    toastr[type](message, title, {
        positionClass: "toast-top-right",
        closeButton: true,
        progressBar: true,
        newestOnTop: true,
        rtl: false,
        timeOut:2000
    });
}