(function() {

var sock = SockJS(location.origin + '/notifier');
sock.onopen = function() {
  console.log('connected');
}
sock.onclose = function() {
  console.log('disconnected');
}

})();
