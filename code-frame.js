const textToCopyEl = document.getElementById("text-to-copy")
const copyBtn = document.getElementById("copy-btn")
console.log("js filed linked")



// function copy() {
//     // copyTextToClipboard(textToCopyEl.textContent);
//     navigator.clipboard.writeText("sdflkjfsdlkjasdf")
// }

copyBtn.addEventListener("click", function() {
    console.log("button clicked")
    alert("codice copiato con successo!")
    const textInput = document.createElement("textarea");
    textInput.value = textToCopyEl.textContent;
    document.body.appendChild(textInput)
    textInput.select()
    document.execCommand("copy")
    document.body.removeChild(textInput)
})

const el = document.createElement("div");
el.style = { "width": "200px", "height": "200px", "position": "absolute" }
