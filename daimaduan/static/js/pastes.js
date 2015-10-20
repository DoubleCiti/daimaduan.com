(function() {
  function initCodes() {
    var i = 1;
    

    $(document).on('click', '#one_more', function(event) {
      event.preventDefault();

      var $code = $('.code').last().clone();
      $code.find('input').first().attr('name', 'codes-' + i + '-title');
      $code.find('textarea').first().attr('name', 'codes-' + i + '-content');

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

  $(document).ready(function() {
    initCodes();
    initRate();
  });
})();