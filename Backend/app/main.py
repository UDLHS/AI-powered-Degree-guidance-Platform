from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    auth_routes,
    profile_routes,
    recommendation_routes,
    university_routes,
    admin_routes,
    dashboard_routes
)

app = FastAPI(
    title="AI Degree Guidance API",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.56.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(profile_routes.router, prefix="/api/profiles", tags=["Academic Profiles"])
app.include_router(recommendation_routes.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(university_routes.router, prefix="/api/universities", tags=["Universities"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])


@app.get("/")
def root():
    return {"message": "AI Degree Guidance API is running"}