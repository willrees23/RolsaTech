window.onload = function () {
    // Get the gallery box
    var imageBox1 = document.getElementById("qrcode");

    // Get the modal image tag
    var modal = document.getElementById("qrcode_modal");

    var modalImage = document.getElementById("modal-image");

    var closebtn = document.getElementById("modal-close")

    // When the user clicks the big picture, set the image and open the modal
    imageBox1.onclick = function (e) {
        var src = e.target.src;
        modal.style.display = "flex";
        modalImage.src = src;
    };

    closebtn.onclick = function (e) {
        modal.style.display = "none";
    }
}