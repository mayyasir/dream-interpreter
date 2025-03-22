from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to ["http://localhost:3002"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Gemini API Key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# **Database Setup**
DATABASE_URL = "sqlite:///./dreams.db"  # Using SQLite for now
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# **Dream Model**
class Dream(Base):
    __tablename__ = "dreams"

    id = Column(Integer, primary_key=True, index=True)
    dream_text = Column(String, nullable=False)
    interpretation = Column(String, nullable=False)
    emotion = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define request model
class DreamRequest(BaseModel):
    dream_text: str

# Define response model
class DreamResponse(BaseModel):
    dream_text: str
    interpretation: str
    emotion: str
    confidence: float

# **Define API endpoint to interpret dreams and save to DB**
@app.post("/analyze_dream", response_model=DreamResponse)
async def analyze_dream(dream: DreamRequest, db: Session = Depends(get_db)):
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Create the prompt
        prompt = f"""
        You are an AI dream interpreter. Please interpret this dream:
        {dream.dream_text}

        Also, analyze the primary emotion behind this dream 
        and provide a confidence score between 0 and 1.

        Format your response like this:
        Interpretation: [Your interpretation]
        Emotion: [Primary emotion]
        Confidence: [A number between 0 and 1]
        """

        # Generate response
        response = model.generate_content(prompt)

        # Extract and parse response
        if response and hasattr(response, "text"):
            result = response.text.strip()
        else:
            result = "No interpretation available."

        # Default values
        interpretation = result
        emotion = "Unknown"
        confidence = 0.5

        # Parse structured response
        try:
            parts = result.split("Emotion:")
            interpretation = parts[0].strip()

            if len(parts) > 1:
                emotion_confidence = parts[1].split("Confidence:")
                emotion = emotion_confidence[0].strip()
                confidence = float(emotion_confidence[1].strip())
        except:
            pass  # If parsing fails, keep default values

        # **Save to the database**
        new_dream = Dream(
            dream_text=dream.dream_text,
            interpretation=interpretation,
            emotion=emotion,
            confidence=confidence
        )
        db.add(new_dream)
        db.commit()
        db.refresh(new_dream)

        return new_dream

    except Exception as e:
        error_message = str(e)
        if "API key" in error_message:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key. Please check your Gemini API key."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while processing your request: {error_message}"
            )

# **New Endpoint to Retrieve Past Dream History**
@app.get("/dream_history")
def get_dream_history(db: Session = Depends(get_db)):
    dreams = db.query(Dream).all()
    return dreams

# Run the API (only for local testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)