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
    if ($('#form-paste').size() == 0) return;

    var makeOption = function(input) {
        return {
          value: input,
          text: input
        };
    };

    // https://gist.github.com/james2doyle/85e503c77e581df6a5c0
    Vue.directive('selectize-tags', {
      twoWay: true,
      priority: 1000,
      bind: function (tags) {
        var self = this;
        $(this.el).selectize({
          delimiter: ',',
          persist: false,
          create: makeOption,
          onChange: function (val) {
            self.set(val);
          },
          onItemRemove: function(value) {
            // Avoid to delete syntax tags
            if (_.includes(self.vm.syntaxTags, value)) {
              self.update(self.vm.tags);
            }
          }
        });
      },
      update: function (tags) {
        var selectize = $(this.el).data('selectize');
        selectize.clearOptions();

        _.each(tags, function(tag) {
            selectize.addOption(makeOption(tag));
            selectize.addItem(tag);
        });
      },
      unbind: function () {
        $(this.el).destroy();
      }
    });

    var newCode = { title: "", syntax: "text", content: "" };
    new Vue({
      el: "#form-paste",
      data: {
        lexers: lexers,
        paste: app.paste,
        errors: {},
        customTags: [],
      },
      created: function() {
        this.sliceCustomTags(app.paste.tags);
      },
      computed: {
        codeRemovable: function() {
          return this.paste.codes.length > 1;
        },
        codeIncreasable: function() {
          return this.paste.codes.length < 7;
        },
        syntaxTags: function() {
            return _.map(app.paste.codes, 'syntax') || [];
        },
        tags: {
            get: function() {
                return this.syntaxTags.concat(this.customTags);
            },

            set: function(tags) {
                this.sliceCustomTags(tags.split(','));
            }
        }
      },
      methods: {
        sliceCustomTags: function(inputTags) {
            this.customTags = _.chain(inputTags || [])
                               .difference(this.syntaxTags)
                               .compact()
                               .uniq()
                               .value();
            this.paste.tags = this.tags.join(',');
        },
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
          var formData = this.paste;
          
          $.ajax({
            url: document.location.href,
            method: 'POST',
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify(formData),
            success: function(data) {
              if (data.success) {
                document.location = '/paste/' + data.hash_id;
              } else {
                self.errors = data.errors;
              }
            }
          });
        },
        syntaxChanged: function() {
          this.sliceCustomTags(this.syntaxTags.concat(this.customTags));
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
