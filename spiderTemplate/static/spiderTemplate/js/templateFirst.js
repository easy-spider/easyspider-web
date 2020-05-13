let searchbox = $("#template-search-box");

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
});

$(".fa-search").parent("a").on("click", function () {
  let value = searchbox.val().trim();
  if(value !== "") {
      let url = $(this).attr("href");
    $(this).attr("href", url + "&search=" + value);
  }
  else {
    Toast.fire({
        icon: "error",
        title: "&nbsp;搜索框输入不能为空",
    });
    return false;
  }
});
