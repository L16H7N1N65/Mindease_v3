import logging
from typing import Dict, List

from datasets import load_dataset
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentMetadata, DocumentEmbedding
from app.services.embedding_service import EmbeddingService
from tqdm import tqdm
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ETLPipeline:
    def __init__(self, db: Session, embedding_service: EmbeddingService):
        self.db = db
        self.embedding_service = embedding_service

    def run(self) -> None:
        logger.info("Loading HuggingFace dataset: RishiKompelli/TherapyDataset")
        try:
            dataset = load_dataset("RishiKompelli/TherapyDataset", split="train")
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return
    
        # ✅ Compose content from 'input' and 'output'
        contents = [
            f"{item['input']}\n{item['output']}" 
            for item in dataset 
            if 'input' in item and 'output' in item
        ]

        # 🔐 Generate embeddings
        embeddings = self.embedding_service.generate_embeddings(contents)
        embedding_model_name = self.embedding_service.model_name # Get model name

        documents_to_add = []
        metadata_to_add = []

        for i, item in tqdm(enumerate(dataset), total=len(dataset), desc="ETL"):
            try:
                # ✅ Compose document content from fields
                content = f"{item.get('input', '')}\n{item.get('output', '')}".strip()
                title = f"therapy_dialogue_{i}"
                category = "therapy"
                metadata = {k: str(v) for k, v in item.items() if k not in {"input", "output"}}

                doc = Document(
                    title=title[:255],
                    content=content,
                    source="huggingface:RishiKompelli/TherapyDataset",
                    category=category
                )
                documents_to_add.append(doc)
                self.db.add(doc)
                self.db.flush() # Flush to get doc.id

                # Create DocumentEmbedding instance and associate it
                doc_embedding = DocumentEmbedding(
                    document_id=doc.id,
                    content=content, # Store the content that was embedded
                    embedding=embeddings[i],
                    model_name=embedding_model_name
                )
                self.db.add(doc_embedding)

                for key, value in metadata.items():
                    metadata_to_add.append(DocumentMetadata(document_id=doc.id, key=key, value=value))
            except Exception as e:
                logger.warning(f"Skipping document {i} due to error: {e}")

        if metadata_to_add:
            self.db.add_all(metadata_to_add)

        self.db.commit()
        logger.info(f"Successfully  imported {len(documents_to_add)} documents from HuggingFace.")
        # """
# ETL pipeline for processing documents and generating embeddings using standard Python libraries.
# """
# import csv
# import json
# import logging
# import os
# import time
# from typing import Any, Dict, Generator, List, Optional, Tuple

# from sqlalchemy.orm import Session
# from app.db.models import User
# from app.core.config import settings
# from app.db.models import Document, DocumentMetadata
# from app.services.embedding_service import EmbeddingService

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# class ETLPipeline:
#     """
#     ETL pipeline for processing documents from various sources.
#     """
#     def __init__(self, db: Session, embedding_service: EmbeddingService, user: Optional[User] = None):
#         """
#         Initialize the ETL pipeline.
        
#         Args:
#             db: Database session
#             embedding_service: Embedding service instance
#         """
#         self.db = db
#         self.embedding_service = embedding_service
#         self.user = user  # User context injected into pipeline
#         self.batch_size = settings.BATCH_SIZE
#         self.dataset_dir = settings.DATASET_DIR

#     def run(self) -> None:
#         """
#         Run the ETL pipeline.
#         """
#         logger.info("Starting ETL pipeline...")
#         start_time = time.time()
        
#         processed_count = 0
#         skipped_count = 0
#         error_count = 0
        
#         if not os.path.exists(self.dataset_dir):
#             logger.warning(f"Dataset directory not found: {self.dataset_dir}")
#             return

#         for filename in os.listdir(self.dataset_dir):
#             file_path = os.path.join(self.dataset_dir, filename)
#             if os.path.isfile(file_path):
#                 logger.info(f"Processing file: {filename}")
#                 try:
#                     count, errors = self.process_file(file_path)
#                     processed_count += count
#                     error_count += errors
#                 except Exception as e:
#                     logger.error(f"Error processing file {filename}: {str(e)}")
#                     error_count += 1
#             else:
#                 logger.info(f"Skipping directory: {filename}")
#                 skipped_count += 1

#         end_time = time.time()
#         duration = end_time - start_time
#         logger.info(f"ETL pipeline finished in {duration:.2f} seconds.")
#         logger.info(f"Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}")

#     def process_file(self, file_path: str) -> Tuple[int, int]:
#         """
#         Process a single file based on its extension.
        
#         Args:
#             file_path: Path to the file
            
#         Returns:
#             Tuple of (processed_count, error_count)
#         """
#         _, ext = os.path.splitext(file_path)
#         ext = ext.lower()
        
#         processed_count = 0
#         error_count = 0
        
#         try:
#             if ext == ".csv":
#                 processed_count, error_count = self._process_csv(file_path)
#             elif ext == ".json":
#                 processed_count, error_count = self._process_json(file_path)
#             elif ext == ".txt":
#                 processed_count, error_count = self._process_txt(file_path)
#             else:
#                 logger.warning(f"Unsupported file type: {ext}")
#                 error_count = 1
#         except Exception as e:
#             logger.error(f"Error processing file {file_path}: {str(e)}")
#             error_count = 1
            
#         return processed_count, error_count

#     def _process_csv(self, file_path: str) -> Tuple[int, int]:
#         """
#         Process a CSV file.
        
#         Args:
#             file_path: Path to the CSV file
            
#         Returns:
#             Tuple of (processed_count, error_count)
#         """
#         processed_count = 0
#         error_count = 0
#         batch_data = []
        
#         try:
#             with open(file_path, mode='r', encoding='utf-8') as file:
            
#                 reader = csv.DictReader(file)
#                 for row in reader:
#                     try:
#                         document_data = self._extract_document_data(row, file_path)
#                         if document_data:
#                             batch_data.append(document_data)
#                             if len(batch_data) >= self.batch_size:
#                                 self._process_batch(batch_data)
#                                 processed_count += len(batch_data)
#                                 batch_data = []
#                     except Exception as e:
#                         logger.error(f"Error processing row in {file_path}: {row} - {str(e)}")
#                         error_count += 1
            
#             # Process remaining batch
#             if batch_data:
#                 self._process_batch(batch_data)
#                 processed_count += len(batch_data)
                
#         except Exception as e:
#             logger.error(f"Error reading CSV file {file_path}: {str(e)}")
#             error_count += 1
            
#         return processed_count, error_count

#     def _process_json(self, file_path: str) -> Tuple[int, int]:
#         """
#         Process a JSON file (assuming a list of objects).
        
#         Args:
#             file_path: Path to the JSON file
            
#         Returns:
#             Tuple of (processed_count, error_count)
#         """
#         processed_count = 0
#         error_count = 0
#         batch_data = []
        
#         try:
#             with open(file_path, mode='r', encoding='utf-8') as file:
            
            
#                 data = json.load(file)
#                 if not isinstance(data, list):
#                     logger.warning(f"JSON file {file_path} is not a list of objects. Skipping.")
#                     return 0, 1
                    
#                 for item in data:
#                     if isinstance(item, dict):
#                         try:
#                             document_data = self._extract_document_data(item, file_path)
#                             if document_data:
#                                 batch_data.append(document_data)
#                                 if len(batch_data) >= self.batch_size:
#                                     self._process_batch(batch_data)
#                                     processed_count += len(batch_data)
#                                     batch_data = []
#                         except Exception as e:
#                             logger.error(f"Error processing item in {file_path}: {item} - {str(e)}")
#                             error_count += 1
#                     else:
#                         logger.warning(f"Skipping non-dictionary item in {file_path}: {item}")
#                         error_count += 1
            
#             # Process remaining batch
#             if batch_data:
#                 self._process_batch(batch_data)
#                 processed_count += len(batch_data)
                
#         except json.JSONDecodeError as e:
#             logger.error(f"Error decoding JSON file {file_path}: {str(e)}")
#             error_count += 1
#         except Exception as e:
#             logger.error(f"Error reading JSON file {file_path}: {str(e)}")
#             error_count += 1
            
#         return processed_count, error_count

#     def _process_txt(self, file_path: str) -> Tuple[int, int]:
#         """
#         Process a plain text file.
        
#         Args:
#             file_path: Path to the text file
            
#         Returns:
#             Tuple of (processed_count, error_count)
#         """
#         processed_count = 0
#         error_count = 0
        
#         try:
#             with open(file_path, mode='r', encoding='utf-8') as file:
           
#                 content = file.read()
#                 if content:
#                     document_data = self._extract_document_data({"content": content}, file_path)
#                     if document_data:
#                         self._process_batch([document_data])
#                         processed_count = 1
#                 else:
#                     logger.warning(f"Text file {file_path} is empty. Skipping.")
#                     error_count = 1
                    
#         except Exception as e:
#             logger.error(f"Error reading text file {file_path}: {str(e)}")
#             error_count = 1
            
#         return processed_count, error_count

#     def _extract_document_data(self, data: Dict, source: str) -> Optional[Dict]:
#         """
#         Extract document data from a dictionary.
        
#         Args:
#             data: Dictionary containing document data
#             source: Source of the data (e.g., file path)
            
#         Returns:
#             Dictionary with extracted document data or None if invalid
#         """
#         content = self._find_content(data)
#         if not content:
#             logger.warning(f"Could not find content in data from {source}: {data}")
#             return None
            
#         title = self._find_title(data, content)
#         category = self._extract_category_from_row(data, source)
#         metadata_items = {k: str(v) for k, v in data.items() if k not in ["content", "title", "category", "embedding"] and v is not None}
        
#         return {
#             "title": title,
#             "content": content,
#             "source": source,
#             "category": category,
#             "metadata": metadata_items
#         }

#     def _find_content(self, data: Dict) -> Optional[str]:
#         """
#         Find the main content field in the data dictionary.
        
#         Args:
#             data: Dictionary containing document data
            
#         Returns:
#             Content string or None
#         """
#         content_keys = ["content", "text", "body", "description", "abstract"]
#         for key in content_keys:
#             if key in data and data[key]:
#                 return str(data[key])
        
#         # Fallback: concatenate all string values
#         all_strings = [str(v) for v in data.values() if isinstance(v, str)]
#         if all_strings:
#             return " ".join(all_strings)
            
#         return None

#     def _find_title(self, data: Dict, content: str) -> str:
#         """
#         Find or generate a title for the document.
        
#         Args:
#             data: Dictionary containing document data
#             content: Document content
            
#         Returns:
#             Title string
#         """
#         title_keys = ["title", "header", "subject", "name"]
#         for key in title_keys:
#             if key in data and data[key]:
#                 return str(data[key])[:255] # Limit title length
        
#         # Generate title from content if not found
#         return self._generate_title_from_content(content)

#     def _process_batch(self, batch_data: List[Dict]) -> None:
#         """
#         Process a batch of documents: generate embeddings and save to DB.
        
#         Args:
#             batch_data: List of dictionaries, each containing document data
#         """
#         logger.info(f"Processing batch of {len(batch_data)} documents...")
#         contents = [item["content"] for item in batch_data]
        
#         try:
#             embeddings = self.embedding_service.generate_embeddings(contents)
            
#             documents_to_add = []
#             metadata_to_add = []
            
#             for i, item in enumerate(batch_data):
#                 # Check if document already exists (e.g., by source and title)
#                 existing_doc = self.db.query(Document).filter(
#                     Document.source == item["source"],
#                     Document.title == item["title"]
#                 ).first()
                
#                 if existing_doc:
#                     logger.info(f"Document already exists, updating: {item['title']}")
                   
#                     existing_doc.content = item["content"]
#                     existing_doc.embedding = embeddings[i]
#                     existing_doc.category = item["category"]
#                     # Update metadata (simple approach: clear and add new)
#                     self.db.query(DocumentMetadata).filter(DocumentMetadata.document_id == existing_doc.id).delete()
#                     for key, value in item["metadata"].items():
#                         metadata_to_add.append(DocumentMetadata(document_id=existing_doc.id, key=key, value=value))
#                 else:
#                     logger.info(f"Creating new document: {item['title']}")
#                     new_doc = Document(
#                         title=item["title"],
#                         content=item["content"],
#                         embedding=embeddings[i],
#                         source=item["source"],
#                         category=item["category"]
#                     )
#                     documents_to_add.append(new_doc)
#                     # Need to add metadata after document is added and has an ID
            
#             # Add new documents
#             if documents_to_add:
#                 self.db.add_all(documents_to_add)
#                 self.db.flush() # Ensure IDs are generated
                
#                 # Add metadata for new documents
#                 for i, item in enumerate(batch_data):
#                     if i < len(documents_to_add):
#                         doc_id = documents_to_add[i].id
#                         for key, value in item["metadata"].items():
#                             metadata_to_add.append(DocumentMetadata(document_id=doc_id, key=key, value=value))
            
#             # Add all metadata (new and updated)
#             if metadata_to_add:
#                 self.db.add_all(metadata_to_add)
                
#             self.db.commit()
#             logger.info(f"Successfully processed batch of {len(batch_data)} documents.")
            
#         except Exception as e:
#             logger.error(f"Error processing batch: {str(e)}")
#             self.db.rollback()

#     def _generate_title_from_content(self, content: str) -> str:
#         """
#         Generate a title from the first few words or sentence of the content.
        
#         Args:
#             content: Document content
            
#         Returns:
#             Generated title
#         """
#         # Use first line or first sentence
#         if '\n' in content:
#             first_line = content.split('\n')[0].strip()
#             if first_line:
#                 return first_line[:100]
        
#         # Use first sentence
#         if '.' in content[:100]:
#             first_sentence = content.split('.')[0].strip()
            
#             if first_sentence:
#                 return first_sentence[:100]
        
#         # Use first 100 characters
#         return content[:100].strip()
    
#     def _extract_category_from_row(self, row: Dict, source: str) -> str:
#         """
#         Extract category from a row dictionary or source.
        
#         Args:
#             row: Dictionary representing a row
#             source: Source of the data
            
#         Returns:
#             Category
#         """
#         # Check if there's a category column
#         for category_col in ['category', 'type', 'class', 'tag']:
#             if category_col in row and row[category_col]:
#                 return str(row[category_col])
        
#         # Use filename as category
        
#         return os.path.basename(source).split('.')[0]
        
# def process_file(
#     file_path: str,
#     category: str,
#     batch_size: int,
#     db: Session
# ) -> Tuple[int, int]:
#     """
#     Wrapper module-level pour traiter un seul fichier.
#     """
#     embedding_svc = EmbeddingService()
#     pipeline = ETLPipeline(db=db, embedding_service=embedding_svc)
#     pipeline.batch_size = batch_size

#     return pipeline.process_file(file_path)

# def process_archive(
#     archive_dir: str,
#     batch_size: int,
#     db: Session
# ) -> None:
#     """
#     Wrapper module-level pour traiter tout un dossier.
#     """
#     embedding_svc = EmbeddingService()
#     pipeline = ETLPipeline(db=db, embedding_service=embedding_svc)
#     pipeline.batch_size = batch_size
#     pipeline.dataset_dir = archive_dir
#     pipeline.run()