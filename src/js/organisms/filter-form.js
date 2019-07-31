const { parseForm, parseQueryParams } = require('../utils');

module.exports = class FilterForm {
  static init() {
    const elements = document.querySelectorAll('.js-filter-form');
    return Array.from(elements).map(element => new this(element));
  }

  constructor(form) {
    this.form = form;

    // A representation of the current state of the form.
    this.state = parseQueryParams();

    // Stores all resource matches based on the current filter (irrespective of
    // page or number of resources currently shown).
    this.matches = [];

    this.initialResources = parseInt(this.form.dataset.initialResources, 10);
    this.resourcesPerPage = parseInt(
      this.form.dataset.resourcesPerPage || this.initialResources,
      10,
    );

    // Keeps track of the current number of resources on the page. This is used
    // primarily for pagination.
    this.resourcesOnPage = this.initialResources;

    // Elements for the filter form/list.
    const control = document.getElementById(this.form.dataset.controls);
    this.targetEls = control.querySelectorAll('.js-filter-target');
    this.actionsEl = document.getElementById('js-filter-list-actions');
    this.nextPageButton = document.getElementById(
      'js-filter-list-action-next-page',
    );
    this.clearButtons = document.querySelectorAll('.js-filter-clear');
    this.noResultsEl = document.getElementById('js-filter-list-no-results');
    this.clearSectionEls = document.querySelectorAll(
      '.js-filter-form-clear-section',
    );

    this.updateCheckboxes();
    this.setupEvents();
    this.render();
  }

  /** Sets up event listeners. */
  setupEvents() {
    Array.from(this.clearButtons).forEach(btn => {
      btn.addEventListener('click', e => this.uncheckInputs(e));
    });

    this.nextPageButton.addEventListener('click', e => this.nextPage(e));
    this.form.addEventListener('input', () => this.onFormInput());
  }

  /** Updates state and re-renders the results when an input is updated. */
  onFormInput() {
    this.state = parseForm(this.form);
    this.render();
  }

  /** Ensures the DOM reflects the current state. Used after query parameter loading. */
  updateCheckboxes() {
    Object.entries(this.state).forEach(pair => {
      pair[1].forEach(value => {
        const el = this.form.querySelector(
          `input[name='${pair[0]}'][value='${value}']`,
        );
        if (el) {
          el.checked = true;
        }
      });
    });
  }

  /** Uncheck checkboxes by the section they appear in.  */
  uncheckInputs(e) {
    e.preventDefault();
    const { controls } = e.target.dataset;
    const checkboxes = this.form.querySelectorAll('input[type=checkbox]');
    const matchedCheckboxes = Array.from(checkboxes).filter(
      checkbox => (!controls || checkbox.name === controls) && checkbox.checked,
    );

    matchedCheckboxes.forEach(checkbox => {
      // eslint-disable-next-line no-param-reassign
      checkbox.checked = false;
    });

    if (matchedCheckboxes.length) {
      this.form.dispatchEvent(new Event('input'));
    }
  }

  /** Toggles the visibility of clear buttons depending on selected filters. */
  updateClearVisibility() {
    const checkedControls = Object.keys(this.state);

    Array.from(this.clearButtons).forEach(btn => {
      const { controls } = btn.dataset;

      if (checkedControls.includes(controls)) {
        btn.removeAttribute('hidden');
      } else if (controls) {
        btn.setAttribute('hidden', '');
      }
    });

    if (checkedControls.length) {
      Array.from(this.clearSectionEls).forEach(el =>
        el.removeAttribute('hidden'),
      );
    } else {
      Array.from(this.clearSectionEls).forEach(el =>
        el.setAttribute('hidden', ''),
      );
    }
  }

  /** Updates the URL to include selected filters. */
  updateUrlParams() {
    const stringResult = Object.entries(this.state)
      .map(pair => {
        return `${pair[0]}=${pair[1].join(',')}`;
      }, [])
      .join('&');

    if (stringResult) {
      window.history.replaceState({}, '', `?${stringResult}`);
    } else {
      window.history.replaceState({}, null, '.');
    }
  }

  /** Shows the next page of items. */
  nextPage(e) {
    e.preventDefault();
    if (this.matches.length >= this.resourcesOnPage) {
      this.resourcesOnPage += this.resourcesPerPage;
      this.render();
    }
  }

  /** Filters the items by applying the selected filters. */
  filter() {
    this.matches = [];

    if (!Object.keys(this.state).length) {
      this.matches = Array.from(this.targetEls);
      return;
    }

    Array.from(this.targetEls).forEach(el => {
      const results = Object.entries(this.state).map(([key, values]) => {
        const dataValues = el.dataset[key] ? el.dataset[key].split(' ') : [];
        return values.some(value => dataValues.includes(value));
      });

      if (results.every(Boolean)) {
        this.matches.push(el);
      }
    });
  }

  /** Re-renders the items based on the current state. */
  render() {
    this.filter();
    this.updateClearVisibility();

    if (this.matches.length <= this.resourcesOnPage) {
      this.actionsEl.setAttribute('hidden', '');
    } else {
      this.actionsEl.removeAttribute('hidden');
    }

    // Limit the number of matched resources to the current page number.
    const pagedMatches = this.matches.slice(0, this.resourcesOnPage);

    // Show/hide resources on the page based on whether they're included within
    // the filter matches.
    Array.from(this.targetEls).forEach(target => {
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

    this.updateUrlParams();
  }
};
