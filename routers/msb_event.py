from typing import Annotated, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Users, CompanyEventScheduler
from database import get_db
from services.auth_service import get_current_user
from utils.date_utils import get_current_date

router = APIRouter(
    prefix='/msb-event',
    tags=['msb-event-api']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class EventFilter(BaseModel):
    company_name: Optional[str] = None
    event_object: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[int] = None


@router.post("/filter-event", status_code=status.HTTP_200_OK)
async def get_event_by_filter(user: user_dependency,
                              db: db_dependency,
                              event_filter: EventFilter):
    # Authen
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    # Author
    # if user.get("user_role") not in ['MANAGER', 'ADMIN']:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Authorization Failed, Only for MANAGER role')

    # Main Logic
    try:
        query = db.query(CompanyEventScheduler)

        if event_filter.company_name or event_filter.company_name.strip() == "":
            query = query.filter(CompanyEventScheduler.company_name.ilike(f"%{event_filter.company_name}%"))

        if event_filter.event_object or event_filter.event_object.strip() == "":
            query = query.filter(CompanyEventScheduler.event_object.ilike(f"%{event_filter.event_object}%"))

        if event_filter.event_type or event_filter.event_type.strip() == "":
            query = query.filter(CompanyEventScheduler.event_type == event_filter.event_type)

        if event_filter.event_date == get_current_date():
            pass
        else:
            query = query.filter(CompanyEventScheduler.event_year == event_filter.event_date//10000,
                                 CompanyEventScheduler.event_month == (event_filter.event_date % 10000) // 100,
                                 CompanyEventScheduler.event_day == event_filter.event_date % 100
                                 )

        print(query)

        return {
            "error": "",
            "data": query.all()
        }

    except Exception as e:
        return {
            "error": str(e),
            "data": []
        }