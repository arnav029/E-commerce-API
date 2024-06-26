from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
from dotenv import dotenv_values
from models import User
from fastapi import status
import jwt

config_credential = dotenv_values(".env")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UnauthorizedUpdate(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_hashed_password(password):
    return pwd_context.hash(password)


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user = await User.get(id=payload.get("id"))


    except:
        return UnauthorizedUpdate(detail="Invalid token", status_code=status.HTTP_403_FORBIDDEN)

    return user


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username, password):
    user = await User.get(username=username)

    if user and await verify_password(password, user.password):
        return user
    return False


async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}

        )

    token_data = {
        "id": user.id,
        "username": user.username
    }

    token = jwt.encode(token_data, config_credential['SECRET'])

    return token
