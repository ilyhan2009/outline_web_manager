import datetime
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

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=90)

    response.set_cookie(key='ApiUrl', value=ApiUrl, expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    return response


@app.post("/add", response_class=HTMLResponse)
async def create_new_key(request: Request, newKeyName: str = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.create_key(newKeyName)

    return response


@app.post("/rename/{key_id}", response_class=HTMLResponse)
async def rename_key_name(request: Request, key_id: int, keyName: str = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.rename_key(key_id, keyName)

    return response


@app.get("/delete/{key_id}", response_class=HTMLResponse)
async def delete_key(request: Request, key_id: int, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/')

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.delete_key(key_id)

    return response


@app.post("/set-data-limit", response_class=HTMLResponse)
async def delete_key(request: Request, dataLimitForAllKeys: int = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.set_data_limit_for_all_keys(dataLimitForAllKeys * 1000 * 1000 * 1000)

    return response


@app.get("/delete-data-limit", response_class=HTMLResponse)
async def delete_key(request: Request, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/')

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.delete_data_limit_for_all_keys()

    return response


@app.post("/set-data-limit/{key_id}/{limit}", response_class=HTMLResponse)
async def delete_key(request: Request, key_id: int, limit: int, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.add_data_limit(key_id, limit)

    return response


@app.get("/delete-data-limit/{key_id}", response_class=HTMLResponse)
async def delete_key(request: Request, key_id: int, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/')

    try:
        outline_client = OutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.delete_data_limit(key_id)

    return response


@app.get("/logout", response_class=HTMLResponse)
async def root(request: Request):
    response = RedirectResponse('/')
    response.delete_cookie('ApiUrl')
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
