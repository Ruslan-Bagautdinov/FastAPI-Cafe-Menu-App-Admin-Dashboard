from fastapi import HTTPException, status, APIRouter, Depends
import smtplib
from email.message import EmailMessage
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import random
import string

# Own imports
from app.database.postgre_db import get_session
from app.utils.security import get_password_hash, get_current_user, verify_password
from app.database.models import User, ResetToken
from app.database.schemas import ChangePasswordRequest, PasswordResetRequest, EmailRequest
from app.config import HOME_EMAIL
from app.config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, WORK_SERVER_HOST, WORK_SERVER_PORT
from app.config import LOCAL_SMTP_SERVER, LOCAL_SMTP_PORT, LOCAL_SENDER_EMAIL, LOCAL_SENDER_PASSWORD
from app.config import WORK_SMTP_SERVER, WORK_SMTP_PORT, WORK_SENDER_EMAIL, WORK_SENDER_PASSWORD

# Determine the SMTP server configuration based on the HOME_EMAIL flag
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
    """
    Send an email to the specified recipient.

    Args:
        subject (str): The subject of the email.
        recipient (str): The email address of the recipient.
        content (str): The content of the email.

    Raises:
        HTTPException: 500 Internal Server Error if an error occurs while sending the email.
    """
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


@router.post("/send-email/", description="Send an email to a specified recipient.")
async def send_email_endpoint(email_request: EmailRequest):
    """
    Send an email to a specified recipient.

    Args:
        email_request (EmailRequest): The request containing the recipient's email, subject, and message.

    Returns:
        dict: A message indicating the email was sent successfully.
    """
    await send_email(email_request.subject, email_request.recipient, email_request.message)
    return {"message": f"Email to {email_request.recipient} sent successfully"}


@router.post("/request-reset/", description="Request a password reset for a user.")
async def request_password_reset(password_reset_request: PasswordResetRequest, db: AsyncSession = Depends(get_session)):
    """
    Request a password reset for a user.

    Args:
        password_reset_request (PasswordResetRequest): The request containing the user's email.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A message indicating the password reset email was sent successfully.

    Raises:
        HTTPException: 404 Not Found if the user is not found.
    """
    email = password_reset_request.email
    token = secrets.token_urlsafe(32)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = ResetToken(token=token, user_id=user.id)
    db.add(reset_token)
    await db.commit()

    await send_email(
        subject="Password Reset Request",
        recipient=email,
        content=(f"Click the link to reset your password\n"
                 f"for your Food App account:\n "
                 f"http://{HOST}:{PORT}/api/emails/reset-password?token={token}")
    )
    return {"message": f"Password reset email sent to {email}"}


@router.get("/reset-password/", description="Reset a user's password using a valid token.")
async def reset_password(token: str, db: AsyncSession = Depends(get_session)):
    """
    Reset a user's password using a valid token.

    Args:
        token (str): The reset token.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A message indicating the new password was sent successfully.

    Raises:
        HTTPException: 400 Bad Request if the token is invalid or has expired.
        HTTPException: 404 Not Found if the user is not found.
    """
    result = await db.execute(select(ResetToken).where(ResetToken.token == token))
    reset_token = result.scalars().first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid token")

    if reset_token.expiry_time < datetime.utcnow():
        await db.delete(reset_token)
        await db.commit()
        raise HTTPException(status_code=400, detail="Token has expired")

    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    hashed_password = get_password_hash(new_password)

    user_id = reset_token.user_id
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hashed_password

    await db.delete(reset_token)

    await db.commit()

    await send_email(
        subject="Your New Password",
        recipient=user.email,
        content=f"Your new password is: {new_password}"
    )
    return {"message": f"New password sent to {user.email}"}


@router.post("/change_password", description="Change user password")
async def change_password(request: ChangePasswordRequest,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_session)):
    """
    Change the password of a user. Only the user themselves or a superuser can change the password.

    Args:
        request (ChangePasswordRequest): The request containing the email, old password, and new password.
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A message indicating the password was changed successfully.

    Raises:
        HTTPException: 403 Forbidden if the current user is not authorized to change the password.
        HTTPException: 404 Not Found if the user is not found.
        HTTPException: 400 Bad Request if the old password is incorrect or if the new password is the same as the old password.
    """
    if current_user.email != request.email and current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to change this password")

    query = select(User).filter(User.email == request.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(request.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    hashed_new_password = get_password_hash(request.new_password)
    user.hashed_password = hashed_new_password
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "Password changed successfully"}
