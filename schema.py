import strawberry
from typing import List, Optional
from services.ai_service import analyze_job_fit
from services.firestore_service import db
import datetime
from dataclasses import dataclass

@strawberry.type
@dataclass
class JobAnalysis:
    match_score: int
    fit_summary: str
    strengths: List[str]
    missing_skills: List[str]
    recommendations: List[str]
    application_email: str

@strawberry.type
@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    description: str
    saved_at: str
    analysis: Optional[JobAnalysis] = None

@strawberry.type
class Query:
    @strawberry.field
    def jobs(self) -> List[Job]:
        if not db:
            return []
        
        jobs_ref = db.collection("jobs").order_by("saved_at", direction="DESCENDING")
        docs = jobs_ref.stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            analysis_data = data.get("analysis")
            analysis = None
            if analysis_data:
                analysis = JobAnalysis(
                    match_score=analysis_data.get("match_score", 0),
                    fit_summary=analysis_data.get("fit_summary", ""),
                    strengths=analysis_data.get("strengths", []),
                    missing_skills=analysis_data.get("missing_skills", []),
                    recommendations=analysis_data.get("recommendations", []),
                    application_email=analysis_data.get("application_email", "")
                )
            
            results.append(Job(
                id=doc.id,
                title=data.get("title", ""),
                company=data.get("company", ""),
                location=data.get("location", ""),
                description=data.get("description", ""),
                saved_at=data.get("saved_at", ""),
                analysis=analysis
            ))
        return results

from utils.pdf_parser import extract_text_from_pdf

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def analyze_job(
        self,
        title: str,
        company: str,
        location: str,
        description: str,
        resume_base64: str
    ) -> Job:
        # 1. Extract text from resume
        try:
            resume_text = extract_text_from_pdf(resume_base64)
        except Exception as e:
            # Fallback if it's already text or extraction fails
            resume_text = resume_base64 
        
        # 2. AI Analysis
        analysis_result = analyze_job_fit(resume_text, description, job_title=title, company_name=company)
        
        analysis = JobAnalysis(
            match_score=analysis_result.get("match_score", 0),
            fit_summary=analysis_result.get("fit_summary", ""),
            strengths=analysis_result.get("strengths", []),
            missing_skills=analysis_result.get("missing_skills", []),
            recommendations=analysis_result.get("recommendations", []),
            application_email=analysis_result.get("application_email", "")
        )
        
        # 2. Prepare Data
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "saved_at": datetime.datetime.now().isoformat(),
            "analysis": {
                "match_score": analysis.match_score,
                "fit_summary": analysis.fit_summary,
                "strengths": analysis.strengths,
                "missing_skills": analysis.missing_skills,
                "recommendations": analysis.recommendations,
                "application_email": analysis.application_email
            }
        }
        
        # 3. Store in Firestore
        if db:
            doc_ref = db.collection("jobs").document()
            doc_ref.set(job_data)
            job_id = doc_ref.id
        else:
            job_id = "temp_id"
            
        return Job(
            id=job_id,
            title=title,
            company=company,
            location=location,
            description=description,
            saved_at=job_data["saved_at"],
            analysis=analysis
        )

schema = strawberry.Schema(query=Query, mutation=Mutation)
