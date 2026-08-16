from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import (
    auth_router, products_router, customers_router, cases_router,
    recommendations_router, inventory_router, sales_router, evidence_router,
)

# --- Safe Imports for Phase 1 Errors ---
try:
    from app.interface.errors import NotFoundError
except ImportError:
    NotFoundError = None

try:
    from app.interface.errors import ConsentError
except ImportError:
    ConsentError = None

try:
    from app.interface.errors import ValidationError
except ImportError:
    ValidationError = None

try:
    from app.interface.errors import ConflictError
except ImportError:
    ConflictError = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="HBI API",
    version="2.0.0",
    description="Health & Beauty Intelligence - Decision Support Engine",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Exception Handlers (Framework 5 aligned, Phase 1 compatible) ---

if NotFoundError:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "NOT_FOUND", "message": str(exc)}},
        )

if ConflictError:
    @app.exception_handler(ConflictError)
    async def conflict_handler(request, exc):
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "CONFLICT", "message": str(exc)}},
        )

if ConsentError:
    @app.exception_handler(ConsentError)
    async def consent_handler(request, exc):
        return JSONResponse(
            status_code=403,
            content={"error": {"code": "CONSENT_REQUIRED", "message": str(exc)}},
        )

if ValidationError:
    @app.exception_handler(ValidationError)
    async def validation_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}},
        )


# --- Router Registration ---
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(cases_router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(sales_router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(evidence_router, prefix="/api/v1/evidence", tags=["Evidence"])


# --- System Endpoints ---
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "phase": "2", "gate": "6-5"}
