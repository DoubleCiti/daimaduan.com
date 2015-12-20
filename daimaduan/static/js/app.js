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
    hljs.initLineNumbersOnLoad();
    $(document).on('click', '.action-signout', signoutHandler);
});
