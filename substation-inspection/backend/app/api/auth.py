from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_password, create_access_token, get_password_hash
from ..models.user import User
from ..schemas.auth import LoginRequest, TokenResponse, UserResponse
from ..schemas.common import ResponseModel

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ResponseModel[TokenResponse])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return ResponseModel(data=TokenResponse(access_token=token))


@router.get("/userinfo", response_model=ResponseModel[UserResponse])
def get_user_info(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseModel(data=UserResponse.model_validate(user))
