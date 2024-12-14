from datetime import datetime, timedelta, timezone
import uuid
from fastapi import BackgroundTasks, HTTPException, status
import jwt
from security.domain.persistence.user_repository import UserRepository
from security.domain.model.user import Role, User
from passlib.context import CryptContext 
from core.config import securitySettings
from security.service.email_service import EmailService

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    def __init__(self, userRepository: UserRepository, emailService: EmailService):
        self.repository = userRepository
        self.emailService = emailService
    
    def register(self, user: User, background_tasks: BackgroundTasks):
        if self.repository.findByEmail(user.email) or self.repository.findByUsername(user.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        
        user.verification_uuid = self.generateUUID()

        saved_user = self.repository.save(user)
        
        # Create the verification link
        verification_url = f"{securitySettings.origin_url}/login?uuid={saved_user.verification_uuid}"
        self.emailService.sendEmailVerification(saved_user.email, "Email Verification", verification_url, background_tasks)
        
        return saved_user
    
    def authenticate(self, email: str, password: str):
        user = self.repository.findByEmail(email)
        
        if not user or not self.verifyPassword(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        if not user.email_verified_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")
        
        return user
    
    def createJWToken(self, email: str):
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(minutes=securitySettings.access_token_expire_minutes)
        }
        return jwt.encode(payload=payload, key=securitySettings.secret_key, algorithm=securitySettings.algorithm)

    def validateJWToken(self, token: str):
        try:
            payload = jwt.decode(token, securitySettings.secret_key, algorithms=[securitySettings.algorithm])
            email: str = payload.get("email")
            print(f"Decoded email: {email}")
            if email is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            user = self.repository.findByEmail(email)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return user
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    def authorizeRoles(self, user: User, roles: list[Role]):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return True
    
    def hashPassword(self, password: str):
        return pwd_context.hash(password)

    def verifyPassword(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)
    

    def verifyEmail(self, verificationUuid: str):
        user = self.repository.findByVerificationUuid(verificationUuid)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if user.email_verified_at:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already verified")
        
        user.email_verified_at = datetime.now(timezone.utc)
        user.verification_uuid = self.generateUUID()
        self.repository.save(user)

        return True
    
    def sendEmailToResetPassword(self, email: str, background_tasks: BackgroundTasks):
        user = self.repository.findByEmail(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not user.email_verified_at:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User not verified")
        
        # Create the verification link
        verification_url = f"{securitySettings.origin_url}/reset-password?uuid={user.verification_uuid}"
        self.emailService.sendPasswordReset(user.email, "Email Verification", verification_url, background_tasks)
        
        return True

    def resetPassword(self, verificationUuid: str, newHashedPassword: str):
        user = self.repository.findByVerificationUuid(verificationUuid)
        
        if not user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User not found")
        
        if not user.email_verified_at:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User not verified")

        user.hashed_password = newHashedPassword
        user.verification_uuid = self.generateUUID()
        self.repository.save(user)
        
        return True
    
    def generateUUID(self):
        uniqueUuid = str(uuid.uuid4())
        while self.repository.findByVerificationUuid(uniqueUuid):
            uniqueUuid = str(uuid.uuid4())
        return uniqueUuid