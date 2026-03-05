(function () {
const ACCESS_TOKEN_KEY = "access_token";
const TAB_ENDPOINTS = {
    created: "/api/v1/profile/meetings/created",
    joined_active: "/api/v1/profile/meetings/joined/active",
    joined_past: "/api/v1/profile/meetings/joined/past",
};
let currentProfile = null;

function setUiMessage(element, text, type) {
    if (!element) {
        return;
    }
    element.textContent = text;
    element.classList.remove("is-error", "is-success");
    if (type === "error") {
        element.classList.add("is-error");
    } else if (type === "success") {
        element.classList.add("is-success");
    }
}

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

async function fetchJson(url, options) {
    const requestOptions = options || {};
    const token = getAccessToken();
    const headers = { ...(requestOptions.headers || {}) };
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(url, { ...requestOptions, headers });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, status: response.status, data };
}

function formatApiError(result, fallbackMessage) {
    return result?.data?.error?.message || fallbackMessage;
}

function createMeetingListItem(meeting) {
    const li = document.createElement("li");
    li.className = "meeting-item";
    const meetingId = meeting.meeting_id || "unknown";
    const title = meeting.title || "제목 없음";
    const place = meeting.place || "장소 미정";
    const scheduledAt = meeting.scheduled_at || "일시 미정";
    const count = meeting.participant_count ?? 0;
    const maxCapacity = meeting.max_capacity ?? "-";
    const status = meeting.status || "open";

    li.innerHTML = `
        <a href="/meetings/${meetingId}">
            <strong>${title}</strong>
        </a>
        <p>${place} · ${scheduledAt}</p>
        <p>참여 ${count}/${maxCapacity} · 상태 ${status}</p>
    `;
    return li;
}

async function loadMyProfile() {
    const messageEl = document.getElementById("profile-message");
    const emailEl = document.getElementById("profile-email");
    const nicknameInput = document.getElementById("profile-nickname");
    if (!messageEl || !emailEl || !nicknameInput) {
        return;
    }

    setUiMessage(messageEl, "프로필을 불러오는 중...", "");
    const result = await fetchJson("/api/v1/profile/me");
    if (!result.ok) {
        if (result.status === 401) {
            window.location.href = "/login";
            return;
        }
        setUiMessage(messageEl, formatApiError(result, "프로필 조회에 실패했습니다."), "error");
        return;
    }

    const profile = result.data?.data || {};
    currentProfile = profile;
    emailEl.textContent = profile.email || "-";
    nicknameInput.value = profile.nickname || "";
    setProfileAvatarImage(profile.profile_image_url || "");
    setUiMessage(messageEl, "프로필을 불러왔습니다.", "success");
}

function setProfileAvatarImage(imageUrl) {
    const avatarImage = document.getElementById("profile-avatar-image");
    if (!avatarImage) {
        return;
    }
    if (imageUrl) {
        avatarImage.src = imageUrl;
    }
}

function bindProfileAvatarForm() {
    const form = document.getElementById("profile-avatar-form");
    const input = document.getElementById("profile-avatar-input");
    const saveButton = document.getElementById("profile-avatar-save-button");
    const messageEl = document.getElementById("profile-message");
    if (!form || !input || !saveButton || !messageEl) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const file = input.files && input.files[0];
        if (!file) {
            setUiMessage(messageEl, "업로드할 이미지를 선택해주세요.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("avatar", file);

        saveButton.disabled = true;
        setUiMessage(messageEl, "프로필 이미지 업로드 중...", "");
        try {
            const result = await fetchJson("/api/v1/profile/me/avatar", {
                method: "POST",
                body: formData,
            });
            if (!result.ok) {
                setUiMessage(messageEl, formatApiError(result, "프로필 이미지 업로드에 실패했습니다."), "error");
                return;
            }
            const profileImageUrl = result.data?.data?.profile_image_url || "";
            if (currentProfile) {
                currentProfile.profile_image_url = profileImageUrl;
            }
            setProfileAvatarImage(profileImageUrl);
            input.value = "";
            setUiMessage(messageEl, "프로필 이미지가 업데이트되었습니다.", "success");
        } catch (_error) {
            setUiMessage(messageEl, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            saveButton.disabled = false;
        }
    });
}

function bindProfileEditForm() {
    const form = document.getElementById("profile-edit-form");
    const messageEl = document.getElementById("profile-message");
    const saveButton = document.getElementById("profile-save-button");
    const nicknameInput = document.getElementById("profile-nickname");
    if (!form || !messageEl || !saveButton || !nicknameInput) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const nickname = (nicknameInput.value || "").trim();
        if (!nickname) {
            setUiMessage(messageEl, "수정할 닉네임을 입력해주세요.", "error");
            return;
        }

        saveButton.disabled = true;
        setUiMessage(messageEl, "닉네임 수정 중...", "");
        try {
            const result = await fetchJson("/api/v1/profile/me", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nickname }),
            });
            if (!result.ok) {
                setUiMessage(messageEl, formatApiError(result, "닉네임 수정에 실패했습니다."), "error");
                return;
            }
            setUiMessage(messageEl, "닉네임이 수정되었습니다.", "success");
        } catch (_error) {
            setUiMessage(messageEl, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            saveButton.disabled = false;
        }
    });
}

function setTabButtonActive(tabName) {
    const buttons = document.querySelectorAll(".profile-tab-button");
    buttons.forEach((button) => {
        if (!(button instanceof HTMLElement)) {
            return;
        }
        const active = button.dataset.tab === tabName;
        button.disabled = active;
    });
}

async function loadMeetingsTab(tabName) {
    const messageEl = document.getElementById("profile-meetings-message");
    const listEl = document.getElementById("profile-meetings-list");
    if (!messageEl || !listEl) {
        return;
    }
    const endpoint = TAB_ENDPOINTS[tabName];
    if (!endpoint) {
        return;
    }

    setTabButtonActive(tabName);
    setUiMessage(messageEl, "모임 목록을 불러오는 중...", "");
    listEl.innerHTML = "";

    try {
        const result = await fetchJson(endpoint);
        if (!result.ok) {
            if (result.status === 401) {
                window.location.href = "/login";
                return;
            }
            setUiMessage(messageEl, formatApiError(result, "모임 목록 조회에 실패했습니다."), "error");
            return;
        }
        const meetings = result.data?.data?.meetings || [];
        if (meetings.length === 0) {
            setUiMessage(messageEl, "해당 모임이 없습니다.", "");
            return;
        }
        meetings.forEach((meeting) => listEl.appendChild(createMeetingListItem(meeting)));
        setUiMessage(messageEl, `모임 ${meetings.length}건을 불러왔습니다.`, "success");
    } catch (_error) {
        setUiMessage(messageEl, "네트워크 오류가 발생했습니다.", "error");
    }
}

function bindMeetingsTabs() {
    const buttons = document.querySelectorAll(".profile-tab-button");
    if (!buttons.length) {
        return;
    }

    buttons.forEach((button) => {
        if (!(button instanceof HTMLElement)) {
            return;
        }
        button.addEventListener("click", () => {
            loadMeetingsTab(button.dataset.tab || "created");
        });
    });

    loadMeetingsTab("created");
}

function initProfilePage() {
    if (!document.getElementById("profile-root")) {
        return;
    }
    loadMyProfile();
    bindProfileEditForm();
    bindProfileAvatarForm();
    bindMeetingsTabs();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProfilePage);
} else {
    initProfilePage();
}
})();
