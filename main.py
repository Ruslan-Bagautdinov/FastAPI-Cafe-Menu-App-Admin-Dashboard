from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware

# Own imports
from app.database.postgre_db import init_db
# Routers
from app.routers.auth import router as auth_router
from app.routers.dishes import router as dishes_router
from app.routers.emails import router as emails_router
from app.routers.image import router as image_router
from app.routers.restaurants import router as restaurants_router
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for the FastAPI application lifespan.
    Initializes the database connection on startup.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    await init_db()
    yield


# Application description
app_description = """
FastAPI Admin Dashboard is a backend service for a React app, providing an admin dashboard for the cafe app.
It allows users to login as a superuser (admin) or a cafe owner (user). Users can manage their cafe profiles, dishes, and passwords.
Superusers can manage all cafes and users.

## Features

- **Authentication**: Login as a superuser or user.
- **User Management**: View, add, and edit user profiles.
- **Restaurant Management**: View, add, and edit cafe profiles.
- **Dish Management**: View, add, and edit dishes for cafes.
- **Password Management**: Change or reset passwords.
- **Email Operations**: Retrieve emails for password resets.
- **Image Operations**: Manage images related to cafes and dishes.
"""

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI Admin Dashboard",
    description=app_description,
    version="1.0.0",
    contact={
        "name": "Developer Name",
        "url": "https://github.com/yourusername/fastapi-admin-dashboard",
        "email": "developer@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api/users", tags=["superuser operations"])
app.include_router(restaurants_router, prefix="/api/restaurants", tags=["restaurant operations"])
app.include_router(emails_router, prefix="/api/emails", tags=["password and email operations"])
app.include_router(dishes_router, prefix="/api/dishes", tags=["dishes operations"])
app.include_router(image_router, prefix="/api/images", tags=["image operations"])


@app.get("/")
async def root():
    """
    Root endpoint that redirects to the API documentation.

    Returns:
        RedirectResponse: Redirects to the '/docs' endpoint.
    """
    return RedirectResponse(url='/docs')
