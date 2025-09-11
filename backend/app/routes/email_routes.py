from fastapi import APIRouter, HTTPException
from services.email_service import send_email  # Import the send_email function
from dto.email_dto import EmailRequest  # Import the DTO

router = APIRouter(prefix="/email", tags=["Email"])

@router.post("/send-email")
async def send_email_route(req: EmailRequest):
    try:
        # Correctly extract the email from the request body and pass it to send_email
        send_email(req.to)  # req.to is the email provided in the request body
        
        return {"status": "success", "message": f"Email sent to {req.to}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
