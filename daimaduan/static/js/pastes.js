$(document).ready(function() {
  var i = 1;
  var code = $('.code').last().clone();
  $('#one_more').click(function(event) {
    event.preventDefault();
    $('#codes').append($(code));
    $('.code').last().find('input').first().attr('name', 'codes-' + i + '-title');
    $('.code').last().find('textarea').first().attr('name', 'codes-' + i + '-content');
  });
});