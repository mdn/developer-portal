const { parseQueryParams, decodeFormURLEncodedSpaces } = require('../utils');

/**
 * Represents a directory page filter form; a traditional form-submission button
 * triggers server-side rendering of appropriately filtered results
 *
 * @class FilterForm
 */
module.exports = class FilterForm {
  /**
   * Constructs an instance of FilterForm class for each element.
   *
   * @returns {FilterForm[]}
   */
  static init() {
    const elements = document.querySelectorAll('.js-filter-form');
    return Array.from(elements).map((element) => new this(element));
  }

  /**
   * Gets initial state, fetches elements and calls setup methods.
   *
   * @param {Element} form
.  */
  constructor(form) {
    this.form = form;

    // A representation of the current state of the form.
    this.state = parseQueryParams();

    // Elements for the filter form/list.
    // IMPORTANT: there are TWO forms in any page featuring this component: one for
    // desktop viewports and one for mobile/collapsed-menu filtering

    this.clearButtons = document.querySelectorAll('.js-filter-clear');
    this.clearSectionEls = document.querySelectorAll(
      '.js-filter-form-clear-section',
    );

    this.clearSearchButtons = document.querySelectorAll('.js-search-clear');

    this.updateFormControls();
    this.setupEvents();
    this.updateClearVisibility();
  }

  /** Sets up event listeners. */
  setupEvents() {
    Array.from(this.clearButtons).forEach((btn) => {
      btn.addEventListener('click', (e) => this.uncheckInputs(e));
    });
    Array.from(this.clearSearchButtons).forEach((btn) => {
      btn.addEventListener('click', (e) => this.clearSearchFields(e));
    });
    this.form.addEventListener('submit', (e) => this.onFormSubmit(e));
  }

  /**
   * Before the form is submitted, skip over an empty search field, if
   * present. Why? to avoid `search=` appearing in the URL whenever
   * filters are set but there is no search term
   *
   * @param {Event} e
   */
  onFormSubmit(e) {
    e.preventDefault();
    const searchFields = this.form.querySelectorAll("input[name='search']");
    Array.from(searchFields).forEach((field) => {
      if (!field.value) {
        // eslint-disable-next-line no-param-reassign
        field.disabled = true; // disabled fields are not submitted to the server
      }
    });

    this.form.submit();
    /**
     * Note: when this switches to an AJAX submission, remember to
     * re-enable the search field after submission!
     */
  }

  /**
   * Ensures the DOM elements for the filter form (checkboxes and search input - if relevant)
   * reflect the current state.
   *
   * Used after query parameter loading.
   */
  updateFormControls() {
    Object.entries(this.state).forEach((pair) => {
      const [key, val] = pair;
      if (key === 'search') {
        // Search input requires specific behaviour
        const searchInput = this.form.querySelectorAll(`input[name='${key}']`); // only one searchInput _per form_
        /* because application/x-www-form-urlencoded has spaces turned
         * to `+` not `%20`, we need to do a bit more work */
        searchInput[0].value = decodeFormURLEncodedSpaces(val[0]);
      } else {
        // set the checkboxes as appropriate to the querystring
        val.forEach((value) => {
          const el = this.form.querySelector(
            `input[name='${key}'][value='${value}']`,
          );
          if (el) {
            el.checked = true;
          }
        });
      }
    });
  }

  /**
   * Uncheck checkboxes by the section they appear in.
   *
   * @param {Event} e
   */
  uncheckInputs(e) {
    e.preventDefault();
    const { controls } = e.target.dataset;
    const checkboxes = this.form.querySelectorAll('input[type=checkbox]');
    const matchedCheckboxes = Array.from(checkboxes).filter(
      (checkbox) =>
        (!controls || checkbox.name === controls) && checkbox.checked,
    );

    matchedCheckboxes.forEach((checkbox) => {
      // eslint-disable-next-line no-param-reassign
      checkbox.checked = false;
    });

    if (matchedCheckboxes.length) {
      const event = new Event('change');
      this.form.dispatchEvent(event);
    }
  }

  /**
   * Clear the contents of the search input (which is event.target)
   *
   * @param {Event} e
   */

  // eslint-disable-next-line class-methods-use-this
  clearSearchFields(e) {
    e.preventDefault();
    const searchInputs = document.querySelectorAll('.js-search-input');
    Array.from(searchInputs).forEach((el) => {
      // eslint-disable-next-line no-param-reassign
      el.value = '';
    });
  }

  /** Toggles the visibility of clear buttons depending on selected filters. */
  updateClearVisibility() {
    const checkedControls = Object.keys(this.state);
    Array.from(this.clearButtons).forEach((btn) => {
      const { controls } = btn.dataset;

      if (checkedControls.includes(controls)) {
        btn.removeAttribute('hidden');
      } else if (controls) {
        btn.setAttribute('hidden', '');
      }
    });

    if (checkedControls.length) {
      Array.from(this.clearSectionEls).forEach((el) =>
        el.removeAttribute('hidden'),
      );
    } else {
      Array.from(this.clearSectionEls).forEach((el) =>
        el.setAttribute('hidden', ''),
      );
    }
  }
};
