let starter_search_box = $("#starter-search-box");

$.fn.strech_text = function () {
  var elmt = $(this),
    cont_width = elmt.width(),
    txt = elmt.html(),
    one_line = $('<span class="stretch_it">' + txt + "</span>"),
    nb_char = elmt.text().trim().length,
    spacing = cont_width / nb_char,
    txt_width;

  elmt.html(one_line);
  txt_width = one_line.width();

  if (txt_width < cont_width) {
    var char_width = txt_width / nb_char,
      ltr_spacing = spacing - char_width + (spacing - char_width) / nb_char;

    one_line.css({ "letter-spacing": ltr_spacing });
  } else {
    one_line.contents().unwrap();
    elmt.addClass("justify");
  }
};

$(".stretch").each(function () {
  $(this).strech_text();
});

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
});

$(".fa-search").parent("a").on("click", function () {
  let val = starter_search_box.val().trim();
  if(val !== "") {
    let url = $(this).attr("href");
    $(this).attr("href", url + "?search=" + val);
  } else {
    Toast.fire({
        icon: "error",
        title: "&nbsp;搜索框输入不能为空",
    });
    return false;
  }
});
