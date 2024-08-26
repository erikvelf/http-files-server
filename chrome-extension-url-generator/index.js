const generateBtn = document.getElementById("generate-btn")
const ipField = document.getElementById("input-ip")
const portField = document.getElementById("input-port")
const filePathInput = document.getElementById("file-path-input")

const contentCodeBtn = document.getElementById("code-btn")
const contentDownloadBtn = document.getElementById("download-btn")

const deleteBtn = document.getElementById("delete-btn")
const list = document.getElementById("history")

let contentState = "code"

let serverAdress = JSON.parse(localStorage.getItem("serverAdress"))
let serverIP = ""
let serverPort = ""

if (serverAdress != null) {
    serverIP = serverAdress[0]
    serverPort = serverAdress[1]


    ipField.value = serverIP
    portField.value = serverPort
}



let urls = []
let localStorageUrls = localStorage.getItem("urls")

console.log(localStorageUrls)
if (localStorageUrls != null) {
    urls = JSON.parse(localStorageUrls)
    render(urls)
}


function read(inputField) {
    input = inputField.value
    // inputField.value = ""
    return input
}


function render(arr) {
    let listElems = ""

    for (let i = 0; i < arr.length; i++) {
        listElems += `
           <li><a target="_blank" href="${arr[i]}">${arr[i]}</a></li>
            `
    }

    list.innerHTML = listElems
    console.log(listElems)
}

console.log(read(filePathInput))

contentCodeBtn.addEventListener("click", function() {
    console.log("User chose CODE")
    contentState = "code"

    filePathInput.value = "files/code/"
})

contentDownloadBtn.addEventListener("click", function() {
    console.log("User chose Download")
    contentState = "download"

    filePathInput.value = "files/download/"
})

deleteBtn.addEventListener("click", function() {
    urls = []
    render(urls)
    localStorage.removeItem("urls")

})

generateBtn.addEventListener("click", function(){
    serverIP = read(ipField)
    serverPort = read(portField)

    localStorage.setItem("serverAdress", JSON.stringify([serverIP, serverPort]))
    
    filePath = read(filePathInput)
    // console.log(ip, port, filePath)
    url = `http://${serverIP}:${serverPort}/${filePath}`
    // console.log(url)
    if (serverIP + serverPort + filePath === "") {
        console.log("Not enough parameters")
    } else {
        urls.push(url)  
        render(urls)   
        localStorage.setItem("urls", JSON.stringify(urls))
    }

})
