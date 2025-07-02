"""
Data extractors for various data sources in the ETL pipeline.
Handles different file formats and data sources for mental health datasets.
"""
import csv
import json
import logging
import os
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union
from urllib.parse import urlparse

import requests
from datasets import load_dataset 

# Configure logging
logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Base class for all data extractors."""
    
    def __init__(self, source: Union[str, Path], **kwargs):
        """
        Initialize the extractor.
        
        Args:
            source: Data source (file path, URL, etc.)
            **kwargs: Additional configuration options
        """
        self.source = source
        self.config = kwargs
        
    @abstractmethod
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from the source.
        
        Yields:
            Dictionary containing extracted data
        """
        pass
    
    @abstractmethod
    def validate_source(self) -> bool:
        """
        Validate that the data source is accessible and valid.
        
        Returns:
            True if source is valid, False otherwise
        """
        pass


class CSVExtractor(BaseExtractor):
    """Extractor for CSV files containing mental health data."""
    
    def __init__(self, source: Union[str, Path] = None, delimiter: str = ',', encoding: str = 'utf-8', **kwargs):
        """
        Initialize CSV extractor.
        
        Args:
            source: Path to CSV file (optional for testing)
            delimiter: CSV delimiter character
            encoding: File encoding
            **kwargs: Additional options
        """
        if source is not None:
            super().__init__(source, **kwargs)
        self.delimiter = delimiter
        self.encoding = encoding
        
    def validate_source(self) -> bool:
        """Validate CSV file exists and is readable."""
        try:
            path = Path(self.source)
            return path.exists() and path.is_file() and path.suffix.lower() == '.csv'
        except Exception as e:
            logger.error(f"Error validating CSV source {self.source}: {e}")
            return False
    
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from CSV file.
        
        Yields:
            Dictionary for each row in the CSV
        """
        if not self.validate_source():
            logger.error(f"Invalid CSV source: {self.source}")
            return
            
        try:
            with open(self.source, 'r', encoding=self.encoding, newline='') as file:
                # Detect delimiter if not specified
                if self.delimiter == 'auto':
                    sample = file.read(1024)
                    file.seek(0)
                    sniffer = csv.Sniffer()
                    self.delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=self.delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Clean empty values
                        cleaned_row = {k: v.strip() if isinstance(v, str) else v 
                                     for k, v in row.items() if v is not None and v != ''}
                        
                        if cleaned_row:  # Only yield non-empty rows
                            cleaned_row['_source_row'] = row_num
                            cleaned_row['_source_file'] = str(self.source)
                            yield cleaned_row
                            
                    except Exception as e:
                        logger.warning(f"Error processing row {row_num} in {self.source}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading CSV file {self.source}: {e}")


class JSONExtractor(BaseExtractor):
    """Extractor for JSON files containing mental health data."""
    
    def __init__(self, source: Union[str, Path], encoding: str = 'utf-8', **kwargs):
        """
        Initialize JSON extractor.
        
        Args:
            source: Path to JSON file
            encoding: File encoding
            **kwargs: Additional options
        """
        super().__init__(source, **kwargs)
        self.encoding = encoding
        
    def validate_source(self) -> bool:
        """Validate JSON file exists and is readable."""
        try:
            path = Path(self.source)
            if not (path.exists() and path.is_file() and path.suffix.lower() == '.json'):
                return False
                
            # Try to parse JSON to validate format
            with open(path, 'r', encoding=self.encoding) as file:
                json.load(file)
            return True
            
        except Exception as e:
            logger.error(f"Error validating JSON source {self.source}: {e}")
            return False
    
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from JSON file.
        
        Yields:
            Dictionary for each item in the JSON
        """
        if not self.validate_source():
            logger.error(f"Invalid JSON source: {self.source}")
            return
            
        try:
            with open(self.source, 'r', encoding=self.encoding) as file:
                data = json.load(file)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    # Array of objects
                    for index, item in enumerate(data):
                        if isinstance(item, dict):
                            item['_source_index'] = index
                            item['_source_file'] = str(self.source)
                            yield item
                        else:
                            logger.warning(f"Skipping non-dict item at index {index} in {self.source}")
                            
                elif isinstance(data, dict):
                    # Single object or nested structure
                    if 'data' in data and isinstance(data['data'], list):
                        # Common structure: {"data": [...]}
                        for index, item in enumerate(data['data']):
                            if isinstance(item, dict):
                                item['_source_index'] = index
                                item['_source_file'] = str(self.source)
                                yield item
                    else:
                        # Single object
                        data['_source_index'] = 0
                        data['_source_file'] = str(self.source)
                        yield data
                        
                else:
                    logger.warning(f"Unsupported JSON structure in {self.source}")
                    
        except Exception as e:
            logger.error(f"Error reading JSON file {self.source}: {e}")


class TextExtractor(BaseExtractor):
    """Extractor for plain text files."""
    
    def __init__(self, source: Union[str, Path], encoding: str = 'utf-8', chunk_size: Optional[int] = None, **kwargs):
        """
        Initialize text extractor.
        
        Args:
            source: Path to text file
            encoding: File encoding
            chunk_size: Optional size to split large texts into chunks
            **kwargs: Additional options
        """
        super().__init__(source, **kwargs)
        self.encoding = encoding
        self.chunk_size = chunk_size
        
    def validate_source(self) -> bool:
        """Validate text file exists and is readable."""
        try:
            path = Path(self.source)
            return path.exists() and path.is_file() and path.suffix.lower() in ['.txt', '.md', '.rst']
        except Exception as e:
            logger.error(f"Error validating text source {self.source}: {e}")
            return False
    
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from text file.
        
        Yields:
            Dictionary containing text content (potentially chunked)
        """
        if not self.validate_source():
            logger.error(f"Invalid text source: {self.source}")
            return
            
        try:
            with open(self.source, 'r', encoding=self.encoding) as file:
                content = file.read().strip()
                
                if not content:
                    logger.warning(f"Empty text file: {self.source}")
                    return
                
                # Generate title from filename
                filename = Path(self.source).stem
                title = filename.replace('_', ' ').replace('-', ' ').title()
                
                if self.chunk_size and len(content) > self.chunk_size:
                    # Split into chunks
                    chunks = self._split_text(content, self.chunk_size)
                    for index, chunk in enumerate(chunks):
                        yield {
                            'title': f"{title} - Part {index + 1}",
                            'content': chunk,
                            'chunk_index': index,
                            'total_chunks': len(chunks),
                            '_source_file': str(self.source)
                        }
                else:
                    # Single document
                    yield {
                        'title': title,
                        'content': content,
                        '_source_file': str(self.source)
                    }
                    
        except Exception as e:
            logger.error(f"Error reading text file {self.source}: {e}")
    
    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks while preserving sentence boundaries.
        
        Args:
            text: Text to split
            chunk_size: Maximum chunk size
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 1 > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Sentence itself is too long, split by words
                    words = sentence.split()
                    for word in words:
                        if len(current_chunk) + len(word) + 1 > chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = word
                            else:
                                # Single word is too long, just add it
                                chunks.append(word)
                        else:
                            current_chunk += " " + word if current_chunk else word
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


class ArchiveExtractor(BaseExtractor):
    """Extractor for ZIP archives containing multiple data files."""
    
    def __init__(self, source: Union[str, Path], extract_to: Optional[str] = None, **kwargs):
        """
        Initialize archive extractor.
        
        Args:
            source: Path to ZIP file
            extract_to: Directory to extract files to (temporary if None)
            **kwargs: Additional options
        """
        super().__init__(source, **kwargs)
        self.extract_to = extract_to or f"/tmp/mindease_extract_{os.getpid()}"
        
    def validate_source(self) -> bool:
        """Validate ZIP file exists and is readable."""
        try:
            path = Path(self.source)
            if not (path.exists() and path.is_file() and path.suffix.lower() == '.zip'):
                return False
                
            # Try to open ZIP file
            with zipfile.ZipFile(path, 'r') as zip_file:
                zip_file.testzip()
            return True
            
        except Exception as e:
            logger.error(f"Error validating ZIP source {self.source}: {e}")
            return False
    
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from ZIP archive.
        
        Yields:
            Dictionary for each file in the archive
        """
        if not self.validate_source():
            logger.error(f"Invalid ZIP source: {self.source}")
            return
            
        extract_path = Path(self.extract_to)
        extract_path.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(self.source, 'r') as zip_file:
                zip_file.extractall(extract_path)
                
                # Process each extracted file
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        file_path = Path(root) / file
                        
                        # Determine appropriate extractor
                        extractor = self._get_file_extractor(file_path)
                        if extractor:
                            try:
                                for data in extractor.extract():
                                    data['_archive_source'] = str(self.source)
                                    yield data
                            except Exception as e:
                                logger.error(f"Error extracting from {file_path}: {e}")
                                
        except Exception as e:
            logger.error(f"Error processing ZIP file {self.source}: {e}")
        finally:
            # Cleanup extracted files
            self._cleanup_extracted_files(extract_path)
    
    def _get_file_extractor(self, file_path: Path) -> Optional[BaseExtractor]:
        """Get appropriate extractor for file type."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            return CSVExtractor(file_path)
        elif suffix == '.json':
            return JSONExtractor(file_path)
        elif suffix in ['.txt', '.md', '.rst']:
            return TextExtractor(file_path)
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return None
    
    def _cleanup_extracted_files(self, extract_path: Path):
        """Clean up extracted files."""
        try:
            import shutil
            shutil.rmtree(extract_path)
        except Exception as e:
            logger.warning(f"Error cleaning up extracted files: {e}")


class URLExtractor(BaseExtractor):
    """Extractor for downloading data from URLs."""
    
    def __init__(self, source: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None, **kwargs):
        """
        Initialize URL extractor.
        
        Args:
            source: URL to download from
            timeout: Request timeout in seconds
            headers: Optional HTTP headers
            **kwargs: Additional options
        """
        super().__init__(source, **kwargs)
        self.timeout = timeout
        self.headers = headers or {}
        
    def validate_source(self) -> bool:
        """Validate URL is accessible."""
        try:
            parsed = urlparse(self.source)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except Exception as e:
            logger.error(f"Error validating URL source {self.source}: {e}")
            return False
    
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from URL.
        
        Yields:
            Dictionary containing downloaded data
        """
        if not self.validate_source():
            logger.error(f"Invalid URL source: {self.source}")
            return
            
        try:
            response = requests.get(self.source, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            
            # Determine content type and process accordingly
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                data = response.json()
                if isinstance(data, list):
                    for index, item in enumerate(data):
                        if isinstance(item, dict):
                            item['_source_url'] = self.source
                            item['_source_index'] = index
                            yield item
                elif isinstance(data, dict):
                    data['_source_url'] = self.source
                    yield data
                    
            elif 'text/csv' in content_type:
                # Save to temporary file and use CSV extractor
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                    temp_file.write(response.text)
                    temp_path = temp_file.name
                
                try:
                    csv_extractor = CSVExtractor(temp_path)
                    for data in csv_extractor.extract():
                        data['_source_url'] = self.source
                        yield data
                finally:
                    os.unlink(temp_path)
                    
            else:
                # Treat as plain text
                yield {
                    'title': f"Content from {self.source}",
                    'content': response.text,
                    '_source_url': self.source
                }
                
        except Exception as e:
            logger.error(f"Error downloading from URL {self.source}: {e}")


# NEW EXTRACTOR FOR HUGGING FACE DATASETS
class HuggingFaceDatasetExtractor(BaseExtractor):
    """Extractor for Hugging Face datasets"""
    
    def __init__(self, source: str, split: str = 'train', **kwargs):
        """
        Initialize Hugging Face extractor.
        
        Args:
            source: Dataset identifier (e.g., 'username/dataset_name')
            split: Dataset split to use (train, test, validation)
            **kwargs: Additional options
        """
        super().__init__(source, **kwargs)
        self.split = split
        
    def validate_source(self) -> bool:
        """Validate dataset exists and is accessible."""
        try:
            # Check if dataset exists
            dataset_info = load_dataset(self.source, download_mode='force_redownload')
            return True
        except Exception as e:
            logger.error(f"Error validating Hugging Face source {self.source}: {e}")
            return False
    
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        if not self.validate_source():
            logger.error(f"Invalid Hugging Face source: {self.source}")
            return
            
        try:
            # Load dataset with error handling
            try:
                dataset = load_dataset(self.source, split=self.split)
            except ValueError:
                dataset = load_dataset(self.source)
                if self.split in dataset:
                    dataset = dataset[self.split]
                else:
                    dataset = next(iter(dataset.values()))
            
            # Yield each item in the dataset
            for index, item in enumerate(dataset):
                # Convert to dict if it's a special dataset type
                if hasattr(item, 'keys'):
                    item = dict(item)
                
                # Ensure there's a content field
                if 'content' not in item:
                    # Try to find a text field
                    for field in ['text', 'content', 'body', 'input', 'output', 'response']:
                        if field in item:
                            item['content'] = item[field]
                            break
                    
                    # If no content found, create from available fields
                    if 'content' not in item:
                        item['content'] = "\n\n".join(
                            f"{k}: {v}" for k, v in item.items() if isinstance(v, str)
                        )
                
                # Add source metadata
                item['_source_dataset'] = self.source
                item['_source_index'] = index
                yield item
                
        except Exception as e:
            logger.error(f"Error loading Hugging Face dataset {self.source}: {e}")


class ExtractorFactory:
    """Factory for creating appropriate extractors based on source type."""
    
    @staticmethod
    def create_extractor(source: Union[str, Path], **kwargs) -> Optional[BaseExtractor]:
        """
        Create appropriate extractor for the given source.
        
        Args:
            source: Data source (file path, URL, etc.)
            **kwargs: Additional configuration options
            
        Returns:
            Appropriate extractor instance or None if unsupported
        """
        source_str = str(source)
        
        # URL extractor
        if source_str.startswith(('http://', 'https://')):
            return URLExtractor(source_str, **kwargs)
        
        # File extractors
        path = Path(source)
        if path.exists():
            suffix = path.suffix.lower()
            
            if suffix == '.csv':
                return CSVExtractor(source, **kwargs)
            elif suffix == '.json':
                return JSONExtractor(source, **kwargs)
            elif suffix in ['.txt', '.md', '.rst']:
                return TextExtractor(source, **kwargs)
            elif suffix == '.zip':
                return ArchiveExtractor(source, **kwargs)
            else:
                logger.warning(f"Unsupported source type: {suffix}")
                return None
        
        # Hugging Face dataset extractor (if source contains '/')
        if '/' in source_str:
            return HuggingFaceDatasetExtractor(source_str, **kwargs)
        
        logger.error(f"Source not found: {source}")
        return None


# Convenience functions
def extract_from_source(source: Union[str, Path], **kwargs) -> Generator[Dict[str, Any], None, None]:
    """
    Extract data from any supported source.
    
    Args:
        source: Data source (file path, URL, etc.)
        **kwargs: Additional configuration options
        
    Yields:
        Dictionary containing extracted data
    """
    extractor = ExtractorFactory.create_extractor(source, **kwargs)
    if extractor:
        yield from extractor.extract()
    else:
        logger.error(f"Could not create extractor for source: {source}")


async def extract_async(source: Union[str, Path], **kwargs) -> List[Dict[str, Any]]:
    """
    Async wrapper for data extraction.
    
    Args:
        source: Data source (file path, URL, etc.)
        **kwargs: Additional options for the extractor
        
    Returns:
        List of extracted data dictionaries
    """
    extractor = ExtractorFactory.create_extractor(source, **kwargs)
    if extractor:
        return list(extractor.extract())
    else:
        logger.error(f"Could not create extractor for source: {source}")
        return []


def get_supported_formats() -> List[str]:
    """Get list of supported file formats."""
    return ['.csv', '.json', '.txt', '.md', '.rst', '.zip']


def validate_source(source: Union[str, Path]) -> bool:
    """
    Validate if a source is supported and accessible.
    
    Args:
        source: Data source to validate
        
    Returns:
        True if source is valid, False otherwise
    """
    extractor = ExtractorFactory.create_extractor(source)
    return extractor.validate_source() if extractor else False