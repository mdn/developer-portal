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
    this.clearAllButtons = document.querySelectorAll(
      '.js-filter-form-clear-section',
    );

    this.updateFormControls();
    this.setupEvents();
    this.updateClearVisibility();
  }

  /** Sets up event listeners. */
  setupEvents() {
    Array.from(this.clearButtons).forEach((btn) => {
      btn.addEventListener('click', (e) => this.clearInputs(e));
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
    const searchFields = document.querySelectorAll('.js-search-input');
    Array.from(searchFields).forEach((field) => {
      if (!field.value) {
        field.setAttribute('disabled', ''); // disabled fields are not submitted to the server
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
  clearInputs(e) {
    e.preventDefault();
    const { controls } = e.target.dataset;
    const formInputs = this.form.querySelectorAll(
      'input[type=checkbox], input[name="search"]',
    );
    const matchedFormInputs = Array.from(formInputs).filter((input) => {
      return (
        // if there is a control group specced, is it the one we want to target?
        (!controls || input.name === controls) &&
        // and is the input called search or is it a checked checkbox?
        (input.name === 'search' || input.checked)
      );
    });

    matchedFormInputs.forEach((input) => {
      if (input.name === 'search') {
        // eslint-disable-next-line no-param-reassign
        input.value = '';
      } else {
        // eslint-disable-next-line no-param-reassign
        input.checked = false;
      }
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
      Array.from(this.clearAllButtons).forEach((el) =>
        el.removeAttribute('hidden'),
      );
    } else {
      Array.from(this.clearAllButtons).forEach((el) =>
        el.setAttribute('hidden', ''),
      );
    }
  }
};
