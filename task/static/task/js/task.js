let taskTable = $("#task-table").DataTable({
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
  },
});

let totalScore = 0;
let btnEle = $("#refresh-delete");
$("#task-table tbody input[type=checkbox]").change(function () {
  if ($(this).is(":checked")) {
    totalScore += 1;
    if (btnEle.text().trim() !== "删除") {
      btnEle.html("<i class='fas fa-trash'></i>&nbsp;删除");
    }
  } else {
    totalScore -= 1;
    if (totalScore === 0) {
      btnEle.html("<i class='fas fa-sync'></i>&nbsp;刷新");
    }
  }
});

$(".dataTables_scrollHeadInner input[type=checkbox]").change(function () {
  if ($(this).is(":checked")) {
    totalScore = $("#task-table tbody tr").length;
    btnEle.html("<i class='fas fa-trash'></i>&nbsp;删除");
  } else {
    totalScore = 0;
    btnEle.html("<i class='fas fa-sync'></i>&nbsp;刷新");
  }
});
