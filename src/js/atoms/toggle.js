/**
 * Listens to click events on a given element, and toggles visibility of other
 * elements accordingly.
 *
 * @class Toggle
 */
module.exports = class Toggle {
  /**
   * Constructs an instance of Toggle class for each toggle element.
   *
   * @returns {Toggle[]}
   */
  static init() {
    const elements = document.querySelectorAll('.js-toggle');
    return Array.from(elements).map((element) => new Toggle(element));
  }

  /**
   * Listens to click events on the toggle element.
   *
   * @param {Element} element
.   */
  constructor(element) {
    this.toggle = element;
    element.addEventListener('click', (e) => this.onToggleClick(e));
  }

  /**
   * Constructs an instance of MapEmbed class for each map element.
   *
   * @param {Event} event
   */
  onToggleClick(event) {
    event.preventDefault();
    const { controls } = this.toggle.dataset;
    const targetEls = document.querySelectorAll(controls);

    Array.from(targetEls).forEach((targetEl) => {
      // eslint-disable-next-line no-param-reassign
      targetEl.hidden = !targetEl.hidden;
    });

    if ('hide' in this.toggle.dataset) this.toggle.hidden = true;
  }
};
