from security.domain.model.user import User
from security.mapping.user_mapper import UserMapper
from security.resource.request.register_user_request import RegisterUserRequest
from security.resource.response.auth_response import AuthResponse 
from security.service.auth_service import pwd_context

class AuthMapper:    
    @staticmethod
    def registerRequestToModel(request: RegisterUserRequest) -> User:
        return User(email=request.email, 
                    username=request.username, 
                    hashed_password=pwd_context.hash(request.password.get_secret_value()))
    
    @staticmethod
    def ModelToResponseWithToken(user: User, accessToken: str) -> AuthResponse:
        userResponse = UserMapper.modelToResponse(user)
        return AuthResponse(access_token=accessToken, 
                            token_type="bearer", 
                            user=userResponse)

