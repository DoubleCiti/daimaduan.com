(function() {
  function initCodes() {
    var i = 1;

    $(document).on('click', '#one_more', function(event) {
      event.preventDefault();

      var $code = $('.code').last().clone();
      $code.find('input').first().attr('name', 'codes-' + i + '-title');
      $code.find('input').first().val('');
      $code.find('select').first().attr('name', 'codes-' + i + '-tag');
      $code.find('textarea').first().attr('name', 'codes-' + i + '-content');
      $code.find('textarea').first().val('');

      i += 1;
      $code.appendTo('#codes');
    });
  }

  function initRate() {
    $('#rate').raty({
      score: function() {
        return $(this).attr('data-score');
      },
      click: function(score, evt) {
        $.ajax({
          data: 'score=' + score,
          type: 'POST',
          url: '/rate/' + $(this).attr('data-id'),
          success: function() {
            return true;
          }
        });
      }
    });
  }

function initGetMore() {
  $(document).on('click', '#more_button', function(event) {
    var p = $(this).attr('data-page');
    event.preventDefault();
    $.ajax({
      data: 'p=' + p,
      type: 'GET',
      url: '/pastes/more',
      success: function(data) {
        $.each(data.pastes, function(i, paste) {
          var li = '<li class="list-group-item">';
          li += '<div class="pull-right">';
          li += '<a href="#" class="text-muted" title="' + paste.user.username + '">' + paste.user.username + '</a>';
          li += '</div>';
          li += '<a href="/paste/' + paste.hash_id + '" title="' + paste.title + '">' + paste.title + ' </a>';
          $.each(paste.tags, function(i, tag){
            li += '<a href="/tag/' + tag + '" class="btn btn-xs btn-warning" title="' + tag + '">' + tag + '</a>';
          });
          li += '<div class="clearfix"></div>';
          li += '</li>';
          $(li).insertBefore('#more_button_li');
        });
      }
    });
    $(this).attr('data-page', parseInt(p) + 1);
  });
}

  $(document).ready(function() {
    initCodes();
    initRate();
    initGetMore();
  });
})();