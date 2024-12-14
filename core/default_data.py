from datetime import datetime, timezone
import uuid
from security.domain.model.user import User, Role
from security.domain.persistence.user_repository import UserRepository
from security.service.auth_service import pwd_context
from core.config import dbSettings

def defaultData(userRepository: UserRepository):
    if not userRepository.findByEmail(dbSettings.initial_admin_email):
        userRepository.save(User(
            verification_uuid=str(uuid.uuid4()),
            email=dbSettings.initial_admin_email,
            username=dbSettings.initial_admin_username, 
            hashed_password=pwd_context.hash(dbSettings.initial_admin_password), 
            email_verified_at=datetime.now(timezone.utc),
            role=Role.ADMIN))
