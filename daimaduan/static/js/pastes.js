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

  $(document).ready(function() {
    initPaste();
    initCodes();
    initGetMore();
  });
})();
