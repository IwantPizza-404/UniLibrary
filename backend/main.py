from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.api.v1 import users, auth, posts, categories, user_follow
from app.core.config import settings
from app.database.models import Base
from admin.config import setup_admin

engine = create_async_engine(settings.DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your existing routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(user_follow.router, prefix="/api/v1/user_follow", tags=["User Follow"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Setup SQLAdmin
setup_admin(app, engine)
