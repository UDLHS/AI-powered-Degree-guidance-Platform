from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth_routes, profile_routes, recommendation_routes, university_routes, admin_routes


app = FastAPI(
    title="AI Degree Guidance API",
    version="1.0.0",
    description="Backend API for Sri Lankan A/L degree recommendation platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Degree Guidance backend is running"
    }


app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(profile_routes.router, prefix="/api/profiles", tags=["Academic Profiles"])
app.include_router(recommendation_routes.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(university_routes.router, prefix="/api/universities", tags=["Universities"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])