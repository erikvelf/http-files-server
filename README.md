# http-files-server
This project is about improving my previous codecrafters-http-server. Here I will try to create a server that can share files if requested on the LAN.

## How the server works
IMPORTANT: the server finds its files in specific folders

Folder explanation:
- templates: there are stored the needed HTML, CSS, Javascript and a favicon.ico.
It is named templates because it will combine the code in the folder in the template's HTML

- files: All files that will be shared from the HTTP server, it contains the folder **files-code** that contains ONLY **.txt** of the code (for now only txts are supported) to combine with the template.
The folder **downloads** contains files of **any extension** to share.

- info: it will store the server's logs and other info in the future

## How to request?
If you wanna request the code from **files-code**, than you have to type: {server's IP}:{server's PORT}/code/{name of the file in the files-code folder **WITHOUT** its extension}

So the url for the **default settings** will be:
{IP}:[PORT]/code/code1

If you wanna download a file, you will type the same server's IP and port, but the path will be: /download/{file with its extension}

So the url for the  **default settings** will be:
{IP}:[PORT]/download/test.test

# This server is able to:
- Run on Linux and Windows
- Find out its IP address automatically
- send HTML's with CSS and Javascript
- pull a .txt file and combining it with a template HTML and CSS with it
- download any files (not folders for now) in the ./files/downloads folder
- creating a file in the downloads folder via POST method

This first iteration is not perfect and there is a lot to improve.
- [ ] Polishing the code

Features soon to be added:
- [ ] Logging information capabilities
- [ ] Adding the ability to download folders (for now the server could only access single files and not folders within a specific folder)

