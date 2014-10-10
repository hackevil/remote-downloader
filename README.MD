Remote Download Helper
==================

Intorduction
-----------------
A simple web app to help you download files from server, it's like a proxyed downloader, useful when certain sites are blocked.

It's built on [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO), [requests](https://github.com/kennethreitz/requests) and [bootstrap](https://github.com/twbs/bootstrap), thanks.

I originally developed this using nodejs, however even using pip, the memory usage is extraordinarily high, cause out-of-memory killer to start when downlaoding large file(well my VPS memroy is quite limited).


Deploy on ubuntu
-------------------------
0. Setup Flask-SocketIO and requests

    ```bash
    sudo apt install build-essential python-dev python-lxml 
    sudo pip install Flask-SocketIO
    sudo pip install requests
    ```

1. Setup nginx server, it's strongly recommended to use stable version instead of the outdated one comes with ubuntu. Steps see [here](http://nginx.org/en/linux_packages.html#stable)
2. clone this repository
3. change repository owner to nginx(or whatever you use with nginx)

    ```bash
    chown -Rh nginx:nginx PATH
    ``` 

4. copy the `config/nginx-sample.conf` to `/etc/nginx/conf.d/` and change the `server/server_name` and `server/location/root`
5. start nginx

    ```bash
    service nginx start
    nginx -s reload
    ```

6. start the python app

    ```bash
    cd PATH
    python app.py
    ```

You are done, visit using your browser(IE>9) and try.

Start python in backgound
-----------------------
To start the python app in backgroud, I suggest using Supervisor. The config is provided as `config/supervisor-sample.conf`, after install Supervisor put it to `/etc/supervisor/conf.d/` and reload supervisor `supervisorctl reload`. For install and debug on supervisor see [this page](https://github.com/clowwindy/shadowsocks/wiki/Configure-Shadowsocks-with-Supervisor)