import ast
from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, computed_field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Users, CompanyEventScheduler
from database import get_db
from services.auth_service import get_current_user
from utils.date_utils import get_current_date
from decouple import config

router = APIRouter(
    prefix='/msb-event',
    tags=['msb-event-api']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class EventFilterForm(BaseModel):
    company_name: Optional[str] = None
    event_object: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[int] = None


class EventSchemaResponse(BaseModel):
    id: int
    company_name: str
    event_day: int
    event_month: int
    event_year: int
    event_type: str
    event_object: str
    event_title: str
    event_position: str
    promt: str
    received_email: str
    is_active: bool
    is_loop: bool
    create_time: datetime

    @computed_field
    @property
    def full_event(self) -> str:
        return f"{self.event_day}-{self.event_month}-{self.event_year}"

    model_config = {
        "from_attributes": True
    }


class Response(BaseModel):
    error: str
    data: list[EventSchemaResponse]


@router.post("/filter-event", status_code=status.HTTP_200_OK, response_model=Response)
async def get_event_by_filter(user: user_dependency,
                              db: db_dependency,
                              event_filter: EventFilterForm):
    # Authen
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    # Author
    # if user.get("user_role") not in ['MANAGER', 'ADMIN']:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Authorization Failed, Only for MANAGER role')

    # Main Logic
    try:
        query = db.query(CompanyEventScheduler)

        if event_filter.company_name and event_filter.company_name.strip() != "":
            query = query.filter(CompanyEventScheduler.company_name.ilike(f"%{event_filter.company_name}%"))

        if event_filter.event_object and event_filter.event_object.strip() != "":
            query = query.filter(CompanyEventScheduler.event_object.ilike(f"%{event_filter.event_object}%"))

        if event_filter.event_type and event_filter.event_type.strip() != "":
            query = query.filter(CompanyEventScheduler.event_type == event_filter.event_type)

        if event_filter.event_date == get_current_date():
            pass
        else:
            query = query.filter(CompanyEventScheduler.event_year == event_filter.event_date // 10000,
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


# Api cho phép manager tạo tài khoản shipper
class CreateEventForm(BaseModel):
    company_name: str
    event_object: str
    event_title: str
    event_position: str
    event_type: str
    promt: str
    input_date: int
    received_email: str
    is_loop: bool


@router.post("/create-event", status_code=status.HTTP_201_CREATED)
async def create_an_event(user: user_dependency,
                          db: db_dependency,
                          create_event: CreateEventForm):
    # Main Logic
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

        create_event_model = CompanyEventScheduler(
            company_name=create_event.company_name,
            event_day=create_event.input_date % 100,
            event_month=(create_event.input_date % 10000) // 100,
            event_year=create_event.input_date // 10000,
            event_type=create_event.event_type,
            event_object=create_event.event_object,
            event_title=create_event.event_title,
            event_position=create_event.event_position,
            promt=create_event.promt,
            received_email=create_event.received_email,
            is_active=True,
            is_loop=create_event.is_loop
        )

        db.add(create_event_model)
        db.commit()

        return {
            "error": "",
            "message": "Sự kiện đã được tạo thành công",
            "data": []
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Có lỗi không mong muốn xảy ra",
            "data": []
        }


import requests
import json

@router.post("/preview-event", status_code=status.HTTP_200_OK)
async def preview_an_event(user: user_dependency,
                           db: db_dependency,
                           create_event: CreateEventForm):
    # Main Logic
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

        event = CompanyEventScheduler(
            company_name=create_event.company_name,
            event_day=create_event.input_date % 100,
            event_month=(create_event.input_date % 10000) // 100,
            event_year=create_event.input_date // 10000,
            event_type=create_event.event_type,
            event_object=create_event.event_object,
            event_title=create_event.event_title,
            event_position=create_event.event_position,
            promt=create_event.promt,
            received_email=create_event.received_email,
            is_active=True,
            is_loop=create_event.is_loop
        )

        # if event.event_type == 'BIRTH_DATE':
        #     inp_event_type = "chúc mừng sinh nhật"
        # elif event.event_type == 'FOUNDING_DATE':
        #     inp_event_type = "chúc mừng ngày thành lập doanh nghiệp"
        # elif event.event_type == 'ACTIVE_DATE':
        #     inp_event_type = "nhắc khách hàng kích hoạt hạn mức"

        headers = {
            "Authorization": f"Bearer {config('OPEN_API_KEY')}",
            "Content-Type": "application/json"
        }

        if event.event_type == 'BIRTH_DATE':
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Bạn là một người đại diện cho ngân hàng TMCP hàng hải MSB và là người chăm sóc khách hàng"},
                    {
                        "role": "user",
                        "content": f""" Hãy viết cho tôi một email hoàn chỉnh để chúc mừng sinh nhật cho {event.event_title} {event.event_object}
                                        hiện đang là {event.event_position} tại doanh nghiệp có tên là {event.company_name}.
                                        Hãy chú ý viết theo các yêu cầu sau:
                                        - {event.promt}
                                        - Phần email closing chỉ cần ghi là "Ngân hàng TMCP Hàng Hải MSB", không cần để sẵn biến để tôi thay thế
                                        - Ngắn gọn khoảng 5-7 câu
                                        - Chú ý không sử dụng từ "năm mới hoặc năm nay" do dịch tiếng anh sang tiếng việt
                                        - Trả lời kết quả dưới dạng json như sau và không trả gì thêm ngoài json
                                        {{   
                                            "subject": "Dòng tiêu đề mail",
                                            "body_html": "Nội dung email ở định dạng HTML"
                                        }}
                                        """
                    }
                ]
            }

        elif event.event_type == 'FOUNDING_DATE':

            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system",
                     "content": "Bạn là một người đại diện cho ngân hàng TMCP hàng hải MSB và là người chăm sóc khách hàng"},
                    {
                        "role": "user",
                        "content": f""" Trên vai trò là người đại diện của ngân hàng TMCP MSB và là người chăm sóc khách hàng hãy viết cho tôi một email hoàn chỉnh để 
                                        cảm ơn và chúc mừng nhân ngày thành lập thứ {datetime.now().year - event.event_year} của doanh nghiệp có tên là {event.company_name}.
                                        Hãy chú ý viết theo các yêu cầu sau:
                                        - {event.promt}
                                        - Phần email closing chỉ cần ghi là "Ngân hàng TMCP Hàng Hải MSB", không cần để sẵn biến để tôi thay thế
                                        - Ngắn gọn khoảng 8-10 câu
                                        - Trả lời kết quả dưới dạng JSON như sau và không trả gì thêm ngoài Json
                                        {{   
                                            "subject": "Dòng tiêu đề mail",
                                            "body_html": "Nội dung email ở định dạng HTML"
                                        }}
                                        """
                    }
                ]
            }

        # Call OpenAI:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            verify=False
        )
        reply = response.json()
        print(reply)
        intermediate = ast.literal_eval(reply['choices'][0]['message']['content'].replace("```json", "").replace("```",""))
        # result_data = json.loads(intermediate)

        return {
            "error": "",
            "message": "Sự kiện đã được tạo thành công",
            "data": intermediate
        }

    # except Exception as e:
    except Warning as e:
        return {
            "error": str(e),
            "message": "Có lỗi không mong muốn xảy ra",
            "data": []
        }