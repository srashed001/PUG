let lat = parseFloat($('#map-container').data('lat'))
let lng = parseFloat($('#map-container').data('lng'))


function initMap() {
  const myLatLng = {lat: lat, lng: lng };
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 15,
    center: myLatLng,
  });
  new google.maps.Marker({
    position: myLatLng,
    map,
    title: "Hello World!",
  });
}


