from pydantic import BaseModel, EmailStr, SecretStr

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: SecretStr# Permite que el rol se especifique opcionalmente

class EmailVerificationRequest(BaseModel):
    verification_uuid: str

class PasswordResetRequestByEmail(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    verification_uuid: str
    password: SecretStr