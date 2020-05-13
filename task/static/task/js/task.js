let taskTableEle = $("#task-table");
let taskTableBodyEle = taskTableEle.find("tbody");

taskTableEle.css("min-height","100px");

let taskTable = taskTableEle.DataTable({
  dom: '<"toolbar">frtip',
  fnInitComplete: function(){
     $('div.toolbar').html('            <button\n' +
         '              type="submit"\n' +
         '              class="btn btn-primary"\n' +
         '              id="refresh-delete"\n' +
         '            >\n' +
         '              <i class="fas fa-sync"></i>&nbsp;刷新\n' +
         '            </button>');
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

$('#cancel-task-modal').on('show.bs.modal', function(e) {
    let aEle = $(e.relatedTarget);
    let taskID = aEle.data('id');
    let cancelTaskForm = $("#cancel-task-form");
    let cancelBtn = cancelTaskForm.find("button[type=submit]");
    cancelTaskForm.off("submit");
    cancelTaskForm.submit(function () {
        cancelBtn.attr("disabled", "disabled");
        $.ajax({
            url: $(this).attr("action").split("/").slice(0,-2).concat(taskID).join("/") + "/",
            type: "POST",
            data: $(this).serialize(),
            cache: false,
            success: function (data) {
              if(data["status"] === "SUCCESS") {
                  cancelBtn.removeAttr("disabled");
                  Toast.fire({
                      icon: "success",
                      title: "&nbsp;任务已终止",
                  });
                  // 更新采集状态、操作、耗时、采集完成时间
                  let preEle = aEle.prev("a");
                  preEle.find("i").attr("class", "far fa-play-circle hidden");
                  preEle.attr({
                      "href": "#restart-task-modal",
                      "data-id": "" + taskID,
                      "data-target": "#restart-task-modal"
                  });
                  let parent = aEle.parent("td");
                  parent.removeClass();
                  parent.addClass("canceled");
                  let status = parent.prev("td");
                  status.removeClass();
                  status.addClass("canceled");
                  status.html("已终止");
                  aEle.remove();
                  // 隐去modal
                  $('#cancel-task-modal').modal('hide');
                  taskTable.columns.adjust().draw();
              } else {
                  cancelBtn.removeAttr("disabled");
                  Toast.fire({
                      icon: "error",
                      title: "&nbsp;" + data["message"],
                  });
              }
            },
            error: function (xhr) {
              cancelBtn.removeAttr("disabled");
              console.log(xhr);
            }
        });
        return false;
    });
});

taskTableBodyEle.find("input[type=checkbox]").change(function () {
  if ($(this).is(":checked")) {
    $(this).parents("tr").addClass("selected");
    totalScore += 1;
    if (btnEle.text().trim() !== "删除") {
      btnEle.html("<i class='fas fa-trash'></i>&nbsp;删除");
    }
  } else {
    $(this).parents("tr").removeClass("selected");
    totalScore -= 1;
    if (totalScore === 0) {
      btnEle.html("<i class='fas fa-sync'></i>&nbsp;刷新");
    }
  }
});

$(".dataTables_scrollHeadInner input[type=checkbox]").change(function () {
  let trEles = taskTableBodyEle.find("tr");
  if ($(this).is(":checked")) {
    trEles.addClass("selected");
    totalScore = trEles.length;
    btnEle.html("<i class='fas fa-trash'></i>&nbsp;删除");
  } else {
    trEles.removeClass("selected");
    totalScore = 0;
    btnEle.html("<i class='fas fa-sync'></i>&nbsp;刷新");
  }
});
