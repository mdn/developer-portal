/**
 * Listens to click events on a given element, and toggles visibility of other
 * elements accordingly.
 */
module.exports = class Toggle {
  /**
   * Constructs an instance of Toggle class for each toggle element.
   */
  static init() {
    const elements = Array.from(document.querySelectorAll('.js-toggle'));
    Array.from(elements).forEach(element => new this(element));
  }

  /**
   * Listens to click events on the toggle element.
   *
   * @param {Element} element
.   */
  constructor(element) {
    this.toggle = element;
    element.addEventListener('click', e => this.onToggleClick(e));
  }

  /**
   * Constructs an instance of MapEmbed class for each map element.
   *
   * @param {Event} event
   */
  onToggleClick(event) {
    event.preventDefault();
    const { controls, hide } = this.toggle.dataset;
    const targetEls = document.querySelectorAll(controls);

    Array.from(targetEls).forEach(targetEl => {
      // eslint-disable-next-line no-param-reassign
      targetEl.hidden = !targetEl.hidden;
    });

    if (hide) this.toggle.hidden = false;
  }
};
