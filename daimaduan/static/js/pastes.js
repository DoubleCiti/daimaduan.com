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

function initGetMore() {
  $(document).on('click', '#more_button', function(event) {
    var p = $(this).attr('data-page');
    event.preventDefault();
    $.ajax({
      data: 'p=' + p,
      type: 'GET',
      url: '/pastes/more',
      success: function(data) {
        if (data.pastes.length < 20) {
            $('#more_button').attr('disabled', 'disabled');
        }
        $.each(data.pastes, function(i, paste) {
          var li = createLi(paste);
          $(li).insertBefore('#more_button_li');
        });
      }
    });
    $(this).attr('data-page', parseInt(p) + 1);
  });
}

  $(document).ready(function() {
    initCodes();
    initGetMore();
  });
})();
