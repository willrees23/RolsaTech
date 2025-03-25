window.onload = function () {
    let formContainer = document.querySelector(".form");
    let realForm = null;

    for (const child of formContainer.children) {
        console.log(child.nodeName)
        if (child.nodeName == "FORM") {
            realForm = child
            break
        }
    }

    console.log(realForm)

    function onSubmit(e) {
        for (const child of realForm.children) {
            if (child.nodeName == "INPUT" || child.nodeName == "BUTTON") { child.disabled = true }
        }
    }

    realForm.addEventListener("submit", onSubmit)

}