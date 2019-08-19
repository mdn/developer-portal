module.exports = class Toggle {
  static init() {
    const elements = Array.from(document.querySelectorAll('.js-toggle'));
    return Array.from(elements).map(element => new this(element));
  }

  constructor(element) {
    element.addEventListener('click', e => this.onToggleClick(e));
  }

  // eslint-disable-next-line class-methods-use-this
  onToggleClick(e) {
    e.preventDefault();
    const { controls } = e.target.dataset;
    const targetEls = document.querySelectorAll(controls);

    Array.from(targetEls).forEach(targetEl => {
      if (targetEl.hasAttribute('hidden')) {
        targetEl.removeAttribute('hidden');
      } else {
        targetEl.setAttribute('hidden', '');
      }
    });

    if ('hide' in e.target.dataset) {
      e.target.setAttribute('hidden', '');
    }
  }
};
