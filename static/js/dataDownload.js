$("#data-table").DataTable({
  scrollX: true,
  searching: false,
  ordering: false,
  bLengthChange: false,
  pageLength: 100,
  language: {
    info: "_TOTAL_ 条数据中的第 _START_ 至 _END_ 条",
    paginate: {
      next: "下一页",
      previous: "上一页",
    },
  },
});
