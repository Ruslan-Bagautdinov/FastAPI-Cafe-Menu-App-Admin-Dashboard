from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer

from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# own_import
from app.database.postgre_db import init_db

# routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.restaurants import router as restaurants_router
from app.routers.emails import router as emails_router
from app.routers.dishes import router as dishes_router
from app.routers.image import router as image_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

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
    return RedirectResponse(url='/docs')

