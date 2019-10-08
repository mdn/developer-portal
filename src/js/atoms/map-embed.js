/* globals mapboxgl */

/**
 * Creates a Mapbox embed with marker.
 *
 * @class MapEmbed
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
   *
   * @returns {MapEmbed[]}
   */
  static init() {
    const elements = document.querySelectorAll('.map');
    return Array.from(elements).map(element => new MapEmbed(element));
  }

  /**
   * Creates a Map, Marker and Popup based on the element’s data attributes.
   *
   * @param {Element} element
   */
  constructor(element) {
    const { lat, lng, mapId, venue } = element.dataset;
    const coords = [lng, lat];
    const map = MapEmbed.createMap(coords, mapId);
    const popup = MapEmbed.createPopup(venue);
    MapEmbed.createMarker(coords)
      .setPopup(popup)
      .addTo(map);
  }
};
