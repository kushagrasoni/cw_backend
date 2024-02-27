from pydantic import BaseModel, FilePath, validator

class FileData(BaseModel):
    target_table: str
    file: FilePath

    @validator("file")
    def validate_file(cls, v):
        # Add validation logic for the file (optional)
        # For example, check allowed extensions or file size
        return v
