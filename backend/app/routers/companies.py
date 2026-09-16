from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.pagination import Page, PageParams, paginate
from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import Company
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter(
    prefix="/companies", tags=["companies"], dependencies=[Depends(require_api_token)]
)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    company = Company(**payload.model_dump())
    db.add(company)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this domain already exists.",
        )
    db.refresh(company)
    return company


@router.get("", response_model=Page[CompanyRead])
def list_companies(params: PageParams = Depends(), db: Session = Depends(get_db)) -> Page:
    stmt = select(Company).order_by(Company.created_at.desc())
    return paginate(db, stmt, params)


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company