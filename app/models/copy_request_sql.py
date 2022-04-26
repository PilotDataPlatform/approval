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
from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, Date, DateTime, Integer, Boolean, ForeignKey, BigInteger
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.config import ConfigClass
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class RequestModel(Base):
    __tablename__ = "approval_request"
    __table_args__ = {"schema": ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    status = Column(String())
    submitted_by = Column(String())
    submitted_at = Column(DateTime(), default=datetime.utcnow)
    destination_id = Column(UUID(as_uuid=True))
    source_id = Column(UUID(as_uuid=True))
    note = Column(String())
    project_code = Column(String())
    destination_path = Column(String())
    source_path = Column(String())
    review_notes = Column(String())
    completed_by = Column(String())
    completed_at = Column(DateTime())

    def to_dict(self):
        result = {}
        for field in self.__table__.columns.keys():
            if field in ["submitted_at", "completed_at"]:
                if getattr(self, field):
                    result[field] = str(getattr(self, field).isoformat()[:-3] + 'Z')
                else:
                    result[field] = None
            elif field in ["id", "destination_id", "source_id"]:
                result[field] = str(getattr(self, field))
            else:
                result[field] = getattr(self, field)
        return result


class EntityModel(Base):
    __tablename__ = "approval_entity"
    __table_args__ = {"schema": ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey(RequestModel.id))
    entity_id = Column(UUID(as_uuid=True))
    entity_type = Column(String())
    review_status = Column(String())
    reviewed_by = Column(String())
    reviewed_at = Column(String())
    parent_id = Column(UUID(as_uuid=True))
    copy_status = Column(String())
    name = Column(String())
    uploaded_by = Column(String(), nullable=True)
    dcm_id = Column(String(), nullable=True)
    uploaded_at = Column(DateTime(), default=datetime.utcnow)
    file_size = Column(BigInteger(), nullable=True)

    def to_dict(self):
        result = {}
        for field in self.__table__.columns.keys():
            if field == "uploaded_at":
                result[field] = str(getattr(self, field).isoformat()[:-3] + 'Z')
            elif field in ["id", "request_id", "entity_id", "parent_id"]:
                result[field] = str(getattr(self, field))
            else:
                result[field] = getattr(self, field)
        return result

