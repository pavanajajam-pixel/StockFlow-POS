// =====================================================
// STOCKFLOW LOGIN
// =====================================================

const loginForm = document.getElementById("loginForm");

const usernameInput = document.getElementById("username");

const passwordInput = document.getElementById("password");

const togglePassword =
    document.getElementById("togglePassword");

const loginButton =
    document.getElementById("loginButton");

const loginMessage =
    document.getElementById("loginMessage");


// =====================================================
// SHOW / HIDE PASSWORD
// =====================================================

togglePassword.addEventListener("click", function () {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        togglePassword.textContent = "Hide";

    } else {

        passwordInput.type = "password";

        togglePassword.textContent = "Show";

    }

});


// =====================================================
// LOGIN FORM
// =====================================================

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const username =
        usernameInput.value.trim();

    const password =
        passwordInput.value.trim();


    // =================================================
    // VALIDATION
    // =================================================

    if (username === "") {

        showMessage(
            "Please enter your username.",
            "error"
        );

        usernameInput.focus();

        return;
    }


    if (password === "") {

        showMessage(
            "Please enter your password.",
            "error"
        );

        passwordInput.focus();

        return;
    }


    // =================================================
    // LOGIN BUTTON
    // =================================================

    loginButton.disabled = true;

    loginButton.innerHTML =
        "<span>Signing in...</span>";

    clearMessage();


    // =================================================
    // SEND LOGIN REQUEST TO FLASK
    // =================================================

    try {

        const response = await fetch(
            "https://stockflow-pos-yorq.onrender.com/api/login",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );


        const data = await response.json();


        // =================================================
        // LOGIN SUCCESS
        // =================================================

        if (response.ok && data.success) {

            showMessage(
                "Login successful! Redirecting...",
                "success"
            );


            // Save logged-in staff information
            localStorage.setItem("stockflowStaff", JSON.stringify(data.staff));
            localStorage.setItem("staffName", data.staff.username);
            localStorage.setItem("staffRole", data.staff.role);
            localStorage.setItem("staffId", data.staff.staff_id);


            // Redirect to dashboard
            setTimeout(function () {

                window.location.href =
                    "dashboard.html";

            }, 700);

        }


        // =================================================
        // LOGIN FAILED
        // =================================================

        else {

            showMessage(
                data.message ||
                "Incorrect username or password.",
                "error"
            );

            loginButton.disabled = false;

            loginButton.innerHTML =
                "<span>Sign in</span>" +
                "<span class='arrow'>→</span>";

            passwordInput.value = "";

            passwordInput.focus();
        }

    }


    // =================================================
    // CONNECTION ERROR
    // =================================================

    catch (error) {

        console.error(
            "Login Error:",
            error
        );

        showMessage(
            "Unable to connect to StockFlow server. Make sure Flask is running.",
            "error"
        );

        loginButton.disabled = false;

        loginButton.innerHTML =
            "<span>Sign in</span>" +
            "<span class='arrow'>→</span>";
    }

});


// =====================================================
// SHOW MESSAGE
// =====================================================

function showMessage(message, type) {

    loginMessage.textContent = message;


    if (type === "error") {

        loginMessage.style.color =
            "#dc2626";

    }

    else if (type === "success") {

        loginMessage.style.color =
            "#16a34a";

    }

}


// =====================================================
// CLEAR MESSAGE
// =====================================================

function clearMessage() {

    loginMessage.textContent = "";

}


// =====================================================
// REGISTER PAGE
// =====================================================

function goToRegister(event) {

    event.preventDefault();

    window.location.href =
        "register.html";

}
