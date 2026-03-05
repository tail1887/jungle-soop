(function () {
    async function handleUserProfileClick(event) {
        const link = event.target.closest(".js-user-profile");
        if (!link) {
            return;
        }
        event.preventDefault();

        const userId = link.dataset.userId;
        if (!userId) {
            return;
        }

        try {
            const res = await fetch(`/api/v1/users/${userId}`);
            const body = await res.json().catch(() => ({}));
            if (!res.ok) {
                const msg =
                    body?.error?.message || "유저 정보를 가져오지 못했습니다.";
                alert(msg);
                return;
            }
            const data = body.data || {};
            const nickname = data.nickname || "(닉네임 없음)";
            const email = data.email || "(이메일 없음)";
            alert(`닉네임: ${nickname}\n이메일: ${email}`);
        } catch (_err) {
            alert("유저 정보를 불러오는 중 오류가 발생했습니다.");
        }
    }

    function initUserProfileClickHandler() {
        document.addEventListener("click", handleUserProfileClick);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initUserProfileClickHandler);
    } else {
        initUserProfileClickHandler();
    }
})();