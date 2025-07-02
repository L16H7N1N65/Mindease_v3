import os, logging, uvicorn
from app import create_app
from app.db.database import init_db

log = logging.getLogger("mindease")

app = create_app()

@app.on_event("startup")
async def startup():
    # run Alembic only when explicit
    init_db(migrate=bool(os.getenv("MIGRATE_ON_START")))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



# """
# Main application entry point for MindEase FastAPI.
# """
# import logging
# from app import create_app

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
# )
# logger = logging.getLogger(__name__)

# # Create FastAPI application instance
# app = create_app()

# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting MindEase FastAPI server")
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

