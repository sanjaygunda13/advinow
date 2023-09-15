import uvicorn
from fastapi import FastAPI # need python-multipart
import views
import os
app = FastAPI(title="AdviNow Interview Challenge", version="1.6")

app.include_router(views.router)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8013)
