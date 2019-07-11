const AND_FILTERS = [
  'topics',
];

const OR_FILTERS = [
  'initial-group',
  'month',
];

class Selector {
  static attr(key, value, append = '') {
    return `[data-${key}~="${value}"]${append}`;
  }

  static map(array, join, append) {
    return array.map(({ key, values }) => (
      values.map(value => (
        Selector.attr(key, value, append)
      ))
      .filter(Boolean)
      .join(join)
    ))
    .filter(Boolean)
    .join(join);
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

    // Stores all resource matches based on the current filter (irrespective of
    // page or number of resources currently shown).
    this.matches = [];

    this.initialResources = parseInt(this.form.dataset.initialResources);
    this.resourcesPerPage = parseInt(this.form.dataset.resourcesPerPage || this.initialResources);

    // Keeps track of the current number of resources on the page. This is used
    // primarily for pagination.
    this.resourcesOnPage = this.initialResources;

    const control = document.getElementById(this.form.dataset.controls);
    this.targetEls = control.querySelectorAll('.js-filter-target');
    this.actionsEl = document.getElementById('js-filter-list-actions');
    this.nextPageButton = document.getElementById('js-filter-list-action-see-more');
    this.clearButtons = document.querySelectorAll('.js-filter-clear');
    this.noResultsEl = document.getElementById('js-filter-list-no-results');

    this.setupEvents();
  }

  setupEvents() {
    Array.from(this.clearButtons).forEach(btn => {
      btn.addEventListener('click', (e) => this.clearCheckboxes(e));
    });

    this.nextPageButton.addEventListener('click', (e) => this.nextPage(e));

    this.form.addEventListener('input', () => this.filter());
    this.form.dispatchEvent(new Event('input'));
  }

  filter() {
    const formData = new FormData(this.form);
    const selector = new Selector({
      and: AND_FILTERS.map(key => ({ key, values: formData.getAll(key) })),
      or: OR_FILTERS.map(key => ({ key, values: formData.getAll(key) })),
    }).toString();

    this.matches = Array.from(this.targetEls).reduce((acc, target) => {
      if (!selector || (selector && target.matches(selector))) {
        acc.push(target);
      }

      return acc;
    }, []);

    this.render();
  }

  nextPage(e) {
    e.preventDefault();
    if (this.matches.length >= this.resourcesOnPage) {
      this.resourcesOnPage += this.resourcesPerPage;
      this.render();
    }
  }

  clearCheckboxes(e) {
    e.preventDefault();
    const { controls } = e.target.dataset;
    const checkboxes = this.form.querySelectorAll('input[type=checkbox]');
    const matchedCheckboxes = Array.from(checkboxes).filter(checkbox =>
      (!controls || checkbox.name === controls) && checkbox.checked);

    matchedCheckboxes.forEach(checkbox => {
      checkbox.checked = false;
    });

    if (matchedCheckboxes.length) {
      this.form.dispatchEvent(new Event('input'));
    }
  }

  render() {
    if (this.matches.length <= this.resourcesOnPage) {
      this.actionsEl.setAttribute('hidden', '');
    } else {
      this.actionsEl.removeAttribute('hidden');
    }

    // Limit the number of matched resources to the current page number.
    const pagedMatches = this.matches.slice(0, this.resourcesOnPage);

    // Show/hide resources on the page based on whether they're included within
    // the filter matches.
    Array.from(this.targetEls).forEach((target) => {
      if (pagedMatches.includes(target)) {
        target.removeAttribute('hidden');
      } else {
        target.setAttribute('hidden', '');
      }
    });

    // Show "no resources" message if no resources match the current filters.
    if (pagedMatches.length === 0) {
      this.noResultsEl.removeAttribute('hidden');
    } else {
      this.noResultsEl.setAttribute('hidden', '');
    }
  }
}
