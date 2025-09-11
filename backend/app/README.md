## Backend (FastAPI) - Project Guide

This document covers setup, configuration, run/deploy, authentication (access/refresh tokens), response DTOs, database migrations with Alembic, and troubleshooting for the backend app.

### Tech Stack
- FastAPI, Pydantic
- SQLAlchemy ORM
- Alembic (migrations)
- PostgreSQL (via `DATABASE_URL`)
- jose (JWT)

### Project Structure (key paths)
```
backend/app/
  auth/
    jwt_handler.py         # create/decode JWTs
    security.py            # password hashing/verification (if used)
  connection/
    database.py            # SQLAlchemy engine, SessionLocal, Base
  dependencies/
    get_db.py              # DB session dependency
    auth_dependencies.py   # auth/role dependencies (e.g., require_roles)
  dto/
    response.py            # SuccessResponse, ErrorResponse, ErrorCode
    user_dto.py            # UserRequest for login
    task.py                # Task-related DTOs
  models/
    users.py, projects.py, tasks.py, task_assignees.py, task_logs.py
  routes/
    user_routes.py         # /user/login
    auth_routes.py         # /auth/login, /auth/refresh (if enabled)
    project_routes.py, task_routes.py, save_route.py, report_routes.py
  services/
    user_services.py       # Login via ACE API, create tokens, upsert user
    auth_service.py        # Token refresh
    project_service.py, task_service.py, data_service.py
  alembic/                 # Alembic migrations
  main.py                  # FastAPI app factory & router registration
```

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Windows commands below assume running from `backend/app` and venv at `fastapienv` (already included in the repo).

### Environment Variables (.env)
Set in `backend/app/.env` (example):
```
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
ACE_API_URL=https://your-ace-api/login

SECRET_KEY=your-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Install & Run
```
cd backend\app
fastapienv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
App runs on `http://127.0.0.1:8000` with docs at `/docs`.

### Response DTOs
File: `dto/response.py`
```python
class ErrorResponse(BaseModel):
    error: str
    error_code: ErrorCode        # e.g. INVALID_CREDENTIALS, INVALID_ACCOUNT_ID, ...
    message: str
    data: Optional[Any] = None

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
```

Typical error example:
```json
{
  "error": "Invalid Credentials",
  "error_code": "INVALID_CREDENTIALS",
  "message": "The provided email/username or password is incorrect",
  "data": null
}
```

### Authentication
Token utilities: `auth/jwt_handler.py`
- `create_access_token({"sub": guid, "role": role, "type": "access"})`
- `create_refresh_token({"sub": guid, "type": "refresh"})`
- `decode_token(token)`

Login flow: `services/user_services.py`
- Calls ACE API with account id, username, password
- On failure: returns `ErrorResponse` with specific `error_code`
- On success: upserts `Users` record and returns `SuccessResponse` with:
  - `guid`, `user_id`, `ace_user_id`, `username`, `account_id`
  - `access_token`, `refresh_token`

Refresh flow: `services/auth_service.py`
```python
payload = decode_token(refresh_token)
if payload.get("type") != "refresh":
    raise HTTPException(status_code=401, detail="Invalid token type")
new_access = create_access_token({"sub": payload["sub"], "type": "access"})
return {"access_token": new_access}
```

Optional role guard: `dependencies/auth_dependencies.py`
```python
@router.get("/admin", dependencies=[Depends(require_roles(RoleEnum.admin))])
def admin_only():
    ...
```

### Key Endpoints
- `POST /user/login` → `SuccessResponse | ErrorResponse`
  - Returns access/refresh tokens on success
- `PATCH /auth/refresh` → returns new access token (requires refresh token)
- `GET /tasks/{user_id}` → fetch tasks
- `POST /projects/fetch-projects` → fetch and persist projects from ACE
- `POST /data/save` → batch-save entities (users/projects/tasks/assignees)

Swagger UI: `http://127.0.0.1:8000/docs`

### HTTP Status Codes in Swagger
To surface correct status codes (e.g., 401/403/404), either:
1) Return `(dto, status_code)` from services and set `response.status_code` in routes, or
2) Raise `HTTPException` with `detail` aligned to your DTO (if you prefer exceptions).

Current project pattern uses DTOs; routes can set the status based on service result as needed.

### Database & Alembic
Model Base: `connection/database.py` → `Base = declarative_base()`
Alembic metadata: `alembic/env.py` → `target_metadata = Base.metadata`

Create/apply migrations (Windows CMD from `backend/app`):
```
fastapienv\Scripts\activate
set DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
alembic upgrade head
```
Autogenerate new migration after model changes:
```
alembic revision --autogenerate -m "sync models"
alembic upgrade head
``;
Other useful:
```
alembic current
alembic history
alembic downgrade -1
```

### Troubleshooting
- ModuleNotFoundError: `from db import Base` → Fix imports to `from connection.database import Base`
- Status code always 200 in Swagger → set `response.status_code` in route based on service return
- JWT invalid on refresh → ensure `type` claim is `refresh`; verify `SECRET_KEY/ALGORITHM`
- Env not picked up by Alembic → in `alembic/env.py`, set `config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))`

### Testing (placeholder)
- Run test suite (if configured): `pytest` from `backend/app`

### License
Internal training project; no license specified.


