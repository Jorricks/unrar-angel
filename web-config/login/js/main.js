$(window, document, undefined).ready(function() {

  $('input').blur(function() {
    var $this = $(this);
    if ($this.val())
      $this.addClass('used');
    else
      $this.removeClass('used');
  });

  var $ripples = $('.ripples');

  $ripples.on('click.Ripples', function(e) {

    var $this = $(this);
    var $offset = $this.parent().offset();
    var $circle = $this.find('.ripplesCircle');

    var x = e.pageX - $offset.left;
    var y = e.pageY - $offset.top;

    $circle.css({
      top: y + 'px',
      left: x + 'px'
    });

    $this.addClass('is-active');

  });

  $ripples.on('animationend webkitAnimationEnd mozAnimationEnd oanimationend MSAnimationEnd', function(e) {
  	$(this).removeClass('is-active');
  });

});

$passwordIsWrongNote = '';
$(document).ready(function(){
  $passwordIsWrongNote = $('.possible-error');
  $('#form1').submit(function(event){
    event.preventDefault();
    checkPassword();
  })
});

function checkPassword(){
  var url = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '') + '/get_api_info/';
  var pass = $('#pass').val();
  $.getJson(url + pass)
      .done(function(json){
        if(json.data === "valid"){
          // Valid
            createCookie('password', pass, '100');
            location.reload();
        } else {
          // Invalid
            $passwordIsWrongNote.show();
        }
      })
}

function createCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}