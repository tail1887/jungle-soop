(function () {
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

    function setMessage(el, text, type) {
        if (!el) return;
        el.textContent = text;
        el.classList.remove("is-error", "is-success");
        if (type === "error") el.classList.add("is-error");
        if (type === "success") el.classList.add("is-success");
    }

    async function loadUserProfile() {
        const root = document.getElementById("user-profile-root");
        const messageEl = document.getElementById("user-profile-message");
        const avatarEl = document.getElementById("user-profile-avatar-image");
        const nicknameEl = document.getElementById("user-profile-nickname");
        const emailEl = document.getElementById("user-profile-email");
        if (!root || !messageEl || !avatarEl || !nicknameEl || !emailEl) {
            return;
        }

        const userId = root.dataset.userId || "";
        if (!userId) {
            setMessage(messageEl, "잘못된 사용자 경로입니다.", "error");
            return;
        }

        const token = getAccessToken();
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        setMessage(messageEl, "프로필을 불러오는 중...", "");

        try {
            const response = await fetch(`/api/v1/users/${encodeURIComponent(userId)}`, { headers });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = "/login";
                    return;
                }
                const errorMessage = result?.error?.message || "프로필을 불러오지 못했습니다.";
                setMessage(messageEl, errorMessage, "error");
                return;
            }

            const data = result?.data || {};
            avatarEl.src = data.profile_image_url || "";
            nicknameEl.textContent = data.nickname || "-";
            emailEl.textContent = data.email || "-";
            setMessage(messageEl, "프로필을 불러왔습니다.", "success");
        } catch (_error) {
            setMessage(messageEl, "네트워크 오류가 발생했습니다.", "error");
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", loadUserProfile);
    } else {
        loadUserProfile();
    }
})();
