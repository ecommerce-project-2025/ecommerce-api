from dependency_injector import containers, providers
from security.domain.persistence.user_repository import UserRepository
from security.service.auth_service import AuthService
from security.service.email_service import EmailService
from security.service.user_service import UserService

class Container(containers.DeclarativeContainer):
    # Repositories
    userRepository = providers.Factory(UserRepository)
    # robotRepository = providers.Factory(RobotRepository)
    # servoGroupRepository = providers.Factory(ServoGroupRepository)
    # movementRepository = providers.Factory(MovementRepository)
    # positionRepository = providers.Factory(PositionRepository)
    
    # Services
    emailService = providers.Factory(EmailService)
    userService = providers.Factory(UserService, userRepository=userRepository)
    authService = providers.Factory(AuthService, userRepository=userRepository, emailService=emailService)
    
    # robotService  = providers.Factory(RobotService, robotRepository=robotRepository, movementRepository=movementRepository, positionRepository=positionRepository)
    # servoGroupService = providers.Factory(ServoGroupService, servoGroupRepository=servoGroupRepository)
    # movementService = providers.Factory(MovementService, movementRepository=movementRepository)
    # positionService = providers.Factory(PositionService, positionRepository=positionRepository)
    