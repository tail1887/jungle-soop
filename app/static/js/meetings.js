(function () {
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
const DEFAULT_LIMIT = 10;

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

function formatApiError(result, fallbackMessage) {
    return result?.data?.error?.message || fallbackMessage;
}

function pickFirst(...values) {
    for (const value of values) {
        if (value !== undefined && value !== null && value !== "") {
            return value;
        }
    }
    return "";
}

function parseMeetingItems(resultData) {
    return (
        resultData?.data?.items
        || resultData?.data?.meetings
        || resultData?.meetings
        || []
    );
}

function readFormField(form, names) {
    for (const name of names) {
        const field = form.elements.namedItem(name);
        if (field && "value" in field) {
            return field.value;
        }
    }
    return "";
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

function createMeetingListItem(meeting) {
    const li = document.createElement("li");
    li.className = "meeting-item";
    const id = meeting.meeting_id || "unknown";
    const title = meeting.title || "제목 없음";
    const place = pickFirst(meeting.place, meeting.location, "장소 미정");
    const scheduledAt = pickFirst(meeting.scheduled_at, meeting.datetime, meeting.time, "일시 미정");
    const count = meeting.participant_count ?? 0;
    const maxCapacity = pickFirst(meeting.max_capacity, meeting.capacity, "-");
    const status = meeting.status || "open";

    li.innerHTML = `
        <a href="/meetings/${id}">
            <strong>${title}</strong>
        </a>
        <p>${place} · ${scheduledAt}</p>
        <p>참여 ${count}/${maxCapacity} · 상태 ${status}</p>
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
    try {
        const result = await fetchJson(`/api/v1/meetings?page=1&limit=${DEFAULT_LIMIT}&sort=latest`);
        if (!result.ok) {
            setUiMessage(
                messageElement,
                formatApiError(result, "모임 목록을 불러오지 못했습니다."),
                "error"
            );
            return;
        }

        const meetings = parseMeetingItems(result.data);
        if (meetings.length === 0) {
            setUiMessage(messageElement, "등록된 모임이 없습니다.", "");
            return;
        }

        meetings.forEach((meeting) => {
            listElement.appendChild(createMeetingListItem(meeting));
        });
        const total = result.data?.data?.pagination?.total ?? meetings.length;
        setUiMessage(messageElement, `모임 목록을 불러왔습니다. (총 ${total}건)`, "success");
    } catch (_error) {
        setUiMessage(messageElement, "네트워크 오류로 목록을 불러오지 못했습니다.", "error");
    }
}

function bindMeetingsListPage() {
    const refreshButton = document.getElementById("meetings-refresh-button");
    if (refreshButton) {
        refreshButton.addEventListener("click", () => {
            loadMeetingsList();
        });
    }
    loadMeetingsList();
}

function parseCreateFormPayload(form) {
    const rawMaxCapacity = readFormField(form, ["max_capacity", "capacity"]);
    return {
        title: readFormField(form, ["title"]).trim(),
        scheduled_at: readFormField(form, ["scheduled_at", "datetime"]).trim(),
        place: readFormField(form, ["place", "location"]).trim(),
        description: readFormField(form, ["description"]).trim(),
        max_capacity: Number(rawMaxCapacity),
    };
}

function validateCreateForm(payload) {
    if (!payload.title || !payload.scheduled_at || !payload.place || Number.isNaN(payload.max_capacity)) {
        return "제목, 일시, 장소, 모집 인원을 입력해주세요.";
    }
    if (payload.max_capacity < 2 || payload.max_capacity > 20) {
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
        let payload;
        try {
            payload = parseCreateFormPayload(form);
        } catch (_error) {
            setUiMessage(messageElement, "입력값을 읽는 중 오류가 발생했습니다. 페이지를 새로고침해주세요.", "error");
            return;
        }
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
                setUiMessage(
                    messageElement,
                    formatApiError(result, "모임 생성 요청이 실패했습니다."),
                    "error"
                );
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
    const place = pickFirst(meeting.place, meeting.location, "장소 미정");
    const scheduledAt = pickFirst(meeting.scheduled_at, meeting.datetime, meeting.time, "일시 미정");
    const count = meeting.participant_count ?? 0;
    const maxCapacity = pickFirst(meeting.max_capacity, meeting.capacity, "-");
    const status = meeting.status || "open";
    metaEl.textContent = `${place} · ${scheduledAt} · 참여 ${count}/${maxCapacity} · 상태 ${status}`;
    descEl.textContent = meeting.description || "설명이 없습니다.";
}

function updateMeetingDetailCounters(detailData) {
    const root = document.getElementById("meeting-detail-root");
    const metaEl = document.getElementById("meeting-detail-meta");
    if (!root || !metaEl) {
        return;
    }
    const baseMeta = root.dataset.metaPrefix || "정보";
    const maxCapacity = root.dataset.maxCapacity || "-";
    const participantCount = detailData.participant_count ?? 0;
    const status = detailData.status || "open";
    metaEl.textContent = `${baseMeta} · 참여 ${participantCount}/${maxCapacity} · 상태 ${status}`;
}

async function requestJoinAction(meetingId, method) {
    return fetchJson(`/api/v1/meetings/${meetingId}/join`, { method });
}

function bindMeetingJoinActions(meetingId, messageElement) {
    const joinButton = document.getElementById("meeting-join-button");
    const cancelButton = document.getElementById("meeting-cancel-button");
    if (!joinButton || !cancelButton) {
        return;
    }

    const setActionBusy = (busy) => {
        joinButton.disabled = busy;
        cancelButton.disabled = busy;
    };

    joinButton.addEventListener("click", async () => {
        setActionBusy(true);
        setUiMessage(messageElement, "모임 참여 요청 중...", "");
        try {
            const result = await requestJoinAction(meetingId, "POST");
            if (!result.ok) {
                setUiMessage(messageElement, formatApiError(result, "모임 참여에 실패했습니다."), "error");
                return;
            }
            updateMeetingDetailCounters(result.data?.data || {});
            setUiMessage(messageElement, result.data?.message || "모임 참여가 완료되었습니다.", "success");
        } catch (_error) {
            setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            setActionBusy(false);
        }
    });

    cancelButton.addEventListener("click", async () => {
        setActionBusy(true);
        setUiMessage(messageElement, "모임 참여 취소 요청 중...", "");
        try {
            const result = await requestJoinAction(meetingId, "DELETE");
            if (!result.ok) {
                setUiMessage(messageElement, formatApiError(result, "모임 참여 취소에 실패했습니다."), "error");
                return;
            }
            updateMeetingDetailCounters(result.data?.data || {});
            setUiMessage(messageElement, result.data?.message || "모임 참여가 취소되었습니다.", "success");
        } catch (_error) {
            setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            setActionBusy(false);
        }
    });
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
            setUiMessage(messageElement, formatApiError(result, "모임 상세를 불러오지 못했습니다."), "error");
            return;
        }

        const meeting = result.data?.data || {};
        root.dataset.maxCapacity = String(pickFirst(meeting.max_capacity, meeting.capacity, "-"));
        root.dataset.metaPrefix = `${pickFirst(meeting.place, meeting.location, "장소 미정")} · ${pickFirst(meeting.scheduled_at, meeting.datetime, meeting.time, "일시 미정")}`;
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
    const meetingId = document.getElementById("meeting-detail-root")?.dataset.meetingId;
    const messageElement = document.getElementById("meeting-detail-message");
    if (meetingId && messageElement) {
        bindMeetingJoinActions(meetingId, messageElement);
    }
    loadMeetingDetail();
}

function initMeetingsPage() {
    bindMeetingsListPage();
    bindMeetingCreatePage();
    bindMeetingDetailPage();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMeetingsPage);
} else {
    initMeetingsPage();
}
})();
