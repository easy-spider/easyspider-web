$("#template-type .nav-link").on("click", function (event) {
  $(this)
    .addClass("active")
    .parent()
    .siblings()
    .find(".nav-link")
    .removeClass("active");
});

$("#template-order .nav-link").on("click", function (event) {
  $(this)
    .addClass("active")
    .parent()
    .siblings()
    .find(".nav-link")
    .removeClass("active");
});
