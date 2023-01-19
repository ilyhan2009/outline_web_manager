import datetime
from dataclasses import dataclass
import requests
import json
import typing as t

import uvicorn

from fastapi import FastAPI, Request, Form, Cookie, Depends
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


async def get_outline_client(
        outputJsonCookie: t.Union[str, None] = Cookie(default=None),
        outputJsonForm: str = Form(None),
):
    if not outputJsonCookie and not outputJsonForm:
        return None

    try:
        parsed = json.loads(outputJsonCookie or outputJsonForm)
        outline_client = PatchedOutlineVPN(api_url=parsed['apiUrl'], cert_sha256=parsed['certSha256'])

        server_information = outline_client.get_server_information()
    except Exception as e:
        return None

    return outline_client


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, outline_client: PatchedOutlineVPN = Depends(get_outline_client)):
    if not outline_client:
        return templates.TemplateResponse("sign-in.html", {"request": request})

    transferred_data = outline_client.get_transferred_data()

    total_month_usage = sum(transferred_data['bytesTransferredByUserId'].values())

    server_information = outline_client.get_server_information()

    data = {
        'request': request,
        'server_information': server_information,
        'server_creation': datetime.datetime.fromtimestamp(server_information['createdTimestampMs'] // 1000),
        'total_month_usage': total_month_usage,
        'keys': outline_client.get_keys(),
    }

    return templates.TemplateResponse("main.html", data)


@app.post("/sign-in", response_class=HTMLResponse)
async def root(outline_client: PatchedOutlineVPN = Depends(get_outline_client), outputJsonForm: str = Form()):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    if not outline_client:
        return response

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=90)

    response.set_cookie(key='outputJsonCookie', value=outputJsonForm, expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    return response


@app.post("/add", response_class=HTMLResponse)
async def create_new_key(
    newKeyName: str = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.create_key(newKeyName)

    return response


@app.post("/rename/{key_id}", response_class=HTMLResponse)
async def rename_key_name(
    key_id: int,
    keyName: str = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.rename_key(key_id, keyName)

    return response


@app.get("/delete/{key_id}", response_class=HTMLResponse)
async def delete_key(
    key_id: int,
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/')

    outline_client.delete_key(key_id)

    return response


@app.post("/set-server-name", response_class=HTMLResponse)
async def set_server_name(
    serverName: str = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_server_name(serverName)

    return response


@app.post("/set-hostname", response_class=HTMLResponse)
async def set_hostname(
    hostnameForAccessKeys: str = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_hostname(hostnameForAccessKeys)

    return response


@app.post("/set-metrics", response_class=HTMLResponse)
async def set_hostname(
    metrics: bool = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_metrics_status(metrics)

    return response


@app.post("/set-port", response_class=HTMLResponse)
async def set_port(
    portForNewAccessKeys: int = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_port_new_for_access_keys(portForNewAccessKeys)

    return response


@app.post("/set-data-limit", response_class=HTMLResponse)
async def set_data_limit(
    dataLimitForAllKeys: int = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_data_limit_for_all_keys(dataLimitForAllKeys * 1000 * 1000 * 1000)

    return response


@app.get("/delete-data-limit", response_class=HTMLResponse)
async def delete_data_limit(
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/')

    outline_client.delete_data_limit_for_all_keys()

    return response


@app.post("/set-data-limit/{key_id}", response_class=HTMLResponse)
async def set_key_data_limit(
    key_id: int, dataLimit: int = Form(),
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.add_data_limit(key_id, dataLimit * 1000 * 1000 * 1000)

    return response


@app.get("/delete-data-limit/{key_id}", response_class=HTMLResponse)
async def delete_key_data_limit(
    key_id: int,
    outline_client: PatchedOutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/')

    outline_client.delete_data_limit(key_id)

    return response


@app.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse('/')
    response.delete_cookie('outputJsonCookie')
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
