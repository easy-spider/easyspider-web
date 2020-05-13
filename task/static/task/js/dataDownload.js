let dataTableEle = $("#data-table");
let dataTable = dataTableEle.DataTable({
  scrollX: true,
  searching: false,
  ordering: false,
  bLengthChange: false,
  pageLength: 5,
  language: {
    info: "_TOTAL_ 条数据中的第 _START_ 至 _END_ 条",
    infoEmpty: "_TOTAL_ 条数据中的第 0 至 _END_ 条",
    paginate: {
      next: "下一页",
      previous: "上一页",
    },
    emptyTable: "暂无数据"
  },
});

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
});

$('#data-modal').on('show.bs.modal', function(e) {
  let dtEles = $(this).find("dt");
  let rowIndex = $(e.relatedTarget).data('id');
  $(this).find(".modal-title").html("#" + rowIndex + " 数据详情");
  for(let i = 0; i < dtEles.length; i++) {
    let next = dtEles.eq(i).next();
    let updateStr = "<dd>" + $(dataTable.cell(rowIndex - 1, i + 2).data().trim()).text().trim() + "</dd>";
    if(next.is("dd")) {
      next.html(updateStr);
    } else {
      $(updateStr).insertAfter(dtEles.eq(i));
    }
  }
});
