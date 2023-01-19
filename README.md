# Outline Web Manager

A Python-based simple Web Manager for [Outline VPN](https://getoutline.org/)

### Disclaimer

Developed for personal purposes. Front-end is simple HTML POST-forms with Bootstrap, no any JS modern frameworks. Backend is Python FastAPI app using [SINC :(](## "meanwhile FastAPI is async and gets blocked by sync lib") library called [outline-vpn-api](https://github.com/jadolg/outline-vpn-api)  to work with Outline Server management API. 

### Screenshot

<img width="500" alt="screenshot.png from repo" src="https://user-images.githubusercontent.com/18418712/213498267-46aaabd0-61f8-4c97-83ca-21a8d99a1ddd.png">

### Requirements

docker and docker-compose

## How to use

Install Outline Server as usual. It will give you output with management creds:
```
{"apiUrl":"https://76.117.122.22:11384/Psq45dRf4fK34fZpS249Kj","certSha256":"A227C34FB165B0444105154B615F6E2DA1221A7A30C749869B2CE32F98F22654"}
```

Start docker container from this repo (it will automatically build image and etc):
```
docker-compose up
```

After that you will get login form at http://<your_ip>:8000.

Please enter the output of Outline Installer in given form and submit it.

Server will store given creds to your browser cookies (DOESN'T store creds on server) and will give you full access to Outline Web Manager functionality:
1) Get list of keys;
1) Get \edit server-info;
2) Add \ rename \ delete key;
3) Set \ delete all-keys data limit;
4) Set \ delete individual key data limit;
5) Enable \ disable anonymous metrics.
