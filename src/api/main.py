from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from src.race_parser import RaceParser

app = FastAPI(
    title="ThroneButt Parser API",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

class Participant(BaseModel):
    rank: str
    name: str
    distance: str
    kills: str

class RaceParams(BaseModel):
    race_type: str = Field(...)
    year: str = Field(...)
    identifier: str = Field(...)
    page: str = Field("1")
    debug: bool = Field(False)
    all_pages: bool = Field(False)

@app.post("/parse", response_model=List[Participant])
async def parse_race(params: RaceParams):
    try:
        if params.race_type == "daily" and "/" not in params.identifier:
            raise HTTPException(
                status_code=400,
            )
        
        if params.race_type == "daily":
            month, day = params.identifier.split('/')
            identifier = (month, day)
        else:
            identifier = params.identifier
        
        if params.all_pages:
            participants = []
            current_page = 1
            
            while True:
                page_data = await RaceParser.parse_race(
                    params.race_type,
                    params.year,
                    identifier,
                    str(current_page),
                    params.debug
                )
                
                if not page_data:
                    break
                
                participants.extend(page_data)
                current_page += 1
            
            return participants
        else:
            return await RaceParser.parse_race(
                params.race_type,
                params.year,
                identifier,
                params.page,
                params.debug
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API works"}
