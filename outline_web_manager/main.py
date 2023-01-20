import datetime
import json
import typing as t

from fastapi import FastAPI, Request, Form, Cookie, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from outline_vpn.outline_vpn import OutlineVPN
import uvicorn


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


async def get_outline_client(
    outputJsonCookie: t.Union[str, None] = Cookie(default=None),
    outputJsonForm: str = Form(None),
):
    if not outputJsonCookie and not outputJsonForm:
        return None

    try:
        parsed = json.loads(outputJsonCookie or outputJsonForm)
        outline_client = OutlineVPN(api_url=parsed['apiUrl'], cert_sha256=parsed['certSha256'])

        server_information = outline_client.get_server_information()
    except Exception as e:
        return None

    return outline_client


@app.get("/")
async def root(request: Request, outline_client: OutlineVPN = Depends(get_outline_client)):
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


@app.post("/sign-in")
async def root(outline_client: OutlineVPN = Depends(get_outline_client), outputJsonForm: str = Form()):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    if not outline_client:
        return response

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=90)

    response.set_cookie(key='outputJsonCookie', value=outputJsonForm, expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    return response


@app.post("/add")
async def create_new_key(
    newKeyName: str = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.create_key(newKeyName)

    return response


@app.post("/rename/{key_id}")
async def rename_key_name(
    key_id: int,
    keyName: str = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.rename_key(key_id, keyName)

    return response


@app.post("/delete/{key_id}")
async def delete_key(
    key_id: int,
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.delete_key(key_id)

    return response


@app.post("/set-server-name")
async def set_server_name(
    serverName: str = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_server_name(serverName)

    return response


@app.post("/set-hostname")
async def set_hostname(
    hostnameForAccessKeys: str = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_hostname(hostnameForAccessKeys)

    return response


@app.post("/set-metrics")
async def set_hostname(
    metrics: bool = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_metrics_status(metrics)

    return response


@app.post("/set-port")
async def set_port(
    portForNewAccessKeys: int = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_port_new_for_access_keys(portForNewAccessKeys)

    return response


@app.post("/set-data-limit")
async def set_data_limit(
    dataLimitForAllKeys: int = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.set_data_limit_for_all_keys(dataLimitForAllKeys * 1000 * 1000 * 1000)

    return response


@app.post("/delete-data-limit")
async def delete_data_limit(
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.delete_data_limit_for_all_keys()

    return response


@app.post("/set-data-limit/{key_id}")
async def set_key_data_limit(
    key_id: int, dataLimit: int = Form(),
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.add_data_limit(key_id, dataLimit * 1000 * 1000 * 1000)

    return response


@app.post("/delete-data-limit/{key_id}")
async def delete_key_data_limit(
    key_id: int,
    outline_client: OutlineVPN = Depends(get_outline_client),
):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    outline_client.delete_data_limit(key_id)

    return response


@app.post("/logout")
async def logout():
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie('outputJsonCookie')
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
