function signoutHandler() {
  $.ajax({
    url: '/signout',
    method: 'DELETE',
    success: function() {
      document.location = '/';
    }
  });
}

$(document).ready(function() {
    hljs.initHighlightingOnLoad();
    $(document).on('click', '.action-signout', signoutHandler);
});
