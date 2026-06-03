from fastapi import FastAPI
from app.api.routes import router

# Initialize the application
app = FastAPI(title="Financial Ledger API")


# Plug in the router containing all the endpoints
app.include_router(router)


