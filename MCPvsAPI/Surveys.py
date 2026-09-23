"""
Complete Surveys API with CRUD Operations
Uses FastAPI for REST endpoints
Run with: pip install fastapi uvicorn && python surveys_api.py
Then visit: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uvicorn
from uuid import uuid4

# ============ Data Models ============
class SurveyQuestion(BaseModel):
    """Model for survey questions"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    question_text: str
    question_type: str = Field(..., description="Type: 'multiple_choice', 'text', 'rating', 'yes_no'")
    options: Optional[List[str]] = None
    required: bool = True


class SurveyCreate(BaseModel):
    """Model for creating a survey"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    questions: List[SurveyQuestion]
    is_active: bool = True


class Survey(SurveyCreate):
    """Model for complete survey with metadata"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    response_count: int = 0


class SurveyUpdate(BaseModel):
    """Model for updating a survey"""
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[SurveyQuestion]] = None
    is_active: Optional[bool] = None


class SurveyResponse(BaseModel):
    """Model for survey responses"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    survey_id: str
    respondent_email: Optional[str] = None
    answers: dict  # question_id -> answer mapping
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


# ============ In-Memory Database ============
surveys_db: dict[str, Survey] = {}
responses_db: dict[str, SurveyResponse] = {}


# ============ FastAPI App Setup ============
app = FastAPI(
    title="Surveys API",
    description="Complete CRUD API for managing surveys",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ CREATE Endpoints ============
@app.post("/surveys", response_model=Survey, status_code=status.HTTP_201_CREATED, tags=["Surveys"])
def create_survey(survey: SurveyCreate):
    """
    Create a new survey
    
    Args:
        survey: Survey data with title, description, and questions
    
    Returns:
        Created survey with ID and timestamps
    """
    new_survey = Survey(**survey.dict())
    surveys_db[new_survey.id] = new_survey
    return new_survey


@app.post("/surveys/{survey_id}/responses", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED, tags=["Responses"])
def submit_survey_response(survey_id: str, response: SurveyResponse):
    """
    Submit a response to a survey
    
    Args:
        survey_id: ID of the survey
        response: Survey response with answers
    
    Returns:
        Submitted response with timestamp
    """
    if survey_id not in surveys_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    response.survey_id = survey_id
    response_obj = SurveyResponse(**response.dict())
    responses_db[response_obj.id] = response_obj
    
    # Increment response count
    surveys_db[survey_id].response_count += 1
    surveys_db[survey_id].updated_at = datetime.utcnow()
    
    return response_obj


# ============ READ Endpoints ============
@app.get("/surveys", response_model=List[Survey], tags=["Surveys"])
def list_surveys(skip: int = 0, limit: int = 10, is_active: Optional[bool] = None):
    """
    Get list of all surveys with pagination
    
    Args:
        skip: Number of surveys to skip (default: 0)
        limit: Maximum number of surveys to return (default: 10)
        is_active: Filter by active status (optional)
    
    Returns:
        List of surveys
    """
    surveys_list = list(surveys_db.values())
    
    if is_active is not None:
        surveys_list = [s for s in surveys_list if s.is_active == is_active]
    
    return surveys_list[skip : skip + limit]


@app.get("/surveys/{survey_id}", response_model=Survey, tags=["Surveys"])
def get_survey(survey_id: str):
    """
    Get a specific survey by ID
    
    Args:
        survey_id: ID of the survey
    
    Returns:
        Survey details
    """
    if survey_id not in surveys_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    return surveys_db[survey_id]


@app.get("/surveys/{survey_id}/responses", response_model=List[SurveyResponse], tags=["Responses"])
def get_survey_responses(survey_id: str, skip: int = 0, limit: int = 50):
    """
    Get all responses for a specific survey
    
    Args:
        survey_id: ID of the survey
        skip: Number of responses to skip
        limit: Maximum responses to return
    
    Returns:
        List of responses for the survey
    """
    if survey_id not in surveys_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    survey_responses = [r for r in responses_db.values() if r.survey_id == survey_id]
    return survey_responses[skip : skip + limit]


@app.get("/responses/{response_id}", response_model=SurveyResponse, tags=["Responses"])
def get_response(response_id: str):
    """
    Get a specific survey response by ID
    
    Args:
        response_id: ID of the response
    
    Returns:
        Response details
    """
    if response_id not in responses_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response with ID {response_id} not found"
        )
    return responses_db[response_id]


# ============ UPDATE Endpoints ============
@app.put("/surveys/{survey_id}", response_model=Survey, tags=["Surveys"])
def update_survey(survey_id: str, survey_update: SurveyUpdate):
    """
    Update a survey (partial or full update)
    
    Args:
        survey_id: ID of the survey to update
        survey_update: Fields to update
    
    Returns:
        Updated survey
    """
    if survey_id not in surveys_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    survey = surveys_db[survey_id]
    update_data = survey_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(survey, field, value)
    
    survey.updated_at = datetime.utcnow()
    surveys_db[survey_id] = survey
    
    return survey


@app.patch("/surveys/{survey_id}", response_model=Survey, tags=["Surveys"])
def partial_update_survey(survey_id: str, survey_update: SurveyUpdate):
    """
    Partially update a survey (PATCH)
    
    Args:
        survey_id: ID of the survey to update
        survey_update: Fields to update
    
    Returns:
        Updated survey
    """
    return update_survey(survey_id, survey_update)


# ============ DELETE Endpoints ============
@app.delete("/surveys/{survey_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Surveys"])
def delete_survey(survey_id: str):
    """
    Delete a survey and all its responses
    
    Args:
        survey_id: ID of the survey to delete
    
    Returns:
        No content (204)
    """
    if survey_id not in surveys_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    # Delete survey
    del surveys_db[survey_id]
    
    # Delete all responses for this survey
    responses_to_delete = [
        resp_id for resp_id, resp in responses_db.items() 
        if resp.survey_id == survey_id
    ]
    for resp_id in responses_to_delete:
        del responses_db[resp_id]
    
    return None


@app.delete("/responses/{response_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Responses"])
def delete_response(response_id: str):
    """
    Delete a specific survey response
    
    Args:
        response_id: ID of the response to delete
    
    Returns:
        No content (204)
    """
    if response_id not in responses_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response with ID {response_id} not found"
        )
    
    response = responses_db[response_id]
    survey_id = response.survey_id
    
    del responses_db[response_id]
    
    # Decrement response count
    if survey_id in surveys_db:
        surveys_db[survey_id].response_count -= 1
        surveys_db[survey_id].updated_at = datetime.utcnow()
    
    return None


# ============ Health Check ============
@app.get("/", tags=["Health"])
def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "message": "Surveys API is running",
        "surveys_count": len(surveys_db),
        "responses_count": len(responses_db)
    }


@app.get("/stats", tags=["Health"])
def get_stats():
    """Get API statistics"""
    return {
        "total_surveys": len(surveys_db),
        "active_surveys": len([s for s in surveys_db.values() if s.is_active]),
        "total_responses": len(responses_db),
        "average_responses_per_survey": (
            len(responses_db) / len(surveys_db) if surveys_db else 0
        )
    }


# ============ Run Server ============
if __name__ == "__main__":
    print("=" * 60)
    print("Starting Surveys API Server...")
    print("=" * 60)
    print("\n📍 API will be available at: http://localhost:8000")
    print("📚 Interactive Docs: http://localhost:8000/docs")
    print("📋 Alternative Docs: http://localhost:8000/redoc")
    print("\n" + "=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")