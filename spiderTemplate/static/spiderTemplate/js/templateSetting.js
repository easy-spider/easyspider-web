let img = $("#setting-img-wrapper img");

$(".arguments-form input, .arguments-form textarea").on("click", function () {
    let imgUrl = img.attr("src");
    let curField = $(this).siblings(".sr-only").text().trim();
    let url = imgUrl.split('/').slice(0, -1).join("/") + "/" + curField + '.jpg';
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

$("#setting-form").submit(function () {
    $.ajax({
        url: "{% url 'templateSetting' 'douban' 'movie' %}",
        type: "POST",
        data: $(this).serialize(),
        cache: false,
        success: function (data) {
            // console.log(data);
            if(data["status"] === "SUCCESS") {
                Toast.fire({
                    icon: "success",
                    title: "&nbsp;任务创建成功，请到我的任务页面查看",
                });
            } else {
                Toast.fire({
                    icon: "error",
                    title: "&nbsp;" + data["error_message"],
                });
            }
        },
        error: function (xhr) {
            console.log(xhr);
        }
    });
    return false;
});
