const { parseForm, parseQueryParams } = require('../utils');

/**
 * Represents a directory page filter form; reacts to user input and triggers
 * new server-side submiting of results
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
    return Array.from(elements).map(element => new this(element));
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
    this.clearButtons = document.querySelectorAll('.js-filter-clear');
    this.clearSectionEls = document.querySelectorAll(
      '.js-filter-form-clear-section',
    );

    this.updateCheckboxes();
    this.setupEvents();
    // this.submit();
  }

  /** Sets up event listeners. */
  setupEvents() {
    Array.from(this.clearButtons).forEach(btn => {
      btn.addEventListener('click', e => this.uncheckInputs(e));
    });

    // this.nextPageButton.addEventListener('click', e => this.nextPage(e));
    this.form.addEventListener('change', () => this.onFormInput());
  }

  /** Updates state and requests new results from the server when an input is updated. */
  onFormInput() {
    this.state = parseForm(this.form);
    this.submit();
  }

  /**
   * Ensures the DOM reflects the current state. Used after query parameter
   * loading.
   */
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
      checkbox => (!controls || checkbox.name === controls) && checkbox.checked,
    );

    matchedCheckboxes.forEach(checkbox => {
      // eslint-disable-next-line no-param-reassign
      checkbox.checked = false;
    });

    if (matchedCheckboxes.length) {
      const event = new Event('change');
      this.form.dispatchEvent(event);
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

  /**
   * Shows the next page of items.
   *
   * @param {Event} e
   */
  nextPage(e) {
    e.preventDefault();
    if (this.matches.length >= this.resourcesOnPage) {
      this.resourcesOnPage += this.resourcesPerPage;
      this.submit();
    }
  }

  // /** Filters the items by applying the selected filters. */
  // filter() {
  //   this.matches = [];

  //   if (!Object.keys(this.state).length) {
  //     this.matches = Array.from(this.targetEls);
  //     return;
  //   }

  //   Array.from(this.targetEls).forEach(el => {
  //     const results = Object.entries(this.state).map(([key, values]) => {
  //       const dataValues = el.dataset[key] ? el.dataset[key].split(' ') : [];
  //       return values.some(value => dataValues.includes(value));
  //     });

  //     if (results.every(Boolean)) {
  //       this.matches.push(el);
  //     }
  //   });
  // }

  /** Submits a HTTP request to get an updated list of items based on the
   * current state of the filters */
  submit() {
    // this.filter();
    this.updateClearVisibility();
    // if (this.matches.length <= this.resourcesOnPage) {
    //   this.actionsEl.setAttribute('hidden', '');
    // } else {
    //   this.actionsEl.removeAttribute('hidden');
    // }

    // update the URL params
    this.updateUrlParams();
    // reload the page, based on the params just set
    window.location.reload();
  }
};
