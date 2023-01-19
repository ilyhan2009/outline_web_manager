import datetime
from dataclasses import dataclass
import requests
import typing as t

import uvicorn

from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from outline_vpn.outline_vpn import OutlineVPN, OutlineKey


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@dataclass
class PatchedOutlineKey(OutlineKey):
    data_limit: int


class PatchedOutlineVPN(OutlineVPN):
    def get_keys(self):
        """Get all keys in the outline server"""
        response = requests.get(f"{self.api_url}/access-keys/", verify=False)
        if response.status_code == 200 and "accessKeys" in response.json():
            response_metrics = requests.get(
                f"{self.api_url}/metrics/transfer", verify=False
            )
            if (
                response_metrics.status_code >= 400
                or "bytesTransferredByUserId" not in response_metrics.json()
            ):
                raise Exception("Unable to get metrics")

            response_json = response.json()
            result = []
            for key in response_json.get("accessKeys"):
                result.append(
                    PatchedOutlineKey(
                        key_id=key.get("id"),
                        name=key.get("name"),
                        password=key.get("password"),
                        port=key.get("port"),
                        method=key.get("method"),
                        access_url=key.get("accessUrl"),
                        data_limit=key.get('dataLimit', {}).get('bytes'),
                        used_bytes=response_metrics.json()
                        .get("bytesTransferredByUserId")
                        .get(key.get("id")),
                    )
                )
            return result
        raise Exception("Unable to retrieve keys")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    if not ApiUrl:
        return templates.TemplateResponse("sign-in.html", {"request": request})

    outline_client = PatchedOutlineVPN(api_url=ApiUrl)

    transferred_data = outline_client.get_transferred_data()

    total_month_usage = sum(transferred_data['bytesTransferredByUserId'].values())

    data = {
        'request': request,
        'server_information': outline_client.get_server_information(),
        'total_month_usage': total_month_usage,
        'keys': outline_client.get_keys(),
    }

    return templates.TemplateResponse("main.html", data)


@app.post("/sign-in", response_class=HTMLResponse)
async def root(request: Request, ApiUrl: str = Form()):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

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
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.create_key(newKeyName)

    return response


@app.post("/rename/{key_id}", response_class=HTMLResponse)
async def rename_key_name(request: Request, key_id: int, keyName: str = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.rename_key(key_id, keyName)

    return response


@app.get("/delete/{key_id}", response_class=HTMLResponse)
async def delete_key(request: Request, key_id: int, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/')

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.delete_key(key_id)

    return response


@app.post("/set-data-limit", response_class=HTMLResponse)
async def delete_key(request: Request, dataLimitForAllKeys: int = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.set_data_limit_for_all_keys(dataLimitForAllKeys * 1000 * 1000 * 1000)

    return response


@app.get("/delete-data-limit", response_class=HTMLResponse)
async def delete_key(request: Request, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/')

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.delete_data_limit_for_all_keys()

    return response


@app.post("/set-data-limit/{key_id}", response_class=HTMLResponse)
async def delete_key(request: Request, key_id: int, dataLimit: int = Form(), ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

        server_information = outline_client.get_server_information()
    except Exception as e:
        return response

    outline_client.add_data_limit(key_id, dataLimit * 1000 * 1000 * 1000)

    return response


@app.get("/delete-data-limit/{key_id}", response_class=HTMLResponse)
async def delete_key(request: Request, key_id: int, ApiUrl: t.Union[str, None] = Cookie(default=None)):
    response = RedirectResponse('/')

    try:
        outline_client = PatchedOutlineVPN(api_url=ApiUrl)

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
