function signoutHandler() {
  $.ajax({
    url: '/signout',
    method: 'DELETE',
    success: function() {
      document.location = '/';
    }
  });
}

  app.faIcon = function(icon, text) {
    var template = _.template('<i class="fa fa-<%= icon %>"></i> <%= text %>');
    return template({ icon: icon, text: text });
  };

  function initToggleFullCode() {
    $(document).on('click', '.full-code-toggle', function(event) {
      event.preventDefault();
      $(this).prev().toggleClass('code_preview');
      if ($(this).text() == '显示完整代码')
        $(this).text('隐藏代码');
      else
        $(this).text('显示完整代码');
    });
  }

function switchWatchAction(data) {
    data.text = data.watchedStatus ? "取消关注" : "关注";
    data.class_name = data.watchedStatus ? "unwatch" : "watch";

    var new_html = '<button class="btn btn-info btn-xs action action-<%= class_name %>"><%= text %></button>';

    var compiled = _.template(new_html);
    return compiled(data);
}

function toggleUserWatch() {
    var $action = $(this);
    var action = $action.is(".action-watch") ? "watch" : "unwatch";
    var user_name = $(".panel-heading h4").text();
    var url = "/user/" + action;
    $.ajax({
        url: url,
        data: "user=" + user_name,
        type: 'POST',
        success: function(data) {
            $action.replaceWith(switchWatchAction(data));
        }
    });
}

$(document).ready(function() {
    hljs.initHighlightingOnLoad();
    hljs.initLineNumbersOnLoad();
    initToggleFullCode();
    $(document).on('click', '.action-signout', signoutHandler);
    $(document).on('click', '.action-watch, .action-unwatch', toggleUserWatch);
});
