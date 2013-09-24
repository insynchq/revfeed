(function() {

var sock = SockJS(location.origin + '/notifier');
sock.onopen = function() {
  console.log('connected');
}
sock.onclose = function() {
  console.log('disconnected');
}

$('time').each(function() {
  var $el = $(this);
  $el.text(
    moment.unix(
      parseInt($el.text(), 10)
    ).utc().calendar()
  );
});

})();
