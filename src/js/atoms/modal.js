module.exports = class Modal {
  static createModalOptions({
    dataset: {
      className = 'mzp-has-media',
      closeText = 'Close modal',
      title = 'Example headline with 35 characters',
    } = {},
  } = {}) {
    return { className, closeText, title };
  }

  static init() {
    const contentEls = document.querySelectorAll('.mzp-u-modal-content');
    Array.from(contentEls).forEach(content => new Modal(content));
  }

  constructor(content) {
    this.content = content;
    this.bindListeners();
  }

  bindListeners() {
    const selector = `.js-modal-trigger[data-modal=${this.content.id}]`;
    const modalTriggers = document.querySelectorAll(selector);
    Array.from(modalTriggers).forEach(modalTrigger => {
      modalTrigger.addEventListener('click', event => this.toggle(event));
    });
  }

  toggle(event) {
    event.preventDefault();
    const target = event.currentTarget || event.target;
    const options = Modal.createModalOptions(target);
    Mzp.Modal.createModal(target, this.content, options);
  }
}
