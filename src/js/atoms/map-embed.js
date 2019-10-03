/* globals mapboxgl */

/**
 * Creates a Map Box embed with marker.
 */
module.exports = class MapEmbed {
  /**
   * Returns a Map instance from options.
   *
   * @param {Array<number>} center
   * @param {Element} container
   * @param {string} style
   * @param {number} zoom
   * @returns {mapboxgl.Map}
   */
  static createMap(
    center,
    container,
    style = 'mapbox://styles/mapbox/light-v10',
    zoom = 16,
  ) {
    return new mapboxgl.Map({ center, container, style, zoom });
  }

  /**
   * Returns a Marker instance and sets coordinates.
   *
   * @param {Array<number>} coords
   * @returns {mapboxgl.Marker}
   */
  static createMarker(coords) {
    const el = document.createElement('div');
    el.classList.add('marker');
    return new mapboxgl.Marker(el).setLngLat(coords);
  }

  /**
   * Returns a Popup instance and sets its HTML.
   *
   * @param {string} content
   * @returns {mapboxgl.Popup}
   */
  static createPopup(content) {
    return new mapboxgl.Popup({ offset: 25 }).setHTML(`<p>${content}</p>`);
  }

  /**
   * Constructs an instance of MapEmbed class for each map element.
   */
  static init() {
    const maps = Array.from(document.querySelectorAll('.map'));
    maps.forEach(el => new MapEmbed(el));
  }

  /**
   * Creates a Map, Marker and Popup based on the element’s data attributes.
   *
   * @param {Element} el
   */
  constructor(el) {
    const { lat, lng, mapId, venue } = el.dataset;
    const coords = [lng, lat];
    const map = MapEmbed.createMap(coords, mapId);
    const popup = MapEmbed.createPopup(venue);
    MapEmbed.createMarker(coords)
      .setPopup(popup)
      .addTo(map);
  }
};
