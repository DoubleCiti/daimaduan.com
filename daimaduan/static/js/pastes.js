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

  function pasteCodeAction() {
    $('#tags').tagsinput('removeAll');
    $('div.codes textarea').each(function(i, item) {
      hl = hljs.highlightAuto($(item).val());
      $('#tags').tagsinput('add', hl.language);
      var select_div = $(item)[0].parentNode.parentNode.previousElementSibling;
      $(select_div).find('select').val(hl.language);
    });
  }
  
  function initPasteEditor() {
    if ($('#form-paste').size() == 0) return;

    var newCode = { title: "", syntax: "text", content: "" };
    new Vue({
      el: "#form-paste",
      data: {
        lexers: lexers,
        paste: app.paste,
        errors: {}
      },
      computed: {
        codeRemovable: function() {
          return this.paste.codes.length > 1;
        },
        codeIncreasable: function() {
          return this.paste.codes.length < 7;
        }
      },
      methods: {
        codeHasError: function(index, field) {
          try {
            var error = this.errors.codes[index][field];
            return error ? 'has-error' : '';
          } catch(e) {
            return '';
          }
        },
        addCode: function() {
          this.paste.codes.push(_.clone(newCode));
        },
        removeCode: function(code) {
          this.paste.codes.$remove(code);
          setTimeout(pasteCodeAction, 200);
        },
        submitPaste: function() {
          var self = this;
          
          console.log($('#tags').val());

          $.ajax({
            url: document.location.href,
            method: 'POST',
            dataType: 'json',
            data: $('#form-paste').serialize() + '&tags=' + $('#tags').val(),
            success: function(data) {
              if (data.success) {
                document.location = '/paste/' + data.hash_id;
              } else {
                self.errors = data.errors;
              }
            }
          });
        }
      }
    });
  }

  $(document).ready(function() {
    initPaste();
    initPasteEditor();

    $('.bootstrap-tagsinput').addClass('form-control');
    
    $('.input-group-embed').on('click', selectEmbedCode);
    $('.input-group-embed :text').on('focus', selectEmbedCode);
    $(document).on('click', '.action-like, .action-unlike', togglePasteLike);

    var clipboard = new Clipboard('.copy-code', {
      text: function(trigger) {
        var nextElement = $(trigger)[0].parentNode.nextElementSibling;
        return $(nextElement).find('div.highlight').text();
      }
    });
    
    clipboard.on('success', function(e) {
      $(e.trigger).tooltip('toggle');
    })
  });
})();
