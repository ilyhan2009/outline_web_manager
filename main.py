import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if True:
        return templates.TemplateResponse("sign-in.html", {"request": request})

    return templates.TemplateResponse("main.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)









from outline_vpn.outline_vpn import OutlineVPN

# Setup the access with the API URL (Use the one provided to you after the server setup)
client = OutlineVPN(api_url="")

# Get all access URLs on the server
for key in client.get_keys():
    print(f'{key.name} {key.access_url}')
#
# # Create a new key
# new_key = client.create_key()
#
# # Rename it
# client.rename_key(new_key.key_id, "new_key")
#
# # Delete it
# client.delete_key(new_key.key_id)
#
# # Set a monthly data limit for a key (20MB)
# client.add_data_limit(new_key.key_id, 1024 * 1024 * 20)
#
# # Remove the data limit
# client.delete_data_limit(new_key.key_id)