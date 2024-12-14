from contextlib import asynccontextmanager
import debugpy
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel
import uvicorn
from core.constants import TITLE, DESCRIPTION, CONTACT, LICENSE_INFO, SWAGGER_UI_PARAMETERS, SWAGGER_FAVICON_URL

from security.api.rest.auth_controller import router as AuthController
from security.api.rest.user_controller import router as UserController

from core.container import Container
from core.default_data import defaultData
from core.database import engine
from core.config import appSettings

logger = logging.getLogger(__name__)

container = Container()

# Lifespan handler para manejar el ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciar tablas de la base de datos...")
    SQLModel.metadata.create_all(engine)
    defaultData(container.userRepository())
    
    logger.info("Configurar el contenedor para la inyección de dependencias...")
    container.wire(modules=[
        "security.api.rest.auth_controller",
        "security.api.rest.user_controller"
    ])

    yield

def create_app():
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version="0.1",
        contact=CONTACT,
        license_info=LICENSE_INFO,
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
        swagger_favicon_url=SWAGGER_FAVICON_URL,
        lifespan=lifespan
    )

    app.include_router(AuthController)
    app.include_router(UserController)
    
    app.add_middleware(
        CORSMiddleware,
        #allow_origins=appSettings.origin_url,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

app = create_app()

@app.get("/", include_in_schema=False, response_class=RedirectResponse)
async def redirect_to_swagger():    
    logger.info("Redirect to swagger...")
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    if appSettings.debug_mode == True:
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    