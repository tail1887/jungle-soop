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

async function fetchJson(url, options) {
    const token = getAccessToken();
    const requestOptions = options || {};
    const mergedHeaders = { ...(requestOptions.headers || {}) };
    if (token) {
        mergedHeaders.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(url, { ...requestOptions, headers: mergedHeaders });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, status: response.status, data };
}

function fallbackMeetings() {
    return [
        {
            meeting_id: "sample-1",
            title: "샘플 스터디 모임",
            location: "기숙사 라운지",
            datetime: "2026-03-10T19:30",
            capacity: 4,
            participant_count: 2,
            description: "백엔드 구현 전 UI 테스트용 더미 데이터입니다.",
        },
        {
            meeting_id: "sample-2",
            title: "알고리즘 풀이 모임",
            location: "세미나실 A",
            datetime: "2026-03-11T20:00",
            capacity: 6,
            participant_count: 3,
            description: "목록/상세 이동 상태를 점검하기 위한 샘플입니다.",
        },
    ];
}

function createMeetingListItem(meeting) {
    const li = document.createElement("li");
    li.className = "meeting-item";
    const id = meeting.meeting_id || meeting._id || "unknown";
    const title = meeting.title || "제목 없음";
    const location = meeting.location || meeting.place || "장소 미정";
    const datetime = meeting.datetime || meeting.time || "일시 미정";
    const count = meeting.participant_count ?? 0;
    const capacity = meeting.capacity ?? "-";

    li.innerHTML = `
        <a href="/meetings/${id}">
            <strong>${title}</strong>
        </a>
        <p>${location} · ${datetime}</p>
        <p>참여 ${count}/${capacity}</p>
    `;
    return li;
}

async function loadMeetingsList() {
    const listElement = document.getElementById("meetings-list");
    const messageElement = document.getElementById("meetings-list-message");
    if (!listElement || !messageElement) {
        return;
    }

    setUiMessage(messageElement, "모임 목록을 불러오는 중...", "");
    listElement.innerHTML = "";
    let meetings = [];

    try {
        const result = await fetchJson("/api/v1/meetings");
        if (!result.ok) {
            meetings = fallbackMeetings();
            setUiMessage(
                messageElement,
                "API 미구현 상태여서 샘플 목록을 표시합니다.",
                "error"
            );
        } else {
            meetings = result.data?.data?.meetings || result.data?.meetings || [];
            setUiMessage(messageElement, "모임 목록을 불러왔습니다.", "success");
        }
    } catch (_error) {
        meetings = fallbackMeetings();
        setUiMessage(
            messageElement,
            "네트워크 오류로 샘플 목록을 표시합니다.",
            "error"
        );
    }

    if (meetings.length === 0) {
        setUiMessage(messageElement, "등록된 모임이 없습니다.", "");
        return;
    }

    meetings.forEach((meeting) => {
        listElement.appendChild(createMeetingListItem(meeting));
    });
}

function bindMeetingsListPage() {
    const refreshButton = document.getElementById("meetings-refresh-button");
    if (!refreshButton) {
        return;
    }
    refreshButton.addEventListener("click", () => {
        loadMeetingsList();
    });
    loadMeetingsList();
}

function parseCreateFormPayload(form) {
    return {
        title: form.title.value.trim(),
        datetime: form.datetime.value,
        location: form.location.value.trim(),
        description: form.description.value.trim(),
        capacity: Number(form.capacity.value),
    };
}

function validateCreateForm(payload) {
    if (!payload.title || !payload.datetime || !payload.location || !payload.capacity) {
        return "제목, 일시, 장소, 모집 인원을 입력해주세요.";
    }
    if (payload.capacity < 2 || payload.capacity > 20) {
        return "모집 인원은 2~20명 사이여야 합니다.";
    }
    return "";
}

function bindMeetingCreatePage() {
    const form = document.getElementById("meeting-create-form");
    const messageElement = document.getElementById("meeting-create-message");
    const submitButton = document.getElementById("meeting-create-submit-button");
    if (!form || !messageElement) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = parseCreateFormPayload(form);
        const validationMessage = validateCreateForm(payload);
        if (validationMessage) {
            setUiMessage(messageElement, validationMessage, "error");
            return;
        }

        setUiMessage(messageElement, "모임 생성 요청 중...", "");
        if (submitButton) {
            submitButton.style.display = "none";
        }

        try {
            const result = await fetchJson("/api/v1/meetings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!result.ok) {
                if (result.status === 401) {
                    setUiMessage(messageElement, "로그인이 필요합니다. 로그인 페이지로 이동합니다.", "error");
                    window.location.href = "/login";
                    return;
                }
                const msg =
                    result.data?.error?.message ||
                    "모임 생성 API가 아직 준비되지 않았습니다.";
                setUiMessage(messageElement, msg, "error");
                return;
            }

            setUiMessage(messageElement, "모임이 생성되었습니다. 목록으로 이동합니다.", "success");
            window.location.href = "/meetings";
        } catch (_error) {
            setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            if (submitButton) {
                submitButton.style.display = "";
            }
        }
    });
}

function setMeetingDetail(meeting) {
    const titleEl = document.getElementById("meeting-detail-title");
    const metaEl = document.getElementById("meeting-detail-meta");
    const descEl = document.getElementById("meeting-detail-description");
    if (!titleEl || !metaEl || !descEl) {
        return;
    }

    titleEl.textContent = meeting.title || "제목 없음";
    const location = meeting.location || meeting.place || "장소 미정";
    const datetime = meeting.datetime || meeting.time || "일시 미정";
    const count = meeting.participant_count ?? 0;
    const capacity = meeting.capacity ?? "-";
    metaEl.textContent = `${location} · ${datetime} · 참여 ${count}/${capacity}`;
    descEl.textContent = meeting.description || "설명이 없습니다.";
}

async function loadMeetingDetail() {
    const root = document.getElementById("meeting-detail-root");
    const messageElement = document.getElementById("meeting-detail-message");
    if (!root || !messageElement) {
        return;
    }
    const meetingId = root.dataset.meetingId;
    if (!meetingId) {
        return;
    }

    setUiMessage(messageElement, "모임 상세를 불러오는 중...", "");
    try {
        const result = await fetchJson(`/api/v1/meetings/${meetingId}`);
        if (!result.ok) {
            setMeetingDetail({
                title: `샘플 모임 (${meetingId})`,
                location: "API 미연동",
                datetime: "미정",
                capacity: 4,
                participant_count: 1,
                description: "상세 API 미구현 상태라 샘플 데이터를 표시합니다.",
            });
            setUiMessage(messageElement, "API 미구현 상태로 샘플 상세를 표시합니다.", "error");
            return;
        }

        const meeting = result.data?.data || result.data || {};
        setMeetingDetail(meeting);
        setUiMessage(messageElement, "모임 상세를 불러왔습니다.", "success");
    } catch (_error) {
        setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
    }
}

function bindMeetingDetailPage() {
    const refreshButton = document.getElementById("meeting-detail-refresh-button");
    if (!refreshButton) {
        return;
    }
    refreshButton.addEventListener("click", () => {
        loadMeetingDetail();
    });
    loadMeetingDetail();
}

document.addEventListener("DOMContentLoaded", () => {
    bindMeetingsListPage();
    bindMeetingCreatePage();
    bindMeetingDetailPage();
});
