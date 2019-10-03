/* globals mapboxgl */
module.exports = class MapEmbed {
  static init() {
    const maps = Array.from(document.querySelectorAll('.map'));
    maps.forEach(mapEl => {
      const map = new mapboxgl.Map({
        container: mapEl.dataset.mapId,
        style: 'mapbox://styles/mapbox/light-v10',
        center: [mapEl.dataset.lng, mapEl.dataset.lat],
        zoom: 16,
      });

      const geojson = {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [mapEl.dataset.lng, mapEl.dataset.lat],
            },
            properties: {
              venue: mapEl.dataset.venue,
            },
          },
        ],
      };

      geojson.features.forEach(marker => {
        const el = document.createElement('div');
        el.className = 'marker';
        new mapboxgl.Marker(el)
          .setLngLat(marker.geometry.coordinates)
          .setPopup(
            new mapboxgl.Popup({ offset: 25 }).setHTML(
              `<p>${marker.properties.venue}</p>`,
            ),
          )
          .addTo(map);
      });
    });
  }
};
