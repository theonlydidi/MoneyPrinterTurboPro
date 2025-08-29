"""
Storage Manager for MoneyPrinterTurboPro
Handles file storage, cloud storage, and caching
"""

import asyncio
import json
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import hashlib

import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
import requests
from minio import Minio
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logging import get_logger, time_operation


logger = get_logger(__name__)


class StorageManager:
    """Storage management with local and cloud providers"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_providers()
        self._setup_directories()
        self._load_storage_config()
        
    def _initialize_providers(self):
        """Initialize storage providers"""
        # AWS S3
        if (settings.cloud_storage.aws_access_key and 
            settings.cloud_storage.aws_secret_key and 
            settings.cloud_storage.aws_region):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.cloud_storage.aws_access_key,
                    aws_secret_access_key=settings.cloud_storage.aws_secret_key,
                    region_name=settings.cloud_storage.aws_region
                )
                self.s3_available = True
                self.logger.info("🚀 AWS S3 storage initialized")
            except Exception as e:
                self.logger.warning(f"AWS S3 initialization failed: {str(e)}")
                self.s3_available = False
        else:
            self.s3_available = False
            
        # Azure Blob Storage
        if settings.cloud_storage.azure_connection_string:
            try:
                self.azure_client = BlobServiceClient.from_connection_string(
                    settings.cloud_storage.azure_connection_string
                )
                self.azure_available = True
                self.logger.info("🚀 Azure Blob Storage initialized")
            except Exception as e:
                self.logger.warning(f"Azure Blob Storage initialization failed: {str(e)}")
                self.azure_available = False
        else:
            self.azure_available = False
            
        # Google Cloud Storage
        if settings.cloud_storage.google_credentials_path:
            try:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.cloud_storage.google_credentials_path
                self.gcs_client = storage.Client()
                self.gcs_available = True
                self.logger.info("🚀 Google Cloud Storage initialized")
            except Exception as e:
                self.logger.warning(f"Google Cloud Storage initialization failed: {str(e)}")
                self.gcs_available = False
        else:
            self.gcs_available = False
            
        # MinIO (Local/Private Cloud)
        if (settings.cloud_storage.minio_endpoint and 
            settings.cloud_storage.minio_access_key and 
            settings.cloud_storage.minio_secret_key):
            try:
                self.minio_client = Minio(
                    settings.cloud_storage.minio_endpoint,
                    access_key=settings.cloud_storage.minio_access_key,
                    secret_key=settings.cloud_storage.minio_secret_key,
                    secure=settings.cloud_storage.minio_secure
                )
                self.minio_available = True
                self.logger.info("🚀 MinIO storage initialized")
            except Exception as e:
                self.logger.warning(f"MinIO initialization failed: {str(e)}")
                self.minio_available = False
        else:
            self.minio_available = False
    
    def _setup_directories(self):
        """Setup local storage directories"""
        directories = [
            settings.storage.storage_path,
            settings.storage.temp_dir,
            settings.storage.cache_dir,
            settings.storage.output_dir,
            "cache/videos",
            "cache/audio",
            "cache/images",
            "cache/thumbnails",
            "output/videos",
            "output/audio",
            "output/images"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_storage_config(self):
        """Load storage configuration"""
        self.storage_config = {
            'local': {
                'enabled': True,
                'path': settings.storage.storage_path,
                'max_size_gb': settings.storage.max_size_gb,
                'cleanup_interval_hours': 24
            },
            'cache': {
                'enabled': True,
                'path': settings.storage.cache_dir,
                'max_size_gb': settings.storage.cache_max_size_gb,
                'cleanup_interval_hours': 6
            },
            'cloud': {
                'primary': settings.cloud_storage.primary_provider,
                'backup': settings.cloud_storage.backup_provider,
                'sync_enabled': settings.cloud_storage.sync_enabled
            }
        }
    
    @time_operation("file_upload")
    async def upload_file(
        self,
        file_path: str,
        destination: str,
        provider: str = "auto",
        metadata: Optional[Dict[str, Any]] = None,
        public: bool = False
    ) -> Dict[str, Any]:
        """Upload file to storage"""
        
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Select provider
            if provider == "auto":
                provider = self._select_best_provider(file_path)
            
            # Upload based on provider
            if provider == "local":
                result = await self._upload_local(file_path, destination, metadata)
            elif provider == "s3":
                result = await self._upload_s3(file_path, destination, metadata, public)
            elif provider == "azure":
                result = await self._upload_azure(file_path, destination, metadata, public)
            elif provider == "gcs":
                result = await self._upload_gcs(file_path, destination, metadata, public)
            elif provider == "minio":
                result = await self._upload_minio(file_path, destination, metadata, public)
            else:
                raise ValueError(f"Unknown storage provider: {provider}")
            
            if result['success']:
                # Update local index
                await self._update_file_index(destination, result)
                
                # Sync to backup if enabled
                if self.storage_config['cloud']['sync_enabled']:
                    await self._sync_to_backup(file_path, destination, metadata)
            
            return result
            
        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _select_best_provider(self, file_path: str) -> str:
        """Select best storage provider based on file characteristics"""
        
        file_size = os.path.getsize(file_path) / (1024 * 1024 * 1024)  # GB
        
        # Small files: prefer local storage
        if file_size < 0.1:  # < 100MB
            return "local"
        
        # Medium files: prefer cloud storage
        elif file_size < 1.0:  # < 1GB
            if self.s3_available:
                return "s3"
            elif self.azure_available:
                return "azure"
            elif self.gcs_available:
                return "gcs"
            else:
                return "local"
        
        # Large files: prefer cloud storage with backup
        else:
            if self.s3_available:
                return "s3"
            elif self.azure_available:
                return "azure"
            elif self.gcs_available:
                return "gcs"
            else:
                return "local"
    
    async def _upload_local(
        self,
        file_path: str,
        destination: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Upload file to local storage"""
        
        try:
            # Create destination directory
            dest_path = Path(settings.storage.storage_path) / destination
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, dest_path)
            
            # Save metadata
            if metadata:
                metadata_path = dest_path.with_suffix('.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            return {
                'success': True,
                'provider': 'local',
                'path': str(dest_path),
                'size': os.path.getsize(dest_path),
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Local upload failed: {str(e)}")
    
    async def _upload_s3(
        self,
        file_path: str,
        destination: str,
        metadata: Optional[Dict[str, Any]],
        public: bool
    ) -> Dict[str, Any]:
        """Upload file to AWS S3"""
        
        try:
            bucket_name = settings.cloud_storage.aws_bucket_name
            key = destination
            
            # Prepare upload parameters
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            if public:
                extra_args['ACL'] = 'public-read'
            
            # Upload file
            self.s3_client.upload_file(
                file_path,
                bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            # Generate URL
            url = f"https://{bucket_name}.s3.{settings.cloud_storage.aws_region}.amazonaws.com/{key}"
            
            return {
                'success': True,
                'provider': 's3',
                'url': url,
                'bucket': bucket_name,
                'key': key,
                'size': os.path.getsize(file_path),
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    async def _upload_azure(
        self,
        file_path: str,
        destination: str,
        metadata: Optional[Dict[str, Any]],
        public: bool
    ) -> Dict[str, Any]:
        """Upload file to Azure Blob Storage"""
        
        try:
            container_name = settings.cloud_storage.azure_container_name
            blob_name = destination
            
            # Get container client
            container_client = self.azure_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            # Upload file
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    metadata=metadata
                )
            
            # Generate URL
            url = f"https://{settings.cloud_storage.azure_account_name}.blob.core.windows.net/{container_name}/{blob_name}"
            
            return {
                'success': True,
                'provider': 'azure',
                'url': url,
                'container': container_name,
                'blob': blob_name,
                'size': os.path.getsize(file_path),
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Azure upload failed: {str(e)}")
    
    async def _upload_gcs(
        self,
        file_path: str,
        destination: str,
        metadata: Optional[Dict[str, Any]],
        public: bool
    ) -> Dict[str, Any]:
        """Upload file to Google Cloud Storage"""
        
        try:
            bucket_name = settings.cloud_storage.google_bucket_name
            blob_name = destination
            
            # Get bucket and blob
            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            blob.upload_from_filename(file_path)
            
            # Make public if requested
            if public:
                blob.make_public()
            
            # Generate URL
            url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            
            return {
                'success': True,
                'provider': 'gcs',
                'url': url,
                'bucket': bucket_name,
                'blob': blob_name,
                'size': os.path.getsize(file_path),
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"GCS upload failed: {str(e)}")
    
    async def _upload_minio(
        self,
        file_path: str,
        destination: str,
        metadata: Optional[Dict[str, Any]],
        public: bool
    ) -> Dict[str, Any]:
        """Upload file to MinIO"""
        
        try:
            bucket_name = settings.cloud_storage.minio_bucket_name
            object_name = destination
            
            # Ensure bucket exists
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
            
            # Upload file
            self.minio_client.fput_object(
                bucket_name,
                object_name,
                file_path,
                metadata=metadata
            )
            
            # Generate URL
            protocol = "https" if settings.cloud_storage.minio_secure else "http"
            url = f"{protocol}://{settings.cloud_storage.minio_endpoint}/{bucket_name}/{object_name}"
            
            return {
                'success': True,
                'provider': 'minio',
                'url': url,
                'bucket': bucket_name,
                'object': object_name,
                'size': os.path.getsize(file_path),
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"MinIO upload failed: {str(e)}")
    
    @time_operation("file_download")
    async def download_file(
        self,
        source: str,
        destination: str,
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """Download file from storage"""
        
        try:
            # Select provider
            if provider == "auto":
                provider = self._determine_provider(source)
            
            # Download based on provider
            if provider == "local":
                result = await self._download_local(source, destination)
            elif provider == "s3":
                result = await self._download_s3(source, destination)
            elif provider == "azure":
                result = await self._download_azure(source, destination)
            elif provider == "gcs":
                result = await self._download_gcs(source, destination)
            elif provider == "minio":
                result = await self._download_minio(source, destination)
            else:
                raise ValueError(f"Unknown storage provider: {provider}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"File download failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _determine_provider(self, source: str) -> str:
        """Determine storage provider from source string"""
        
        if source.startswith('s3://'):
            return "s3"
        
        # Use urlparse for HTTP(S) URLs
        if source.startswith('http://') or source.startswith('https://'):
            parsed = urlparse(source)
            hostname = parsed.hostname or ""
            if hostname.endswith("blob.core.windows.net"):
                return "azure"
            elif hostname == "storage.googleapis.com" or hostname.endswith(".storage.googleapis.com"):
                return "gcs"
            else:
                return "minio"  # Assume MinIO for other HTTP URLs
        else:
            return "local"
    
    async def _download_local(self, source: str, destination: str) -> Dict[str, Any]:
        """Download file from local storage"""
        
        try:
            source_path = Path(settings.storage.storage_path) / source
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            # Create destination directory
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            return {
                'success': True,
                'provider': 'local',
                'source': str(source_path),
                'destination': str(dest_path),
                'size': os.path.getsize(dest_path)
            }
            
        except Exception as e:
            raise Exception(f"Local download failed: {str(e)}")
    
    async def _download_s3(self, source: str, destination: str) -> Dict[str, Any]:
        """Download file from S3"""
        
        try:
            # Parse S3 URL or key
            if source.startswith('s3://'):
                bucket_name, key = source[5:].split('/', 1)
            else:
                bucket_name = settings.cloud_storage.aws_bucket_name
                key = source
            
            # Create destination directory
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            self.s3_client.download_file(bucket_name, key, destination)
            
            return {
                'success': True,
                'provider': 's3',
                'bucket': bucket_name,
                'key': key,
                'destination': destination,
                'size': os.path.getsize(destination)
            }
            
        except Exception as e:
            raise Exception(f"S3 download failed: {str(e)}")
    
    async def _download_azure(self, source: str, destination: str) -> Dict[str, Any]:
        """Download file from Azure Blob Storage"""
        
        try:
            # Parse Azure URL or blob name
            if source.startswith('https://'):
                # Extract container and blob from URL
                parts = source.split('/')
                container_name = parts[-2]
                blob_name = parts[-1]
            else:
                container_name = settings.cloud_storage.azure_container_name
                blob_name = source
            
            # Create destination directory
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            container_client = self.azure_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            with open(destination, 'wb') as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())
            
            return {
                'success': True,
                'provider': 'azure',
                'container': container_name,
                'blob': blob_name,
                'destination': destination,
                'size': os.path.getsize(destination)
            }
            
        except Exception as e:
            raise Exception(f"Azure download failed: {str(e)}")
    
    async def _download_gcs(self, source: str, destination: str) -> Dict[str, Any]:
        """Download file from Google Cloud Storage"""
        
        try:
            # Parse GCS URL or blob name
            if source.startswith('https://'):
                # Extract bucket and blob from URL
                parts = source.split('/')
                bucket_name = parts[-2]
                blob_name = parts[-1]
            else:
                bucket_name = settings.cloud_storage.google_bucket_name
                blob_name = source
            
            # Create destination directory
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.download_to_filename(destination)
            
            return {
                'success': True,
                'provider': 'gcs',
                'bucket': bucket_name,
                'blob': blob_name,
                'destination': destination,
                'size': os.path.getsize(destination)
            }
            
        except Exception as e:
            raise Exception(f"GCS download failed: {str(e)}")
    
    async def _download_minio(self, source: str, destination: str) -> Dict[str, Any]:
        """Download file from MinIO"""
        
        try:
            # Parse MinIO URL or object name
            if source.startswith('http'):
                # Extract bucket and object from URL
                parts = source.split('/')
                bucket_name = parts[-2]
                object_name = parts[-1]
            else:
                bucket_name = settings.cloud_storage.minio_bucket_name
                object_name = source
            
            # Create destination directory
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            self.minio_client.fget_object(bucket_name, object_name, destination)
            
            return {
                'success': True,
                'provider': 'minio',
                'bucket': bucket_name,
                'object': object_name,
                'destination': destination,
                'size': os.path.getsize(destination)
            }
            
        except Exception as e:
            raise Exception(f"MinIO download failed: {str(e)}")
    
    async def _update_file_index(self, destination: str, upload_result: Dict[str, Any]):
        """Update local file index"""
        
        try:
            index_file = Path(settings.storage.storage_path) / ".file_index.json"
            
            # Load existing index
            if index_file.exists():
                with open(index_file, 'r') as f:
                    index = json.load(f)
            else:
                index = {}
            
            # Update index
            index[destination] = {
                'provider': upload_result['provider'],
                'path': upload_result.get('path', ''),
                'url': upload_result.get('url', ''),
                'size': upload_result.get('size', 0),
                'uploaded_at': upload_result.get('uploaded_at', datetime.now().isoformat()),
                'metadata': upload_result.get('metadata', {})
            }
            
            # Save index
            with open(index_file, 'w') as f:
                json.dump(index, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to update file index: {str(e)}")
    
    async def _sync_to_backup(self, file_path: str, destination: str, metadata: Optional[Dict[str, Any]]):
        """Sync file to backup storage provider"""
        
        try:
            backup_provider = self.storage_config['cloud']['backup']
            
            if backup_provider and backup_provider != "none":
                await self.upload_file(
                    file_path,
                    f"backup/{destination}",
                    provider=backup_provider,
                    metadata=metadata
                )
                
        except Exception as e:
            self.logger.warning(f"Backup sync failed: {str(e)}")
    
    @time_operation("storage_cleanup")
    async def cleanup_storage(self, provider: str = "all") -> Dict[str, Any]:
        """Clean up storage based on configuration"""
        
        try:
            results = {}
            
            if provider in ["all", "local"]:
                results['local'] = await self._cleanup_local_storage()
            
            if provider in ["all", "cache"]:
                results['cache'] = await self._cleanup_cache()
            
            return {
                'success': True,
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Storage cleanup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _cleanup_local_storage(self) -> Dict[str, Any]:
        """Clean up local storage"""
        
        try:
            storage_path = Path(settings.storage.storage_path)
            max_size_gb = self.storage_config['local']['max_size_gb']
            
            # Calculate current size
            total_size = sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file())
            total_size_gb = total_size / (1024 * 1024 * 1024)
            
            if total_size_gb <= max_size_gb:
                return {
                    'cleaned': False,
                    'reason': 'Storage within limits',
                    'current_size_gb': total_size_gb,
                    'max_size_gb': max_size_gb
                }
            
            # Get file list sorted by access time
            files = []
            for file_path in storage_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    stat = file_path.stat()
                    files.append((file_path, stat.st_atime, stat.st_size))
            
            files.sort(key=lambda x: x[1])  # Sort by access time
            
            # Remove old files until under limit
            removed_size = 0
            removed_files = []
            
            for file_path, _, file_size in files:
                if (total_size_gb - (removed_size / (1024 * 1024 * 1024))) <= max_size_gb:
                    break
                
                try:
                    file_path.unlink()
                    removed_size += file_size
                    removed_files.append(str(file_path))
                except Exception as e:
                    self.logger.warning(f"Failed to remove file {file_path}: {str(e)}")
            
            return {
                'cleaned': True,
                'removed_files': len(removed_files),
                'removed_size_gb': removed_size / (1024 * 1024 * 1024),
                'current_size_gb': total_size_gb - (removed_size / (1024 * 1024 * 1024))
            }
            
        except Exception as e:
            raise Exception(f"Local storage cleanup failed: {str(e)}")
    
    async def _cleanup_cache(self) -> Dict[str, Any]:
        """Clean up cache storage"""
        
        try:
            cache_path = Path(settings.storage.cache_dir)
            max_size_gb = self.storage_config['cache']['max_size_gb']
            cleanup_interval = self.storage_config['cache']['cleanup_interval_hours']
            
            # Calculate current size
            total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
            total_size_gb = total_size / (1024 * 1024 * 1024)
            
            if total_size_gb <= max_size_gb:
                return {
                    'cleaned': False,
                    'reason': 'Cache within limits',
                    'current_size_gb': total_size_gb,
                    'max_size_gb': max_size_gb
                }
            
            # Get file list sorted by access time
            files = []
            cutoff_time = time.time() - (cleanup_interval * 3600)
            
            for file_path in cache_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    stat = file_path.stat()
                    if stat.st_atime < cutoff_time:  # Only consider old files
                        files.append((file_path, stat.st_atime, stat.st_size))
            
            files.sort(key=lambda x: x[1])  # Sort by access time
            
            # Remove old files until under limit
            removed_size = 0
            removed_files = []
            
            for file_path, _, file_size in files:
                if (total_size_gb - (removed_size / (1024 * 1024 * 1024))) <= max_size_gb:
                    break
                
                try:
                    file_path.unlink()
                    removed_size += file_size
                    removed_files.append(str(file_path))
                except Exception as e:
                    self.logger.warning(f"Failed to remove cache file {file_path}: {str(e)}")
            
            return {
                'cleaned': True,
                'removed_files': len(removed_files),
                'removed_size_gb': removed_size / (1024 * 1024 * 1024),
                'current_size_gb': total_size_gb - (removed_size / (1024 * 1024 * 1024))
            }
            
        except Exception as e:
            raise Exception(f"Cache cleanup failed: {str(e)}")
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get storage status and statistics"""
        
        try:
            # Calculate local storage usage
            storage_path = Path(settings.storage.storage_path)
            cache_path = Path(settings.storage.cache_dir)
            
            storage_size = sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file())
            cache_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
            
            # Get provider status
            providers = {
                'local': True,
                's3': self.s3_available,
                'azure': self.azure_available,
                'gcs': self.gcs_available,
                'minio': self.minio_available
            }
            
            return {
                'local_storage': {
                    'enabled': True,
                    'path': str(storage_path),
                    'size_gb': storage_size / (1024 * 1024 * 1024),
                    'max_size_gb': self.storage_config['local']['max_size_gb']
                },
                'cache': {
                    'enabled': True,
                    'path': str(cache_path),
                    'size_gb': cache_size / (1024 * 1024 * 1024),
                    'max_size_gb': self.storage_config['cache']['max_size_gb']
                },
                'providers': providers,
                'cloud_sync': self.storage_config['cloud']['sync_enabled'],
                'primary_provider': self.storage_config['cloud']['primary'],
                'backup_provider': self.storage_config['cloud']['backup']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get storage status: {str(e)}")
            return {
                'error': str(e),
                'error_type': type(e).__name__
            }
