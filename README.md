# http-files-server
This project is about improving my previous codecrafters-http-server. Here I created a server that can share files on the LAN.


This server is able to:
- Run on Linux and Windows
- Find out its IP address automatically
- send HTML's with CSS and Javascript
- render pulled code on a web page
- download any files that are not code files
- Logs

# How to setup the server
1. Place the http-server.py file in a folder
2. **IMPORTANT** Create folder named "info" in the same folder as the python program (there you will find the logs of the server)
3. **IMPORTANT** Create a folder named "templates" in the same folder as the python program
4. **IMPORTANT** Put the files "__code-frame.html", "__code-frame.css", "__code-frame.js" in the folder "templates"
5. Run the server **in the same directory where you placed it**

The minimal setup should look like that:
```
├── http-server.py
├── info
│   └── logs.txt
└── templates
    ├── __code-frame.css
    ├── __code-frame.html
    └── __code-frame.js
```

# How to use the server
To request a **file**, write its path. The file will be searched within the folder where the python program was placed
Ex: http://{server's IP}:{server's PORT}/{path to the file}

You can get the server's IP and PORT by launching the server and reading the first printed lines:
```
[0] Using linux.

[*] Listening on 192.168.178.106:4221...
```

If you requested a file that has a code extension (and exists) specified in the list **CODE_EXTENSIONS** (line 31 of the python program), then the server will send you a web page with the code file contents in it.

If the file isn't in the CODE_EXTENSIONS list, then if the file exists it will be sent as a file to download.

In any other case you will receive an error 404


# Chrome extension to generate urls
You can use the chrome extension provided in the repo, it does **remember the provided IP and PORT**

It will create a request to the server based on it's inputs

Since the minimal setup doesn't have the folders for the code files and download files, you might want to add them to be able to use the buttons in the dropdown menu "Content"
To use that button you can either modify the js file of the extension or add folders where you will put files in.

So the setup in the repo looks like that:
```
.
├── files
│   ├── code
│   │   └── your_code_file.c
│   └── download
│       └── your_file_that_you_want_to_share.download
├── http-server-v4.py
├── info
│   └── logs.txt
└── templates
    ├── __code-frame.css
    ├── __code-frame.html
    └── __code-frame.js

```

