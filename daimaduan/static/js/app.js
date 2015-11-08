function signoutHandler() {
  $.ajax({
    url: '/signout',
    method: 'DELETE',
    success: function() {
      document.location = '/';
    }
  });
}

function createLi(paste) {
      var li = '<li class="list-group-item">';
      li += '<div class="pull-right">';
      li += '<a href="/user/' + paste.user.username + '" class="text-muted" title="' + paste.user.username + '">';
      li += '<img src="' + paste.user.gravatar_url + '" alt="' + paste.user.username + '" class="img-rounded"/></a>';
      li += '</div>';
      li += '<h5>';
      li += '<a href="/paste/' + paste.hash_id + '" title="' + paste.title + '">' + paste.title + '</a> ';
      li += '<span class="label label-default">' + paste.time_passed + '</span> ';
      li += '<span class="label label-primary">有' + paste.num_codes + '段代码</span>';
      li += '<a href="/paste/' + paste.hash_id + '#disqus_thread" class="label label-info"></a>'
      li += '</h5>';
      $.each(paste.tags, function(i, tag) {
        li += '<a href="/tag/' + tag + '" class="btn btn-xs btn-warning" title="' + tag + '">' + tag + '</a>';
      });
      li += '<div class="clearfix"></div>';
      li += '</li>';
      return li;
 }

$(document).ready(function() {
    hljs.initHighlightingOnLoad();
    hljs.initLineNumbersOnLoad();
    $(document).on('click', '.action-signout', signoutHandler);
});
