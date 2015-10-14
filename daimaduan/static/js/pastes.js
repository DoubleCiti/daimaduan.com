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

  $(document).ready(function() {
    initCodes();
  });
})();