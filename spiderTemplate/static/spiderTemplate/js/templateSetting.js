let img = $("#setting-img-wrapper img");

$(".arguments-form input, .arguments-form textarea").on("click", function () {
    let imgUrl = img.attr("src");
    let curField = $(this).attr("name");
    let url = imgUrl.split('/').slice(0, -2).join("/") + "/" + curField + '/';
    if (imgUrl !== url) {
        img.attr("src", url);
    }
});


const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
});
