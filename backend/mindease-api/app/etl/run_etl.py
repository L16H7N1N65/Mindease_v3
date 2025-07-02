# app/etl/run_etl.py
import logging
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.etl.pipeline import ETLPipeline
from app.services.embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("etl_runner")


def main() -> None:
    db: Session = SessionLocal()
    try:
        pipeline = ETLPipeline(db, EmbeddingService())
        pipeline.run()                     # ← run is synchronous
        logger.info("ETL finished successfully")
    except Exception as e:
        logger.error(f"ETL failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

# # run_etl.py

# import asyncio
# import logging
# from sqlalchemy.orm import Session
# from app.db.session import SessionLocal
# from app.etl.pipeline import ETLPipeline

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("etl_runner")

# async def main():
#     db: Session = SessionLocal()
#     try:
#         pipeline = ETLPipeline(db)
#         await pipeline.run()
#     except Exception as e:
#         logger.error(f"ETL failed: {e}")
#     finally:
#         db.close()

# if __name__ == "__main__":
#     asyncio.run(main())
    
    
# # run_etl.py
# import asyncio
# import logging
# from app.db.session    import get_async_db
# from app.etl.extractors import extract_from_source
# from app.etl.transformers import create_default_pipeline
# from app.etl.validators import ETLValidator
# from app.etl.loaders    import ETLLoader
# from app.core.config    import settings

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# async def main():
#     async with get_async_db() as session:
#         transformer = create_default_pipeline()
#         validator   = ETLValidator(enable_all=True)
#         loader      = ETLLoader()

#         for src in settings.DATASET_SOURCES:    # e.g. ["RishiKompelli/TherapyDataset", "./archive"]
#             logger.info(f"Processing source: {src}")
#             raw_items = list(extract_from_source(src))
#             logger.info(f"  Extracted {len(raw_items)} items")

#             # 2. Transform
#             transformed = transformer.transform_batch(raw_items)
#             logger.info(f"  Transformed → {len(transformed)} items")

#             # 3. Validate & filter
#             valid_items, report = await validator.validate_and_filter(
#                 transformed,
#                 allow_warnings=True,
#                 allow_errors=False
#             )
#             logger.info(f"  Validation: {report.valid_items}/{report.total_items} passed "
#                         f"({report.errors} errors, {report.warnings} warnings)")

#             if not valid_items:
#                 logger.warning(f"No valid items to load for source {src}, skipping.")
#                 continue

#             # 4. Load
#             stats = await loader.load_dataset(
#                 session,
#                 {"name": src, "documents": valid_items}
#             )
#             logger.info(f"  Loaded {stats['documents']['successful']} documents "
#                         f"({stats['documents']['failed']} failed)")

# if __name__ == "__main__":
#     asyncio.run(main())
    
# """
# Script to run the ETL pipeline for processing archive datasets.
# """
# import logging
# import time
# from typing import Optional

# from sqlalchemy.orm import Session

# from app.db.session import SessionLocal
# from app.etl.pipeline import ETLPipeline
# from app.services.embedding_service import EmbeddingService

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def run_etl(db: Optional[Session] = None) -> None:
#     """
#     Run the ETL pipeline to process datasets from the archive folder.
    
#     Args:
#         db: Optional database session (creates one if not provided)
#     """
#     start_time = time.time()
#     logger.info("Starting ETL process...")
    
#     # Create database session if not provided
#     close_db = False
#     if db is None:
#         db = SessionLocal()
#         close_db = True
    
#     try:
#         # Initialize services
#         embedding_service = EmbeddingService()
        
#         # Initialize and run pipeline
#         pipeline = ETLPipeline(db, embedding_service)
#         results = pipeline.process_all_datasets()
        
#         # Log results
#         total_documents = sum(results.values())
#         logger.info(f"ETL process completed. Processed {total_documents} documents from {len(results)} datasets.")
#         for dataset, count in results.items():
#             logger.info(f"  - {dataset}: {count} documents")
        
#         elapsed_time = time.time() - start_time
#         logger.info(f"Total processing time: {elapsed_time:.2f} seconds")
    
#     except Exception as e:
#         logger.error(f"Error running ETL process: {str(e)}")
#         raise
    
#     finally:
#         if close_db:
#             db.close()


# if __name__ == "__main__":
#     run_etl()
