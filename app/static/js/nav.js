const ACCESS_TOKEN_KEY = "access_token";

function getCookieValue(name) {
    const target = `${name}=`;
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const rawCookie of cookies) {
        const cookie = rawCookie.trim();
        if (cookie.startsWith(target)) {
            return decodeURIComponent(cookie.slice(target.length));
        }
    }
    return "";
}

function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY) || getCookieValue(ACCESS_TOKEN_KEY);
}

function clearAccessToken() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    document.cookie = `${ACCESS_TOKEN_KEY}=; Max-Age=0; path=/`;
}

async function requestLogout() {
    try {
        const token = getAccessToken();
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        await fetch("/api/v1/auth/logout", { method: "POST", headers });
    } catch (_error) {
        // 네트워크 오류가 있어도 로그인 페이지로 이동시킵니다.
    }
}

function bindLogoutButton() {
    const logoutButton = document.getElementById("nav-logout-button");
    if (!logoutButton) {
        return;
    }

    logoutButton.addEventListener("click", async () => {
        await requestLogout();
        clearAccessToken();
        window.location.href = "/login";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    bindLogoutButton();
});
