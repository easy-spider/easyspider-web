let img = $("#setting-img-wrapper img");
$("#arguments-card #inputPageNum").on("click", function () {
    if (img.attr("src") !== "img/page.jpg") {
        img.attr("src", "img/page.jpg");
    }
});

$("#arguments-card #textareaUrl").on("click", function () {
    if (img.attr("src") !== "img/url.jpg") {
        img.attr("src", "img/url.jpg");
    }
});

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
});

//注意处理重复点击的问题，可以重复创建，但同组不同任务名或者不同组
$(".swalDefaultSuccess").click(function () {
    Toast.fire({
        icon: "success",
        title: "&nbsp;任务创建成功，请到我的任务页面查看",
    });
});
