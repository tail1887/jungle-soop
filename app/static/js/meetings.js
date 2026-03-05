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

let listSortState = { sort: "latest", order: "desc" };
/** "open" | "closed" — 필터 버튼이 모집중이면 open, 마감됨이면 closed */
let listFilterStatus = "open";

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

function decodeJwtPayload(token) {
    if (!token) {
        return null;
    }
    const parts = token.split(".");
    if (parts.length < 2) {
        return null;
    }
    try {
        const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
        const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
        const decoded = atob(padded);
        return JSON.parse(decoded);
    } catch (_error) {
        return null;
    }
}

function getCurrentUserId() {
    const token = getAccessToken();
    const payload = decodeJwtPayload(token);
    return payload?.user_id ? String(payload.user_id) : "";
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

function toDatetimeLocalValue(value) {
    if (!value) {
        return "";
    }
    const normalized = String(value);
    if (normalized.length >= 16) {
        return normalized.slice(0, 16);
    }
    return normalized;
}

/** Returns current local time as YYYY-MM-DDTHH:mm for datetime-local min attribute (현재 시간 이후만 허용). */
function getDatetimeLocalMin() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    const h = String(d.getHours()).padStart(2, "0");
    const min = String(d.getMinutes()).padStart(2, "0");
    return `${y}-${m}-${day}T${h}:${min}`;
}

async function fetchJson(url, options) {
    const token = getAccessToken();
    const requestOptions = options || {};
    const mergedHeaders = { ...(requestOptions.headers || {}) };
    if (token) {
        mergedHeaders.Authorization = `Bearer ${token}`;
    }
    const response = await fetch(url, {
        ...requestOptions,
        headers: mergedHeaders,
        credentials: "include",
    });
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
    const deadlineAt = pickFirst(meeting.deadline_at, meeting.deadline, scheduledAt);
    const count = meeting.participant_count ?? 0;
    const maxCapacity = pickFirst(meeting.max_capacity, meeting.capacity, "-");
    const status = meeting.status || "open";

    li.innerHTML = `
        <a href="/meetings/${id}">
            <strong>${title}</strong>
        </a>
        <p>${place} · ${scheduledAt}</p>
        <p>마감 ${deadlineAt} · 참여 ${count}/${maxCapacity} · 상태 ${status}</p>
    `;
    return li;
}

async function loadMeetingsList(opts) {
    const listElement = document.getElementById("meetings-list");
    const messageElement = document.getElementById("meetings-list-message");
    if (!listElement || !messageElement) {
        return;
    }

    const sort = opts?.sort ?? listSortState.sort;
    const order = opts?.order ?? listSortState.order;
    listSortState = { sort, order };
    const statusFilter = opts?.status ?? listFilterStatus;
    listFilterStatus = statusFilter;

    setUiMessage(messageElement, "모임 목록을 불러오는 중...", "");
    listElement.innerHTML = "";
    try {
        const params = new URLSearchParams({
            page: "1",
            limit: String(DEFAULT_LIMIT),
            sort,
            order,
            status: statusFilter,
        });
        const result = await fetchJson(`/api/v1/meetings?${params}`);
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
        } else {
            meetings.forEach((meeting) => {
                listElement.appendChild(createMeetingListItem(meeting));
            });
            const total = result.data?.data?.pagination?.total ?? meetings.length;
            setUiMessage(messageElement, `모임 목록을 불러왔습니다. (총 ${total}건)`, "success");
        }
    } catch (_error) {
        setUiMessage(messageElement, "네트워크 오류로 목록을 불러오지 못했습니다.", "error");
    }

    updateListToolbarButtons();
}

function updateListToolbarButtons() {
    const filterBtn = document.getElementById("meetings-filter-status");
    const sortBtn = document.getElementById("meetings-sort-latest");
    if (filterBtn) {
        filterBtn.textContent = listFilterStatus === "open" ? "모집중" : "마감됨";
        filterBtn.classList.add("is-active");
        filterBtn.setAttribute("aria-label", listFilterStatus === "open" ? "모집중 필터 (클릭 시 마감됨)" : "마감됨 필터 (클릭 시 모집중)");
    }
    if (sortBtn) {
        sortBtn.classList.add("is-active");
        sortBtn.textContent = `최신순 ${listSortState.order === "desc" ? "▼" : "▲"}`;
    }
}

function bindMeetingsListPage() {
    const refreshButton = document.getElementById("meetings-refresh-button");
    if (refreshButton) {
        refreshButton.addEventListener("click", () => {
            loadMeetingsList();
        });
    }

    const filterBtn = document.getElementById("meetings-filter-status");
    if (filterBtn) {
        filterBtn.addEventListener("click", () => {
            listFilterStatus = listFilterStatus === "open" ? "closed" : "open";
            loadMeetingsList();
        });
    }

    const sortBtn = document.getElementById("meetings-sort-latest");
    if (sortBtn) {
        sortBtn.addEventListener("click", () => {
            listSortState.order = listSortState.order === "desc" ? "asc" : "desc";
            loadMeetingsList();
        });
    }

    updateListToolbarButtons();
    loadMeetingsList();
}

function parseCreateFormPayload(form) {
    const rawMaxCapacity = readFormField(form, ["max_capacity", "capacity"]);
    const scheduledAt = readFormField(form, ["scheduled_at", "datetime"]).trim();
    const deadlineAtInput = readFormField(form, ["deadline_at", "deadline"]).trim();
    return {
        title: readFormField(form, ["title"]).trim(),
        scheduled_at: scheduledAt,
        deadline_at: deadlineAtInput || scheduledAt,
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
    const now = Date.now();
    const scheduledAtTs = Date.parse(payload.scheduled_at);
    const deadlineAtTs = Date.parse(payload.deadline_at) || scheduledAtTs;
    if (Number.isNaN(scheduledAtTs)) {
        return "모임 일시 형식이 올바르지 않습니다.";
    }
    if (scheduledAtTs <= now) {
        return "모임 일시는 현재 시간 이후로 설정해주세요.";
    }
    if (!Number.isNaN(deadlineAtTs) && deadlineAtTs <= now) {
        return "마감 기한은 현재 시간 이후로 설정해주세요.";
    }
    if (!Number.isNaN(deadlineAtTs) && deadlineAtTs >= scheduledAtTs) {
        return "마감 기한은 모임 일시보다 이전이어야 합니다.";
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

    const scheduledInput = form.elements.namedItem("scheduled_at");
    const deadlineInput = form.elements.namedItem("deadline_at");
    if (scheduledInput) {
        scheduledInput.min = getDatetimeLocalMin();
    }
    if (deadlineInput) {
        deadlineInput.min = getDatetimeLocalMin();
        scheduledInput.addEventListener("change", function () {
            if (scheduledInput.value) {
                deadlineInput.max = scheduledInput.value;
            } else {
                deadlineInput.removeAttribute("max");
            }
        });
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
    const deadlineAt = pickFirst(meeting.deadline_at, meeting.deadline, scheduledAt);
    const count = meeting.participant_count ?? 0;
    const maxCapacity = pickFirst(meeting.max_capacity, meeting.capacity, "-");
    const status = meeting.status || "open";
    metaEl.textContent = `${place} · 일정 ${scheduledAt} · 마감 ${deadlineAt} · 참여 ${count}/${maxCapacity} · 상태 ${status}`;
    descEl.textContent = meeting.description || "설명이 없습니다.";
}

function renderMeetingParticipants(participants) {
    const listEl = document.getElementById("meeting-participants-list");
    const emptyEl = document.getElementById("meeting-participants-empty");
    if (!listEl || !emptyEl) {
        return;
    }

    listEl.innerHTML = "";
    const normalized = Array.isArray(participants) ? participants : [];
    if (normalized.length === 0) {
        emptyEl.textContent = "아직 참여자가 없습니다.";
        return;
    }

    emptyEl.textContent = "";
    normalized.forEach((participantId) => {
        const li = document.createElement("li");
        li.textContent = String(participantId);
        listEl.appendChild(li);
    });
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

let currentMeetingDetail = null;

function updateCloseButtonState(meeting) {
    const closeButton = document.getElementById("meeting-close-button");
    if (!closeButton) return;
    const status = meeting?.status || "open";
    const deadlineAt = meeting?.deadline_at || meeting?.scheduled_at;
    if (status === "open") {
        closeButton.textContent = "조기마감";
        closeButton.disabled = false;
        closeButton.dataset.action = "close";
        setButtonVisible(closeButton, true);
        return;
    }
    if (status === "closed") {
        const deadlinePassed = deadlineAt ? Date.now() >= Date.parse(deadlineAt) : true;
        if (deadlinePassed) {
            setButtonVisible(closeButton, false);
            return;
        }
        closeButton.textContent = "조기마감 취소";
        closeButton.disabled = false;
        closeButton.dataset.action = "cancel";
        setButtonVisible(closeButton, true);
    }
}

function bindOwnerActions(meetingId, messageElement) {
    const editButton = document.getElementById("meeting-edit-button");
    const closeButton = document.getElementById("meeting-close-button");
    const deleteButton = document.getElementById("meeting-delete-button");
    if (editButton) {
        editButton.addEventListener("click", () => {
            window.location.href = `/meetings/${meetingId}/edit`;
        });
    }
    if (closeButton) {
        closeButton.addEventListener("click", async () => {
            const action = closeButton.dataset.action;
            const isClosing = action === "close";
            closeButton.disabled = true;
            setUiMessage(
                messageElement,
                isClosing ? "모임을 조기마감하는 중..." : "조기마감 취소하는 중...",
                ""
            );
            try {
                const result = await fetchJson(`/api/v1/meetings/${meetingId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: isClosing ? "closed" : "open" }),
                });
                if (!result.ok) {
                    setUiMessage(
                        messageElement,
                        formatApiError(
                            result,
                            isClosing ? "조기마감에 실패했습니다." : "조기마감 취소에 실패했습니다."
                        ),
                        "error"
                    );
                    return;
                }
                await loadMeetingDetail({ skipSuccessMessage: true });
                setUiMessage(
                    messageElement,
                    isClosing ? "모임이 조기마감되었습니다." : "조기마감이 취소되었습니다.",
                    "success"
                );
            } catch (_error) {
                setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
            } finally {
                closeButton.disabled = false;
            }
        });
    }
    if (deleteButton) {
        deleteButton.addEventListener("click", async () => {
            if (!window.confirm("이 모임을 삭제하시겠습니까?")) {
                return;
            }
            deleteButton.disabled = true;
            setUiMessage(messageElement, "모임을 삭제하는 중...", "");
            try {
                const result = await fetchJson(`/api/v1/meetings/${meetingId}`, { method: "DELETE" });
                if (result.status === 204 || result.ok) {
                    setUiMessage(messageElement, "모임이 삭제되었습니다. 목록으로 이동합니다.", "success");
                    window.location.href = "/meetings";
                    return;
                }
                setUiMessage(messageElement, formatApiError(result, "모임 삭제에 실패했습니다."), "error");
            } catch (_error) {
                setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
            } finally {
                deleteButton.disabled = false;
            }
        });
    }
}

function setButtonVisible(element, visible) {
    if (!element) {
        return;
    }
    element.style.display = visible ? "" : "none";
}

function applyDetailActionVisibility(meeting) {
    const currentUserId = getCurrentUserId();
    const authorId = String(meeting.author_id || "");
    const isAuthor = Boolean(currentUserId) && currentUserId === authorId;

    const editButton = document.getElementById("meeting-edit-button");
    const closeButton = document.getElementById("meeting-close-button");
    const deleteButton = document.getElementById("meeting-delete-button");
    const joinButton = document.getElementById("meeting-join-button");
    const cancelButton = document.getElementById("meeting-cancel-button");

    setButtonVisible(editButton, isAuthor);
    setButtonVisible(closeButton, isAuthor);
    setButtonVisible(deleteButton, isAuthor);
    setButtonVisible(joinButton, !isAuthor);
    setButtonVisible(cancelButton, !isAuthor);
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
            await loadMeetingDetail({ skipSuccessMessage: true });
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
            await loadMeetingDetail({ skipSuccessMessage: true });
            setUiMessage(messageElement, result.data?.message || "모임 참여가 취소되었습니다.", "success");
        } catch (_error) {
            setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            setActionBusy(false);
        }
    });
}

async function loadMeetingDetail(options) {
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
        currentMeetingDetail = meeting;
        root.dataset.maxCapacity = String(pickFirst(meeting.max_capacity, meeting.capacity, "-"));
        root.dataset.metaPrefix = `${pickFirst(meeting.place, meeting.location, "장소 미정")} · 일정 ${pickFirst(meeting.scheduled_at, meeting.datetime, meeting.time, "일시 미정")} · 마감 ${pickFirst(meeting.deadline_at, meeting.deadline, meeting.scheduled_at, meeting.datetime, meeting.time, "일시 미정")}`;
        setMeetingDetail(meeting);
        renderMeetingParticipants(meeting.participants);
        applyDetailActionVisibility(meeting);
        updateCloseButtonState(meeting);
        if (!options?.skipSuccessMessage) {
            setUiMessage(messageElement, "모임 상세를 불러왔습니다.", "success");
        }
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
        bindOwnerActions(meetingId, messageElement);
        bindMeetingJoinActions(meetingId, messageElement);
    }
    loadMeetingDetail();
}

function bindMeetingEditPage() {
    const root = document.getElementById("meeting-edit-root");
    const form = document.getElementById("meeting-edit-form");
    const messageElement = document.getElementById("meeting-edit-message");
    const submitButton = document.getElementById("meeting-edit-submit-button");
    const meetingId = root?.dataset.meetingId;
    if (!root || !form || !messageElement || !meetingId) {
        return;
    }

    const fillForm = (meeting) => {
        const titleField = form.elements.namedItem("title");
        const scheduledAtField = form.elements.namedItem("scheduled_at");
        const deadlineAtField = form.elements.namedItem("deadline_at");
        const placeField = form.elements.namedItem("place");
        const descriptionField = form.elements.namedItem("description");
        const maxCapacityField = form.elements.namedItem("max_capacity");
        if (titleField && "value" in titleField) titleField.value = meeting.title || "";
        if (scheduledAtField && "value" in scheduledAtField) scheduledAtField.value = toDatetimeLocalValue(meeting.scheduled_at || "");
        if (deadlineAtField && "value" in deadlineAtField) deadlineAtField.value = toDatetimeLocalValue(meeting.deadline_at || meeting.scheduled_at || "");
        if (placeField && "value" in placeField) placeField.value = meeting.place || "";
        if (descriptionField && "value" in descriptionField) descriptionField.value = meeting.description || "";
        if (maxCapacityField && "value" in maxCapacityField) maxCapacityField.value = String(meeting.max_capacity || 4);
        const minVal = getDatetimeLocalMin();
        if (scheduledAtField) scheduledAtField.min = minVal;
        if (deadlineAtField) {
            deadlineAtField.min = minVal;
            if (scheduledAtField && scheduledAtField.value) deadlineAtField.max = scheduledAtField.value;
        }
    };

    const scheduledInput = form.elements.namedItem("scheduled_at");
    const deadlineInput = form.elements.namedItem("deadline_at");
    if (scheduledInput && deadlineInput) {
        scheduledInput.addEventListener("change", function () {
            if (scheduledInput.value) {
                deadlineInput.max = scheduledInput.value;
            } else {
                deadlineInput.removeAttribute("max");
            }
        });
    }

    const loadForEdit = async () => {
        setUiMessage(messageElement, "수정할 모임 정보를 불러오는 중...", "");
        try {
            const result = await fetchJson(`/api/v1/meetings/${meetingId}`);
            if (!result.ok) {
                setUiMessage(messageElement, formatApiError(result, "모임 정보를 불러오지 못했습니다."), "error");
                return;
            }
            fillForm(result.data?.data || {});
            setUiMessage(messageElement, "모임 정보를 불러왔습니다.", "success");
        } catch (_error) {
            setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
        }
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = parseCreateFormPayload(form);
        const validationMessage = validateCreateForm(payload);
        if (validationMessage) {
            setUiMessage(messageElement, validationMessage, "error");
            return;
        }

        submitButton.disabled = true;
        setUiMessage(messageElement, "모임 수정 요청 중...", "");
        try {
            const result = await fetchJson(`/api/v1/meetings/${meetingId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!result.ok) {
                if (result.status === 401) {
                    setUiMessage(messageElement, "로그인이 필요합니다. 로그인 페이지로 이동합니다.", "error");
                    window.location.href = "/login";
                    return;
                }
                setUiMessage(messageElement, formatApiError(result, "모임 수정에 실패했습니다."), "error");
                return;
            }
            setUiMessage(messageElement, "모임이 수정되었습니다. 상세 페이지로 이동합니다.", "success");
            window.location.href = `/meetings/${meetingId}`;
        } catch (_error) {
            setUiMessage(messageElement, "네트워크 오류가 발생했습니다.", "error");
        } finally {
            submitButton.disabled = false;
        }
    });

    loadForEdit();
}

function initMeetingsPage() {
    bindMeetingsListPage();
    bindMeetingCreatePage();
    bindMeetingDetailPage();
    bindMeetingEditPage();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMeetingsPage);
} else {
    initMeetingsPage();
}
})();
