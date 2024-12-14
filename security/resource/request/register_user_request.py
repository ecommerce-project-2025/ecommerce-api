from pydantic import BaseModel, EmailStr, SecretStr

class RegisterUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: SecretStr
    # image_url: str
    # full_name: str
    
