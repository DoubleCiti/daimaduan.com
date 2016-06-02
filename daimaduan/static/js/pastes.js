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

  function syntaxSelectAction() {
    var $tags = $('#tags');
    var tags = [];
    if ($tags.val() != '')
        tags = $tags.val().split(',');
    $.each(languages, function(i, language) {
      var index = tags.indexOf(language);
      delete tags[index];
    });
    languages = [];
    $('div.codes select').each(function(i, select) {
      tags.push($(select).val());
      languages.push($(select).val());
    });
    $tags.tagsinput('removeAll');
    $.each(tags, function(i, language) {
      $tags.tagsinput('add', language);
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
        },
        submitPaste: function() {
          var self = this;
          
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
        },
        codeChanged: function(code) {
          var hl = hljs.highlightAuto(code.content);
          var primarySyntax = hl.language;
          var secondarySyntax = hl.second_best && hl.second_best.language;

          code.syntax = hl.primarySyntax || secondarySyntax;
        }
      }
    });
  }

  $(document).ready(function() {
    initPaste();
    initPasteEditor();
    
    languages = [];

    $('.bootstrap-tagsinput').addClass('form-control');
    
    $('.input-group-embed').on('click', selectEmbedCode);
    $(document).on('click', '.input-group-embed', selectEmbedCode);
    $(document).on('focus', '.input-group-embed :text', selectEmbedCode);
    $(document).on('click', '.action-like, .action-unlike', togglePasteLike);
    $(document).on('change', 'div.codes select', syntaxSelectAction);

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
