import uvicorn
from app.main import create_app
from app.config import ConfigClass

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host=ConfigClass.host, port=ConfigClass.port, log_level="info", reload=True)
