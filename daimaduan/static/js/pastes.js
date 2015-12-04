(function() {
  function initPaste() {
    $(document).on('click', '#delete-paste', function(event) {
      event.preventDefault();
      var r = confirm("确定删除这个代码集合吗?");
      if  (r == true) {
        location.href = $(this).attr('href');
      }
    })
  }

  function initCodes() {
    $(document).on('click', '#one_more', function(event) {
      event.preventDefault();

      var i = $("#codes > .code").length;
      var $code = $('.code').last().clone();

      $code.find('input').first().attr('name', 'codes-' + i + '-title');
      $code.find('input').first().val('');
      $code.find('select').first().attr('name', 'codes-' + i + '-tag');
      $code.find('select').first().val('');
      $code.find('textarea').first().attr('name', 'codes-' + i + '-content');
      $code.find('textarea').first().val('');

      $code.find('div.form-group').last().css('display', 'block');

      $code.appendTo('#codes');
    });

    $(document).on('click', '.remove-code', function(event) {
      event.preventDefault();
      var i = $("#codes > .code").length;
      if (i == 1) {
        $(this).attr('disabled', 'disabled');
      } else {
        $(this).parent().parent().parent().remove();
        $.each($("#codes > .code"), function(i, code) {
          $(code).find('input').first().attr('name', 'codes-' + i + '-title');
          $(code).find('select').first().attr('name', 'codes-' + i + '-tag');
          $(code).find('textarea').first().attr('name', 'codes-' + i + '-content');
        });
      }

    });
    $(this).attr('data-page', parseInt(p) + 1);
  }

  function renderLikePasteAction(data) {
    data.text = data.liked ? '取消喜欢' : '喜欢';
    data.class_name = data.liked ? 'unlike' : 'like';

    var template = ''
      + '<a href="javascript:;" title="<%= text %>"'
      + '   class="btn btn-default btn-xs action action-<%= class_name %>"'
      + '   data-id="<%= paste_id %>">'
      + '  <i class="fa fa-heart"></i> <span><%= text %></span>'
      + '  <%= paste_likes %>'
      + '</a>'
    var compiled = _.template(template);
    return compiled(data);
  }

  function togglePasteLike() {
    var $action = $(this);
    var pasteId = $action.data('id');
    var action  = $action.is('.action-like') ? 'like' : 'unlike';
    var url     = '/paste/' + pasteId + '/' + action;

    $.post(url).then(function(data) {
      // Update paste likes count
      $action.replaceWith(renderLikePasteAction(data));

      // Update user paste likes count
      var $user = $('[data-user="' + app.current_user.id + '"]');
      $user.find('.paste-likes-count').html(data.user_like);
    });
  }

  function initGetMore() {
    $(document).on('click', '#more_button', function(event) {
      var p = $(this).attr('data-page');
      event.preventDefault();
      $.ajax({
        data: 'p=' + p,
        dataType: 'html',
        type: 'GET',
        url: '/pastes/more',
        success: function(data) {
          $(data).insertBefore('#more_button_li');
        }
      });
      $(this).attr('data-page', parseInt(p) + 1);
    });
  }

  function initSearchGetMore() {
    $(document).on('click', '#search_more_button', function(event) {
      var p = $(this).attr('data-page');
      var keyword = $(this).attr('data-keyword');
      event.preventDefault();
      $.ajax({
        data: 'q=' + keyword + '&p=' + p,
        dataType: 'html',
        type: 'GET',
        url: '/search_more',
        success: function(data) {
          $(data).insertBefore('#more_button_li');
        }
      });
      $(this).attr('data-page', parseInt(p) + 1);
    });
  }

  $(document).ready(function() {
    initPaste();
    initCodes();
    initGetMore();
    initSearchGetMore();

    $(document).on('click', '.action-like, .action-unlike', togglePasteLike);
  });
})();
