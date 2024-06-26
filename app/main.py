from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# own_import
from app.database.postgre_db import init_db

# routers
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.get_all_users import router as get_all_users_router
from app.routers.approve_user import router as approve_user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(register_router, prefix="/api/register")
app.include_router(login_router, prefix="/api/login")
app.include_router(get_all_users_router, prefix="/api/get_all_users")
app.include_router(approve_user_router, prefix="/api/approve_user")


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')

