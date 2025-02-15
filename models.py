from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String, nullable=False)
    metadata = Column(JSONB, nullable=True)
    text = Column(JSONB, nullable=True)
    processing_status = Column(String, nullable=False)
