async function requestLogout() {
    try {
        await fetch("/api/v1/auth/logout", { method: "POST" });
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
        document.cookie = "access_token=; Max-Age=0; path=/";
        window.location.href = "/login";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    bindLogoutButton();
});
