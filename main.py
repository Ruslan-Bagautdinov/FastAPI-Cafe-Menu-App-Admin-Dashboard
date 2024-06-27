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
app.include_router(users_router, prefix="/api/users", tags=["user operations"])
app.include_router(restaurants_router, prefix="/api/restaurants", tags=["restaurant operations"])


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')


# @app_cafe_admin.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html(credentials: HTTPAuthorizationCredentials = Security(security)):
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title=app.title + " - Swagger UI",
#         oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
#         swagger_js_url="/static/swagger-ui-bundle.js",
#         swagger_css_url="/static/swagger-ui.css",
#     )
