function signoutHandler() {
  $.ajax({
    url: '/signout',
    method: 'DELETE',
    success: function(data) {
        if (data.status == 302) {
            document.location = data.location;
        }
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
    data.text = data.watchedStatus ? "取消关注TA" : "关注TA";
    data.class_name = data.watchedStatus ? "unwatch" : "watch";

    var new_html = '<button class="btn btn-info btn-xs action action-<%= class_name %>"><%= text %></button>';

    var compiled = _.template(new_html);
    return compiled(data);
}

function toggleUserWatch() {
    var $action = $(this);
    var action = $action.is(".action-watch") ? "watch" : "unwatch";
    var username = $(".panel-heading h4").text();
    $.ajax({
        url: "/user/" + username + "/" + action,
        type: 'POST',
        success: function(data) {
            $action.replaceWith(switchWatchAction(data));
        }
    });
}

$(document).ready(function() {
    initToggleFullCode();
    $(document).on('click', '.action-signout', signoutHandler);
    $(document).on('click', '.action-watch, .action-unwatch', toggleUserWatch);
});
