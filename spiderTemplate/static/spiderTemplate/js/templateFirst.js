let searchbox = $("#template-search-box");

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

$(".fa-search").parent("a").on("click", function () {
  let value = searchbox.val().trim();
  if(value !== "") {
      let url = $(this).attr("href");
    $(this).attr("href", url + "?search=" + value);
  }
  else {
    return false;
  }
});
