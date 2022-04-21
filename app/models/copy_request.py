# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import uuid

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.resources.error_handler import APIException
from .base import APIResponse
from .base import EAPIResponseCode
from .base import PaginationRequest


class POSTRequest(BaseModel):
    entity_geids: list[str]
    destination_geid: str
    source_geid: str
    note: str
    submitted_by: str

    @validator('note')
    def valid_note(cls, value):
        if value == "":
            raise APIException(EAPIResponseCode.bad_request.value, "Note is required")
        return value


class POSTRequestResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': "success",
        'total': 1
    })


class GETRequest(PaginationRequest):
    status: str
    submitted_by: str = None


class GETRequestResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': [],
        'total': 1
    })


class GETRequestFiles(PaginationRequest):
    request_id: uuid.UUID
    parent_geid: str = ""
    query: str = "{}"
    partial: str = "[]"
    order_by: str = "uploaded_at"

    @validator('query', 'partial')
    def valid_json(cls, value):
        try:
            value = json.loads(value)
        except Exception as e:
            error_msg = f"query or partial json is not valid"
            raise APIException(EAPIResponseCode.bad_request.value, f"Invalid json: {value}")
        return value


class GETRequestFilesResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': [],
        'total': 1
    })


class PUTRequest(BaseModel):
    request_id: uuid.UUID
    status: str
    review_notes: str = ""
    username: str

    @validator('status')
    def valid_status(cls, value):
        if value != "complete":
            raise APIException(EAPIResponseCode.bad_request.value, "invalid review status")
        return value


class PUTRequestFiles(BaseModel):
    request_id: uuid.UUID
    review_status: str
    session_id: str
    username: str

    @validator('review_status')
    def valid_review_status(cls, value):
        if value not in ["approved", "denied"]:
            raise APIException(EAPIResponseCode.bad_request.value, "invalid review status")
        return value


class PATCHRequestFiles(BaseModel):
    entity_geids: list[str]
    request_id: uuid.UUID
    review_status: str
    username: str
    session_id: str

    @validator('review_status')
    def valid_review_status(cls, value):
        if value not in ["approved", "denied"]:
            raise APIException(EAPIResponseCode.bad_request.value, "invalid review status")
        return value


class PUTRequestFilesResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': [],
        'total': 1
    })


class GETRequestPending(BaseModel):
    request_id: uuid.UUID


class GETPendingResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': {
            "pending_count": 1,
            "pending_entities": ["geid"],
        },
        'total': 1
    })
