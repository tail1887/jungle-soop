from typing import Optional
from urllib.parse import quote

from bson import ObjectId
from flask import current_app

from app.db import get_database


def _build_default_avatar_url(user_id: str, nickname: str | None) -> str:
    seed = quote(nickname or user_id or "jungle-soop")
    return f"https://api.dicebear.com/9.x/identicon/svg?seed={seed}"


def get_public_user_profile(user_id: str) -> Optional[dict]:
    """
    주어진 user_id에 대한 공개 프로필 정보 조회.

    반환:
      - 성공 시: {"id": str, "email": str | None, "nickname": str | None, "profile_image_url": str}
      - 실패 시: None (잘못된 ObjectId이거나 문서 없음)
    비밀번호(password)는 절대 포함하지 않는다.
    """
    db = get_database(current_app)

    try:
        oid = ObjectId(user_id)
    except Exception:
        return None

    doc = db.users.find_one(
        {"_id": oid},
        projection={"email": 1, "nickname": 1, "profile_image_url": 1},  # 민감정보는 가져오지 않음
    )
    if not doc:
        return None

    return {
        "id": str(doc["_id"]),
        "email": doc.get("email"),
        "nickname": doc.get("nickname"),
        "profile_image_url": doc.get("profile_image_url")
        or _build_default_avatar_url(str(doc["_id"]), doc.get("nickname")),
    }