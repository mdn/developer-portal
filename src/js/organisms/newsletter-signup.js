export default class {
  static init() {
    const elements = document.querySelectorAll('.js-newsletter-signup');
    return Array.from(elements).map(element => new this(element));
  }

  constructor(element) {
    this.element = element;
    const input = element.querySelector('#newsletter-email');
    input.addEventListener('click', () => this.showNewsletterContent());
  }

  showNewsletterContent() {
    const content = this.element.querySelectorAll('.js-newsletter-signup-content');
    console.log('content', content);
    Array.from(content).forEach(element => {
      element.removeAttribute('hidden');
    });
  }
}
