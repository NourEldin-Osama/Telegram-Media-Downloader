from pydantic import BaseModel


class DownloadStatistics(BaseModel):
    total_downloads: int = 0
    skipped_files: int = 0
    filtered_files: int = 0
    failed_downloads: int = 0
