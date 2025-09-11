## API Endpoints (Backend)

Base URL: `http://127.0.0.1:8000`

Swagger UI: `/docs`

Authentication:
- Access token: Bearer token in `Authorization: Bearer <access_token>` (for protected routes if enabled)
- Refresh token: Bearer token in `Authorization: Bearer <refresh_token>` for `/auth/refresh`

---

### User

#### POST `/user/login`
- Authenticate via ACE API, upsert user, and return tokens and user info.

Request body (JSON):
```json
{
  "account_id": "string",
  "username": "string",
  "password": "string"
}
```

Responses:
- 200 OK — Success
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "guid": "string",
    "user_id": "string",
    "ace_user_id": "string",
    "username": "string",
    "account_id": "string",
    "access_token": "jwt",
    "refresh_token": "jwt"
  },
  "error": null
}
```
- 400 Bad Request — General login failure
```json
{
  "error": "Login Failed",
  "error_code": "LOGIN_FAILED",
  "message": "Reason",
  "data": null
}
```
- 401 Unauthorized — Invalid credentials
```json
{
  "error": "Invalid Credentials",
  "error_code": "INVALID_CREDENTIALS",
  "message": "The provided email/username or password is incorrect",
  "data": null
}
```
- 403 Forbidden — Account locked/disabled
```json
{
  "error": "Account Locked",
  "error_code": "ACCOUNT_LOCKED",
  "message": "Your account has been locked or disabled. Please contact support",
  "data": null
}
```
- 404 Not Found — Invalid account id
```json
{
  "error": "Invalid Account ID",
  "error_code": "INVALID_ACCOUNT_ID",
  "message": "The provided account ID is invalid or does not exist",
  "data": null
}
```
- 500 Internal Server Error — Upstream/service error
```json
{
  "error": "Service Unavailable",
  "error_code": "SERVICE_UNAVAILABLE",
  "message": "Unable to connect to authentication service. Please try again later",
  "data": null
}
```

---

### Auth

#### PATCH `/auth/refresh`
- Given a valid refresh token, returns a new access token.

Security:
- Header: `Authorization: Bearer <refresh_token>`

Responses:
- 200 OK
```json
{
  "success": true,
  "message": "Token refreshed",
  "data": { "access_token": "jwt" },
  "error": null
}
```
- 401 Unauthorized — Missing/invalid refresh token
```json
{
  "error": "Unauthorized",
  "error_code": "INVALID_CREDENTIALS",
  "message": "Missing refresh token",
  "data": null
}
```

---

### Tasks

#### GET `/tasks/{user_id}`
- Fetch tasks assigned to a user.

Path params:
- `user_id` (integer)

Response:
- 200 OK — JSON list/structure of tasks as returned by `TaskService.fetch_assigned_tasks`.

#### POST `/tasks/start`
- Start a task timer.

Request body (JSON) — `TaskStartRequest`:
```json
{
  "task_id": "string",
  "user_id": "string",
  "remarks": "string"
}
```

Response — `TaskStartResponse`:
```json
{
  "message": "Task started",
  "start_time": "ISO-8601"
}
```

#### POST `/tasks/stop`
- Stop a task timer.

Request body (JSON) — `TaskStopRequest`:
```json
{
  "task_id": "string",
  "user_id": "string",
  "remarks": "string"
}
```

Response — `TaskStopMessageResponse`:
```json
{ "message": "Task stopped" }
```

---

### Projects

#### POST `/projects/fetch-projects`
- Fetch projects (via ACE API using `guid`) and persist them locally.

Query/body params:
- `guid` (string)

Responses:
- 200 OK — Returns the output of `ProjectService.fetch_and_store_projects(guid)`.

---

### Conventions
- All successful operations return `SuccessResponse` with:
```json
{ "success": true, "message": "...", "data": { ... }, "error": null }
```
- Errors return `ErrorResponse` with `error`, `error_code`, `message`, and `data: null`.
- For accurate HTTP status codes in Swagger, routes set `response.status_code` based on service-layer results.


