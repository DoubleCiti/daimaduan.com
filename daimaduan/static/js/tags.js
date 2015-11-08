(function() {
    function initGetMore() {
      $(document).on('click', '#more_button', function(event) {
        var p = $(this).attr('data-page');
        var tag = $(this).attr('data-tag');
        event.preventDefault();
        $.ajax({
          data: 'p=' + p,
          type: 'GET',
          url: '/tag/' + tag + '/more',
          success: function(data) {
            $.each(data.pastes, function(i, paste) {
              var li = createLi(paste);
              $(li).insertBefore('#more_button_li');
            });
          }
        });
        $(this).attr('data-page', parseInt(p) + 1);
      });
    }

  $(document).ready(function() {
    initGetMore();
  });
})();