document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const status = document.getElementById("authStatus");

    loginForm?.addEventListener("submit", async event => {
        event.preventDefault();

        status.textContent = "Signing in...";

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: document.getElementById("email").value,
                    password: document.getElementById("password").value
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Login failed."
                );
            }

            window.location.href = "/";

        } catch (error) {
            status.textContent = error.message;
        }
    });

    registerForm?.addEventListener("submit", async event => {
        event.preventDefault();

        status.textContent = "Creating account...";

        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: document.getElementById("username").value,
                    email: document.getElementById("email").value,
                    password: document.getElementById("password").value
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Registration failed."
                );
            }

            window.location.href = "/";

        } catch (error) {
            status.textContent = error.message;
        }
    });
});
