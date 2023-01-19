import typing as t

import uvicorn

from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from outline_vpn.outline_vpn import OutlineVPN


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    if not ApiUrl:
        return templates.TemplateResponse("sign-in.html", {"request": request})

    outline_client = OutlineVPN(api_url=ApiUrl)

    data = {
        'request': request,
        'server_information': outline_client.get_server_information(),
        'keys': outline_client.get_keys(),
    }

    return templates.TemplateResponse("main.html", data)


@app.post("/sign-in", response_class=HTMLResponse)
async def root(request: Request, ApiUrl: str = Form()):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    response.set_cookie(key='ApiUrl', value=ApiUrl)
    return response


@app.post("/new-key", response_class=HTMLResponse)
async def create_new_key(request: Request, newKeyName: str = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.create_key(newKeyName)

    return response


@app.get("/logout", response_class=HTMLResponse)
async def root(request: Request):
    response = RedirectResponse('/')
    response.delete_cookie('ApiUrl')
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
