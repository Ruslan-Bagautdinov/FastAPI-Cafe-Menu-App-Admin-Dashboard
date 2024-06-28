from fastapi import HTTPException, APIRouter, Depends
import smtplib
from email.message import EmailMessage
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import random
import string


# own import
from app.database.postgre_db import get_session
from app.utils.security import get_password_hash
from app.database.models import User, ResetToken
from app.database.schemas import PasswordResetRequest, EmailRequest
from app.config import HOME_EMAIL
from app.config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, WORK_SERVER_HOST, WORK_SERVER_PORT
from app.config import LOCAL_SMTP_SERVER, LOCAL_SMTP_PORT, LOCAL_SENDER_EMAIL, LOCAL_SENDER_PASSWORD
from app.config import WORK_SMTP_SERVER, WORK_SMTP_PORT, WORK_SENDER_EMAIL, WORK_SENDER_PASSWORD


if HOME_EMAIL:
    HOST = LOCAL_SERVER_HOST
    PORT = LOCAL_SERVER_PORT
    SMTP_SERVER = LOCAL_SMTP_SERVER
    SMTP_PORT = LOCAL_SMTP_PORT
    SENDER_EMAIL = LOCAL_SENDER_EMAIL
    SENDER_PASSWORD = LOCAL_SENDER_PASSWORD
else:
    HOST = WORK_SERVER_HOST
    PORT = WORK_SERVER_PORT
    SMTP_SERVER = WORK_SMTP_SERVER
    SMTP_PORT = WORK_SMTP_PORT
    SENDER_EMAIL = WORK_SENDER_EMAIL
    SENDER_PASSWORD = WORK_SENDER_PASSWORD

router = APIRouter()


async def send_email(subject: str, recipient: str, content: str):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-email/")
async def send_email_endpoint(email_request: EmailRequest):
    await send_email(email_request.recipient, email_request.subject, email_request.message)
    return {"message": f"Email to {email_request.recipient} sent successfully"}


@router.post("/request-reset/")
async def request_password_reset(password_reset_request: PasswordResetRequest, session: AsyncSession = Depends(get_session)):
    email = password_reset_request.email
    token = secrets.token_urlsafe(32)

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = ResetToken(token=token, user_id=user.id)
    session.add(reset_token)
    await session.commit()

    await send_email(
        subject="Password Reset Request",
        recipient=email,
        content=(f"Click the link to reset your password\n"
                 f"for your Food App account:\n "
                 f"http://{HOST}:{PORT}/api/emails/reset-password?token={token}")
    )
    return {"message": f"Password reset email sent to {email}"}


@router.get("/reset-password/")
async def reset_password(token: str, session: AsyncSession = Depends(get_session)):

    result = await session.execute(select(ResetToken).where(ResetToken.token == token))
    reset_token = result.scalars().first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid token")

    if reset_token.expiry_time < datetime.utcnow():
        await session.delete(reset_token)
        await session.commit()
        raise HTTPException(status_code=400, detail="Token has expired")

    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    hashed_password = get_password_hash(new_password)

    user_id = reset_token.user_id
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hashed_password

    await session.delete(reset_token)

    await session.commit()

    await send_email(
        subject="Your New Password",
        recipient=user.email,
        content=f"Your new password is: {new_password}"
    )
    return {"message": f"New password sent to {user.email}"}
