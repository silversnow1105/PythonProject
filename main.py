# main.py (FastAPI 서버 코드)


from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import json
import os
from datetime import datetime
# --- 상수 및 유틸리티 함수 (기존 코드에서 가져옴) ---
USERS_FILE = "users.json"
ADMIN_PASSWORD = "1105" # 관리자 비밀번호는 여기에 직접 정의합니다.
NOTICE_FILE = "notice.json"
BOARD_FILE = "board.json"



def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_notice():
    if not os.path.exists(NOTICE_FILE):
        return {}
    with open(NOTICE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_notice(data):
    with open(NOTICE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_board():
    if not os.path.exists(BOARD_FILE):
        return {"posts": []}
    with open(BOARD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_board(data):
    with open(BOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
# --- 상수 및 유틸리티 함수 끝 ---

app = FastAPI()

# Pydantic 모델: 클라이언트로부터 받을 데이터의 유효성을 검사합니다.
class UserCreate(BaseModel):
    username: str
    password: str
    admin_password_attempt: str | None = None # 관리자 등록 시도 시 비밀번호

class UserLogin(BaseModel):
    username: str
    password: str

class UserApproval(BaseModel):
    username: str
    admin_password: str

class Notice(BaseModel):
    date: str
    content: str

class Post(BaseModel):
    title: str
    content: str
    author: str

class Comment(BaseModel):
    post_id: int
    comment: str
    author: str

class Like(BaseModel):
    post_id: int
    user: str

@app.post("/register")
async def register_user(user: UserCreate):
    """
    새로운 사용자를 등록합니다.
    """
    users = load_users()

    if user.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 아이디입니다."
        )

    admin_count = sum(1 for u in users.values() if u["role"] == "admin")
    role = "admin" if admin_count == 0 else "member" # 최초 가입자는 관리자

    # 일반 회원이 관리자 등록을 시도하는 경우 (선택적)
    if role == "member" and user.admin_password_attempt:
        if user.admin_password_attempt == ADMIN_PASSWORD:
            role = "admin"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="관리자 비밀번호가 틀렸습니다."
            )

    users[user.username] = {
        "password": user.password, # 실제 서비스에서는 비밀번호를 해싱해야 합니다!
        "role": role,
        "approved": True if role == "admin" else False # 관리자는 즉시 승인, 멤버는 대기
    }
    save_users(users)

    if role == "member":
        return {"message": "회원가입 완료, 관리자의 승인을 기다려주세요."}
    else:
        return {"message": "관리자 회원가입 완료."}

@app.post("/login")
async def login_user(user: UserLogin):
    """
    사용자를 인증합니다.
    """
    users = load_users()
    stored_user = users.get(user.username)

    if not stored_user or stored_user["password"] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 틀렸습니다."
        )

    if stored_user["role"] == "member" and not stored_user.get("approved", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자의 승인을 기다려주세요."
        )

    return {"message": "로그인 성공", "username": user.username, "role": stored_user["role"]}

@app.post("/approve_user")
async def approve_user(approval_request: UserApproval):
    """
    관리자가 회원을 승인합니다.
    """
    if approval_request.admin_password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 비밀번호가 틀렸습니다."
        )

    users = load_users()
    user_to_approve = users.get(approval_request.username)

    if not user_to_approve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    if user_to_approve["role"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="관리자 계정은 승인이 필요 없습니다."
        )
    if user_to_approve.get("approved", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 승인된 사용자입니다."
        )

    user_to_approve["approved"] = True
    save_users(users)
    return {"message": f"{approval_request.username}님이 승인되었습니다."}

@app.get("/pending_approvals")
async def get_pending_approvals():
    """
    승인 대기 중인 사용자 목록을 가져옵니다.
    """
    users = load_users()
    pending = []
    for uid, info in users.items():
        if info["role"] == "member" and not info.get("approved", False):
            pending.append(uid)
    return {"pending_users": pending}

@app.get("/notices")
async def get_notices():
    return load_notice()

@app.post("/notices")
async def post_notice(notice: Notice):
    data = load_notice()
    data[notice.date] = notice.content
    save_notice(data)
    return {"message": f"{notice.date} 공지가 등록되었습니다."}

@app.get("/posts")
async def get_posts():
    return load_board()


@app.post("/posts")
async def create_post(post: Post):
    data = load_board()

    # ✅ "posts" 키가 없으면 초기화
    if "posts" not in data:
        data["posts"] = []

    data["posts"].append({
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "likes": [],
        "comments": []
    })
    save_board(data)
    return {"message": "게시글이 등록되었습니다."}


@app.post("/posts/comment")
async def add_comment(comment: Comment):
    data = load_board()
    try:
        post = data["posts"][comment.post_id]
        post["comments"].append({
            "author": comment.author,
            "comment": comment.comment,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_board(data)
        return {"message": "댓글이 등록되었습니다."}
    except IndexError:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

@app.post("/posts/like")
async def like_post(like: Like):
    data = load_board()
    try:
        post = data["posts"][like.post_id]
        if like.user in post["likes"]:
            raise HTTPException(status_code=400, detail="이미 좋아요를 눌렀습니다.")
        post["likes"].append(like.user)
        save_board(data)
        return {"message": "좋아요가 추가되었습니다."}
    except IndexError:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
