# Approval Service

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pilotdataplatform/approval/Run%20Tests/develop?style=for-the-badge)

## About

Logic for request and approval of files to be copied to core.

## Build With
- Python
- FastAPI
- Postgres

##  Running the service

Configure the setting either in docker-compose or .env

Start API with docker-compose
```
docker-compose up
```

### URLs
Port can be configured in with environment variable `PORT`
- API: http://localhost:8000
- API documentation: http://localhost:8000/v1/api-doc

