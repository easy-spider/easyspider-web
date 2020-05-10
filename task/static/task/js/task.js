let taskTable = $("#task-table").DataTable({
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
    emptyTable: "暂无数据",
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

btnEle.on("click", function () {
  if($(this).find("i").hasClass("fa-sync")) {
      location.reload();
      taskTable.columns.adjust().draw();
      return false;
  } else {
      let taskForm = $("#task-form");
      taskForm.off("submit");
      taskForm.submit(function () {
        let isValid = true;
        let form = this;
        let rows_selected = taskTable.column(0).checkboxes.selected();
        // Iterate over all selected checkboxes
        $.each(rows_selected, function(index, rowId){
          // validation
          let taskStatus =  taskTable.cell(rowId - 1, 2).data().trim();
          if(taskStatus !== "已完成" && taskStatus !== "已终止") {
              Toast.fire({
                  icon: "error",
                  title: "&nbsp;非已完成或已终止状态的任务不能删除",
              });
              isValid = false;
              return false;
          }
        });
        if(isValid) {
            let selectRowsID = new Set();
            $.each(rows_selected, function(index, rowId){
                selectRowsID.add(rowId);
                let taskID = $(taskTable.cell(rowId - 1, 1).data()).attr("data-id");
                // Create a hidden element
                $(form).append(
                     $('<input>')
                        .attr('type', 'hidden')
                        .attr('name', 'id')
                        .val(taskID)
                );
            });
            $.ajax({
              url: $(form).attr("action"),
              type: "POST",
              data: $(form).serialize() + "&for=deleteTask",
              cache: false,
              success: function (data) {
                  if(data["status"] === "SUCCESS") {
                      Toast.fire({
                          icon: "success",
                          title: "&nbsp;任务删除成功",
                      });
                      let index = 0;
                      for(let item of selectRowsID) {
                          taskTable.row(item - index - 1).remove().draw(false);
                          index++;
                      }
                      // reset button
                      btnEle.html("<i class='fas fa-sync'></i>&nbsp;刷新");
                  } else {
                      Toast.fire({
                          icon: "error",
                          title: "&nbsp;" + data["message"],
                      });
                  }
              },
              error: function (xhr) {
                  console.log(xhr);
              }
            });
            // Remove added elements
            $('input[name="id"]', form).remove();
        }
        return false;
      });
  }
});

$('#rename-task-modal').on('show.bs.modal', function(e) {
    let taskID = $(e.relatedTarget).data('id');
    let renameTaskForm = $("#rename-task-form");
    renameTaskForm.off("submit");
    renameTaskForm.submit(function () {
        // validation
        let form = this;
        let inputEle = $(form).find("input");
        let newTaskName = $(form).find("#task-name-input").val().trim();
        if(newTaskName.length === 0) {
            Toast.fire({
                icon: "error",
                title: "&nbsp;任务名不能为空",
            });
            inputEle.val("");
            return false;
        } else {
            if(newTaskName.length < 3 || newTaskName.length > 20) {
                Toast.fire({
                    icon: "error",
                    title: "&nbsp;任务名长度应在3~20个字符之间",
                });
                inputEle.val("");
                return false;
            }
        }
        $.ajax({
            url: $(form).attr("action"),
            type: "POST",
            data: $(form).serialize() + "&id=" + taskID + "&for=renameTask",
            cache: false,
            success: function (data) {
              if(data["status"] === "SUCCESS") {
                  Toast.fire({
                      icon: "success",
                      title: "&nbsp;任务重命名成功",
                  });
                  // 修改任务名
                  let ele = $("a[data-id=" + taskID + "][href=\"#rename-task-modal\"]");
                  let updateNameStr = ele[0].outerHTML + newTaskName;
                  ele.parent("td").html(updateNameStr);
                  // 隐去modal
                  $('#rename-task-modal').modal('hide');
                  taskTable.columns.adjust().draw();
              } else {
                  Toast.fire({
                      icon: "error",
                      title: "&nbsp;" + data["message"],
                  });
              }
            },
            error: function (xhr) {
              console.log(xhr);
            }
        });
        inputEle.val("");
        return false;
    });
});

$('#cancel-task-modal').on('show.bs.modal', function(e) {
    let taskID = $(e.relatedTarget).data('id');
    let cancelTaskForm = $("#cancel-task-form");
    cancelTaskForm.off("submit");
    cancelTaskForm.submit(function () {
        $.ajax({
            url: $(this).attr("action"),
            type: "POST",
            data: $(this).serialize() + "&id=" + taskID + "&for=cancelTask",
            cache: false,
            success: function (data) {
              if(data["status"] === "SUCCESS") {
                  Toast.fire({
                      icon: "success",
                      title: "&nbsp;任务已终止",
                  });
                  // 更新采集状态、操作、耗时、采集完成时间
                  let ele = $("a[data-id=" + taskID + "][href=\"#cancel-task-modal\"]");
                  let preEle = ele.prev("a");
                  preEle.find("i").attr("class", "far fa-play-circle hidden");
                  preEle.attr({
                      "href": "#restart-task-modal",
                      "data-id": "" + taskID,
                      "data-target": "#restart-task-modal"
                  });
                  let parent = ele.parent("td");
                  parent.removeClass();
                  parent.addClass("canceled");
                  let status = parent.prev("td");
                  status.removeClass();
                  status.addClass("canceled");
                  status.html("已终止");
                  // 耗时
                  parent.nextAll().eq(1).html("2分钟");
                  // 采集完成时间
                  parent.nextAll().eq(3).html("20/05/09 13:00");
                  ele.remove();
                  // 隐去modal
                  $('#cancel-task-modal').modal('hide');
                  taskTable.columns.adjust().draw();
              } else {
                  Toast.fire({
                      icon: "error",
                      title: "&nbsp;" + data["message"],
                  });
              }
            },
            error: function (xhr) {
              console.log(xhr);
            }
        });
        return false;
    });
});

$('#restart-task-modal').on('show.bs.modal', function(e) {
    let taskID = $(e.relatedTarget).data('id');
    let restartTaskForm = $("#restart-task-form");
    restartTaskForm.off("submit");
    restartTaskForm.submit(function () {
        $.ajax({
            url: $(this).attr("action"),
            type: "POST",
            data: $(this).serialize() + "&id=" + taskID + "&for=restartTask",
            cache: false,
            success: function (data) {
              if(data["status"] === "SUCCESS") {
                  Toast.fire({
                      icon: "success",
                      title: "&nbsp;任务已重新开始",
                  });
                  // 更新采集状态、操作字符、进度条（为0）、执行次数+1、耗时和采集完成时间清空
                  let ele = $("a[data-id=" + taskID + "][href=\"#restart-task-modal\"]");
                  ele.attr({"href": "", "data-target": "", "data-id": taskID});
                  ele.find("i").attr("class", "far fa-pause-circle hidden");
                  let parent = ele.parent("td");
                                        parent.append("                          <a\n" +
                      "                            data-id=\"" + taskID + "\"\n" +
                      "                            href=\"#cancel-task-modal\"\n" +
                      "                            data-toggle=\"modal\"\n" +
                      "                            data-target=\"#cancel-task-modal\"\n" +
                      "                          >\n" +
                      "                            <i class=\"far fa-stop-circle hidden\"></i>\n" +
                      "                          </a>");
                  parent.removeClass();
                  parent.addClass("ready");
                  let status = parent.prev("td");
                  status.removeClass();
                  status.addClass("ready");
                  status.html("等待运行");
                  // 清空耗时
                  parent.nextAll().eq(1).html("");
                  // 执行次数+1
                  let countEle = parent.nextAll().eq(2);
                  countEle.html(+countEle.html().trim() + 1);
                  // 清空采集完成时间
                  parent.nextAll().eq(3).html("");
                  // 进度条重置为0
                  tdEle = parent
                      .nextAll()
                      .eq(4)
                      .find(".progress")
                      .attr("title", "0%")
                      .find(".progress-bar")
                      .css("width", "0%");

                  // 隐去modal
                  $('#restart-task-modal').modal('hide');
                  taskTable.columns.adjust().draw();
              } else {
                  Toast.fire({
                      icon: "error",
                      title: "&nbsp;" + data["message"],
                  });
              }
            },
            error: function (xhr) {
              console.log(xhr);
            }
        });
        return false;
   });
});

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
