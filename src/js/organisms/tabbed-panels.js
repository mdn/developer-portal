/**
 * Listens to hashchange events and toggles classes on a tabbed-panel element.
 *
 * @class TabbedPanels
 */
module.exports = class TabbedPanels {
  /**
   * Constructs an instance of Toggle class for each toggle element.
   *
   * @returns {TabbedPanels[]}
   */
  static init() {
    const elements = document.querySelectorAll('.js-tabbed-panels');
    return Array.from(elements).map(element => new this(element));
  }

  /**
   * Finds various elements and listens for hashchange events.
   *
   * @param {Element} element
   */
  constructor(element) {
    this.contentItems = Array.from(
      element.querySelectorAll('.tabbed-panels-item'),
    );
    this.navItems = Array.from(
      element.querySelectorAll('.tabbed-panels-nav-item'),
    );

    this.setInitialState();

    window.addEventListener('hashchange', this.showContent.bind(this));

    if (window.location.hash) {
      this.showContent();
    }
  }

  /**
   * Sets the initial state on elements.
   */
  setInitialState() {
    this.contentItems.forEach((background, index) => {
      if (index) background.classList.remove('is-active');
    });
  }

  /**
   * Set CSS classes on elements based on location.hash values.
   */
  showContent() {
    const { hash } = window.location;

    if (!hash) return;

    const hashes = this.contentItems.map(el => `#${el.dataset.hash}`);

    if (!hashes.includes(hash)) return;

    this.navItems.forEach(item => {
      if (item.attributes.getNamedItem('href').value === hash) {
        item.classList.add('is-active');
      } else {
        item.classList.remove('is-active');
      }
    });

    this.contentItems.forEach(item => {
      if (`#${item.dataset.hash}` === hash) {
        item.classList.add('is-active');
      } else {
        item.classList.remove('is-active');
      }
    });
  }
};
