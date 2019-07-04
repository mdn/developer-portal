export default class {
  static init() {
    const elements = document.querySelectorAll('.js-get-started');
    return Array.from(elements).map(element => new this(element));
  }

  constructor(element) {
    this.backgrounds = Array.from(element.querySelectorAll('.get-started-content-bg'));
    this.toggles = Array.from(element.querySelectorAll('.get-started-toggle'));
    this.nav = element.querySelector('.get-started-nav');

    this.setInitialState();

    window.addEventListener('hashchange', this.showContent.bind(this));

    if (window.location.hash) {
      this.showContent();
    }
  }

  setInitialState() {
    this.backgrounds.forEach((background, index) => {
      if (index) background.classList.remove('displayed');
    });
    if (this.toggles.length > 1) {
      this.nav.classList.remove('hidden');
    }
  }

  showContent() {
    const { hash } = window.location;
    if (!hash) return;

    this.toggles.forEach((toggle) => {
      if (toggle.attributes.getNamedItem('href').value === hash) {
        toggle.classList.add('highlight2-inverse');
        toggle.classList.remove('highlight2');
      } else {
        toggle.classList.add('highlight2');
        toggle.classList.remove('highlight2-inverse');
      }
    });

    this.backgrounds.forEach((background) => {
      if (`#${background.dataset.hash}` === hash) {
        background.classList.add('displayed');
      } else {
        background.classList.remove('displayed');
      }
    });
  }
}
