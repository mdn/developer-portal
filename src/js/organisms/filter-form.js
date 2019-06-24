const AND_FILTERS = [
  'topics',
];

const OR_FILTERS = [
  'initial-group',
];

class Selector {
  static attr(key, value, append = '') {
    return `[data-${key}~="${value}"]${append}`;
  }

  static map(array, join, append) {
    return array.map(({ key, values }) => (
      values.map(value => (
        Selector.attr(key, value, append)
      )).join(join)
    )).join(join);
  }

  constructor({ and = [], or = [] }) {
    this.and = and;
    this.or = or;
  }

  createAndSelector() {
    return Selector.map(this.and, '');
  }

  createOrSelector(append) {
    return Selector.map(this.or, ', ', append);
  }

  toString() {
    const andSelector = this.createAndSelector();
    return this.createOrSelector(andSelector) || andSelector;
  }
}

export default class {
  static init() {
    const elements = document.querySelectorAll('.js-filter-form');
    return Array.from(elements).map(element => new this(element));
  }

  constructor(form) {
    this.form = form;
    const control = document.getElementById(this.form.dataset.controls);
    this.targets = control.querySelectorAll('.js-filter-target');
    this.form.addEventListener('input', () => this.filter());
    this.form.dispatchEvent(new Event('input'));
  }

  filter() {
    const formData = new FormData(this.form);

    const selector = new Selector({
      and: AND_FILTERS.map(key => ({ key, values: formData.getAll(key) })),
      or: OR_FILTERS.map(key => ({ key, values: formData.getAll(key) })),
    }).toString();

    this.targets.forEach((target) => {
      if (selector && !target.matches(selector)) {
        target.setAttribute('hidden', '');
      } else {
        target.removeAttribute('hidden');
      }
    });
  }
}
