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
from app.models.copy_request_sql import EntityModel, RequestModel
from datetime import datetime


def get_sql_files_recursive(request_id: str, folder_id: str, file_ids: list[str] = None) -> list[EntityModel]:
    if not file_ids:
        file_ids = []

    entities = db.session.query(EntityModel).filter_by(request_id=request_id, parent_id=folder_id)
    for entity in entities:
        if entity.entity_type == "file":
            if entity.review_status == "pending":
                file_ids.append(entity.entity_id)
        else:
            file_ids = get_sql_files_recursive(request_id, entity.entity_id, file_ids=file_ids)
    return file_ids


def get_all_sub_files(request_id: str, entity_ids: list[str]) -> list[str]:
    entities = db.session.query(EntityModel).filter_by(request_id=request_id).filter(
        EntityModel.entity_id.in_(entity_ids)
    )
    file_ids = []
    for entity in entities:
        if entity.entity_type == "file":
            file_ids.append(entity.entity_id)
        else:
            # Get all files in subfolder
            file_ids = get_sql_files_recursive(request_id, entity.entity_id, file_ids=file_ids)
    return file_ids


def get_sql_file_nodes_recursive(request_id: str, folder_id: str, review_status: str, files: list=None) -> list[EntityModel]:
    if not files:
        files = []

    entities = db.session.query(EntityModel).filter_by(request_id=request_id, parent_id=folder_id)
    for entity in entities:
        if entity.entity_type == "file":
            if entity.review_status == review_status:
                files.append(entity.entity_id)
        else:
            files = get_sql_file_nodes_recursive(request_id, entity.entity_id, review_status, files=files)
    return files


def get_all_sub_folder_nodes(request_id: str, entity_ids: list[str], review_status: str) -> list[str]:
    entities = db.session.query(EntityModel).filter_by(request_id=request_id).filter(
        EntityModel.entity_id.in_(entity_ids)
    )
    files = []
    for entity in entities:
        if entity.entity_type == "folder":
            # Get all files in subfolder
            files = get_sql_file_nodes_recursive(request_id, entity.entity_id, review_status, files=files)
    return files


def update_files_sql(request_id: str, review_status: str, username: str, file_ids: list[str]) -> int:
    review_data = {
        "review_status": review_status,
        "reviewed_by": username,
        "reviewed_at": datetime.utcnow(),
    }
    files = db.session.query(EntityModel).filter_by(request_id=request_id).filter(
        EntityModel.entity_id.in_(file_ids)
    )
    files.update(review_data)
    db.session.commit()
    return files.count()


def create_entity_from_node(request_id: str, entity: dict) -> EntityModel:
    # Create entity in psql given meta

    entity_data = {
        "request_id": request_id,
        "entity_id": entity["id"],
        "entity_type": entity["type"],
        "parent_id": entity["parent"],
        "name": entity["name"],
        "uploaded_by": entity["owner"],
        "uploaded_at": entity["created_time"],
        "dcm_id": entity.get("dcm_id"),
    }
    if entity["type"] == "file":
        entity_data["review_status"] = "pending"
        entity_data["file_size"] = entity["size"]
        entity_data["copy_status"] = "pending"
    entity_obj = EntityModel(**entity_data)
    db.session.add(entity_obj)
    db.session.commit()
    return entity_obj
