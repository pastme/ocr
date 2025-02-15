import os
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from models import UploadedFile
from schemas import FileResponse
from database import SessionLocal, engine, Base

app = FastAPI()

# Directory to store uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Create tables on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")


@app.post("/upload/", response_model=FileResponse)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Create a new database entry to get a unique ID
        new_file = UploadedFile(filepath="")
        db.add(new_file)
        db.flush()  # Assigns an ID to new_file without committing

        # Use the database-generated ID to create a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"file_{new_file.id}"
        if file_extension:
            unique_filename += f".{file_extension}"
        file_location = os.path.join(UPLOAD_DIR, unique_filename)
        content_type = file.content_type

        # Save the file to the filesystem
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())

        # Update the database entry with the file path, and metadata
        new_file.file_metadata = {"request_mimetype": content_type}
        new_file.filepath = file_location
        db.commit()
        db.refresh(new_file)

        return new_file
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
