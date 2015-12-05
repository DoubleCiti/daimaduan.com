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
      var elem = '<div class="paste" id="paste-' + paste.hash_id + '">';
      elem += '<div class="media">';
      elem += '<div class="media-left">';
      elem += '<a href="/user/' + paste.user.username + '" title="' + paste.user.username + '">';
      elem += '<img src="' + paste.user.gravatar_url + '" width="38" height="38" alt="' + paste.user.username + '" class="img-rounded" />';
      elem += '</a>';
      elem += '</div>';

      elem += '<div class="media-body">';
      elem += '<div class="paste-metas pull-right">';
      elem += '<a href="/paste/' + paste.hash_id + '" class="text-muted"><span class="fa fa-title-code-o"></span>' + paste.num_codes + '段代码</a>';
      elem += '<a href="/paste/' + paste.hash_id + '#comments" class="text-muted"><span class="fa fa-file-code-o"></span>';
      elem += '<span class="disqus-comment-count" data-disqus-identifier="' + paste.disqus_identifier + '">0条评论</span>';
      elem += '</a>';
      elem += '</div>';

      elem += '<h5 class="media-heading">';
      elem += '<a href="/paste/' + paste.hash_id + '" title="' + paste.title + '">' + paste.short_title + '</a>';
      elem += '</h5>';

      elem += '<p class="text-muted"><small>' + paste.time_passed + '</small></p>';
      elem += '</div>';

      elem += '<p class="pull-right"><a href="/paste/' + paste.hash_id + '">查看完整代码<span class="fa fa-caret-right"></span></a></p>';

      elem += '<p class="paste-tags">';
      $.each(paste.tags, function(i, tag) {
        elem += '<a href="/tag/' + tag + '" class="label label-warning tag" title="' + tag + '">' + tag + '</a>';
      });
      elem += '</p>';

      elem += '<div class="clearfix"></div>';
      elem += '</div>';

      elem += '<h5>';
      if (paste.is_private) {
        elem += '<span class="label label-default">私有</span>';
      }
      elem += '</h5>';
      return elem;
 }

$(document).ready(function() {
    hljs.initHighlightingOnLoad();
    hljs.initLineNumbersOnLoad();
    $(document).on('click', '.action-signout', signoutHandler);
});
