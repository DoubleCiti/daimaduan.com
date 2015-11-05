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
              var li = '<li class="list-group-item">';
              li += '<div class="pull-right">';
              li += '<a href="#" class="text-muted" title="' + paste.user.username + '">' + paste.user.username + '</a>';
              li += '</div>';
              li += '<a href="/paste/' + paste.hash_id + '" title="' + paste.title + '">' + paste.title + ' </a>';
              $.each(paste.tags, function(i, tag){
                li += '<a href="/tag/' + tag + '" class="btn btn-xs btn-warning" title="' + tag + '">' + tag + '</a>';
              });
              li += '<div class="clearfix"></div>';
              li += '</li>';
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