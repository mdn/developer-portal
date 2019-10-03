/**
 * Listens to hashchange events and toggles classes on a tabbed-panel element.
 */
module.exports = class TabbedPanels {
  /**
   * Constructs an instance of Toggle class for each toggle element.
   *
   * @returns {Element[]}
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
    this.backgrounds = Array.from(
      element.querySelectorAll('.tabbed-panels-content-bg'),
    );
    this.toggles = Array.from(
      element.querySelectorAll('.tabbed-panels-toggle'),
    );
    this.nav = element.querySelector('.tabbed-panels-nav');

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
    this.backgrounds.forEach((background, index) => {
      if (index) background.classList.remove('displayed');
    });
    if (this.toggles.length > 1) {
      this.nav.classList.remove('hidden');
    }
  }

  /**
   * Set CSS classes on elements based on location.hash values.
   */
  showContent() {
    const { hash } = window.location;
    if (!hash) return;

    this.toggles.forEach(toggle => {
      if (toggle.attributes.getNamedItem('href').value === hash) {
        toggle.classList.add('highlight2');
        toggle.classList.remove('highlight2-inverse');
      } else {
        toggle.classList.add('highlight2-inverse');
        toggle.classList.remove('highlight2');
      }
    });

    this.backgrounds.forEach(background => {
      if (`#${background.dataset.hash}` === hash) {
        background.classList.add('displayed');
      } else {
        background.classList.remove('displayed');
      }
    });
  }
};
