let taskTableEle = $("#task-table");
let taskTableBodyEle = taskTableEle.find("tbody");

let taskTable = taskTableEle.DataTable({
  dom: '<"toolbar">frtip',
  fnInitComplete: function(){
     $('div.toolbar').html('            <button\n' +
         '              type="submit"\n' +
         '              class="btn btn-primary"\n' +
         '              id="refresh-delete"\n' +
         '            >\n' +
         '              <span class="spinner-border spinner-border-sm loading" role="status" aria-hidden="true"></span>' +
         '              <i class="fas fa-sync"></i>&nbsp;刷新\n' +
         '            </button>');
     $($.fn.dataTable.tables(true)).DataTable().columns.adjust();
   },
  paging: false,
  info: false,
  scrollX: true,
  columnDefs: [
    {
      targets: 0,
      checkboxes: {
        selectRow: true,
      },
    },
    {
      orderable: false,
      targets: [3, -2, -1],
    },
    {
      colReorder: true,
    },
  ],
  select: {
    style: "multi",
  },
  order: [[1, "asc"]],
  language: {
    search: "搜索:",
    sZeroRecords: "没有找到匹配的采集任务",
    emptyTable: "暂无任务",
  },
});

taskTableEle.on('show.bs.dropdown', function () {
    $('.dataTables_scrollBody').addClass('dropdown-visible');
})
  .on('hide.bs.dropdown', function () {
    $('.dataTables_scrollBody').removeClass('dropdown-visible');
});

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
});

$(".dataTables_filter label").css({
  "margin-top": "6px",
  "margin-bottom": "0px",
});

let totalScore = 0;
let btnEle = $("#refresh-delete");

taskTableBodyEle.find("input[type=checkbox]").change(function () {
  if ($(this).is(":checked")) {
    $(this).parents("tr").addClass("selected");
    totalScore += 1;
    if (btnEle.text().trim() !== "删除") {
      btnEle.html("<span class=\"spinner-border spinner-border-sm loading\" role=\"status\" aria-hidden=\"true\"></span>" +
          " <i class='fas fa-trash'></i>&nbsp;删除");
    }
  } else {
    $(this).parents("tr").removeClass("selected");
    totalScore -= 1;
    if (totalScore === 0) {
      btnEle.html("<span class=\"spinner-border spinner-border-sm loading\" role=\"status\" aria-hidden=\"true\"></span> " +
          "<i class='fas fa-sync'></i>&nbsp;刷新");
    }
  }
});

$(".dataTables_scrollHeadInner input[type=checkbox]").change(function () {
  let trEles = taskTableBodyEle.find("tr");
  if ($(this).is(":checked")) {
    trEles.addClass("selected");
    totalScore = trEles.length;
    btnEle.html("<span class=\"spinner-border spinner-border-sm loading\" role=\"status\" aria-hidden=\"true\"></span> " +
        "<i class='fas fa-trash'></i>&nbsp;删除");
  } else {
    trEles.removeClass("selected");
    totalScore = 0;
    btnEle.html("<span class=\"spinner-border spinner-border-sm loading\" role=\"status\" aria-hidden=\"true\">" +
        "</span> <i class='fas fa-sync'></i>&nbsp;刷新");
  }
});
