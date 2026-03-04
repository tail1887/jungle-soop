function setMessage(element, text, type) {
    if (!element) {
        return;
    }
    element.textContent = text;
    element.classList.remove("is-error", "is-success");
    if (type === "error") {
        element.classList.add("is-error");
    }
    if (type === "success") {
        element.classList.add("is-success");
    }
}

function validateEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function validateLogin(payload) {
    if (!payload.email || !payload.password) {
        return "이메일과 비밀번호를 모두 입력해주세요.";
    }
    if (!validateEmail(payload.email)) {
        return "유효한 이메일 형식을 입력해주세요.";
    }
    return "";
}

function validateSignup(payload) {
    if (!payload.nickname || !payload.email || !payload.password || !payload.passwordConfirm) {
        return "닉네임, 이메일, 비밀번호, 비밀번호 확인을 모두 입력해주세요.";
    }
    if (payload.nickname.trim().length < 2) {
        return "닉네임은 2자 이상 입력해주세요.";
    }
    if (!validateEmail(payload.email)) {
        return "유효한 이메일 형식을 입력해주세요.";
    }
    if (payload.password.length < 8) {
        return "비밀번호는 8자 이상 입력해주세요.";
    }
    if (payload.password !== payload.passwordConfirm) {
        return "비밀번호와 비밀번호 확인이 일치하지 않습니다.";
    }
    return "";
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, status: response.status, data };
}

function bindLoginForm() {
    const form = document.getElementById("login-form");
    const message = document.getElementById("login-message");
    const submitButton = document.getElementById("login-submit-button");
    if (!form || !message) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            email: form.email.value.trim(),
            password: form.password.value,
        };

        const validationMessage = validateLogin(payload);
        if (validationMessage) {
            setMessage(message, validationMessage, "error");
            return;
        }

        setMessage(message, "로그인 요청 중...", "");
        if (submitButton) {
            submitButton.style.display = "none";
        }
        const result = await postJson("/api/v1/auth/login", payload);
        if (!result.ok) {
            const errorMessage = result.data?.error?.message || "로그인에 실패했습니다.";
            setMessage(message, errorMessage, "error");
            if (submitButton) {
                submitButton.style.display = "";
            }
            return;
        }
        setMessage(message, "로그인에 성공했습니다.", "success");
    });
}

function bindSignupForm() {
    const form = document.getElementById("signup-form");
    const message = document.getElementById("signup-message");
    const submitButton = document.getElementById("signup-submit-button");
    if (!form || !message) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            nickname: form.nickname.value.trim(),
            email: form.email.value.trim(),
            password: form.password.value,
            passwordConfirm: form.password_confirm.value,
        };

        const validationMessage = validateSignup(payload);
        if (validationMessage) {
            setMessage(message, validationMessage, "error");
            return;
        }

        setMessage(message, "회원가입 요청 중...", "");
        if (submitButton) {
            submitButton.style.display = "none";
        }
        const result = await postJson("/api/v1/auth/signup", payload);
        if (!result.ok) {
            const errorMessage = result.data?.error?.message || "회원가입에 실패했습니다.";
            setMessage(message, errorMessage, "error");
            if (submitButton) {
                submitButton.style.display = "";
            }
            return;
        }
        setMessage(message, "회원가입에 성공했습니다.", "success");
    });
}

document.addEventListener("DOMContentLoaded", () => {
    bindLoginForm();
    bindSignupForm();
});
