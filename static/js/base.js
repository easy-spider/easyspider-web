let editMenuMarginTop = [-355, -315, -270, -225, -185];
let editMenuEle = $("#edit-menu");
let ellipsises = $(".edit-item .fa-ellipsis-h");
for (let i = 0; i < editMenuMarginTop.length; i++) {
    ellipsises.eq(i).on("click", function (event) {
        $("#user-dropdown + .dropdown-menu").removeClass("show");
        $(".task-dropdown + .dropdown-menu").removeClass("show");
        let targetLoc = editMenuMarginTop[i] + "px";
        if (editMenuEle.css("margin-top") !== targetLoc) {
            editMenuEle.removeClass("show");
            editMenuEle.css("margin-top", targetLoc);
            editMenuEle.addClass("show");
            event.stopPropagation();
        } else {
            editMenuEle.toggleClass("show");
        }
        event.stopPropagation();
    });
}

$("#user-dropdown").on("click", function () {
    editMenuEle.removeClass("show");
});

$(".task-dropdown").on("click", function () {
    editMenuEle.removeClass("show");
});

$(document).click(function () {
    editMenuEle.removeClass("show");
});

$("#createTaskBtn").on("click", function () {
    window.location.href = "templateFirst.html";
});
