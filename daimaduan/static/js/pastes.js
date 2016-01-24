(function() {
  function initPaste() {
    $(document).on('click', '.action-del', function(event) {
      if (!confirm("确认删除吗?")) {
        event.preventDefault();
        return false;
      }
    })
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

  function selectEmbedCode() {
    $('.input-group-embed :text').select();
  }

  function initPasteEditor() {
    var newCode = { title: "", syntax: "text", content: "" };
    var codes = new Vue({
      el: "#form-paste",
      data: {
        lexers: lexers,
        paste: {
          title: "",
          is_private: false,
          codes: [_.clone(newCode)]  
        }
        
      },
      computed: {
        codeRemovable: function() {
          return this.paste.codes.length > 1;
        }
      },
      methods: {
        addCode: function() {
          this.paste.codes.push(_.clone(newCode));
        },
        removeCode: function(code) {
          this.paste.codes.$remove(code);
        },
        submitPaste: function() {
          console.log(JSON.stringify(this.paste, null, "  "));
          alert("Not implemented.");
        }
      }
    });
  }

  $(document).ready(function() {
    initPaste();
    initGetMore();
    initSearchGetMore();
    initPasteEditor();

    $('.input-group-embed').on('click', selectEmbedCode);
    $('.input-group-embed :text').on('focus', selectEmbedCode);
    $(document).on('click', '.action-like, .action-unlike', togglePasteLike);
  });
})();
