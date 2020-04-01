const NEWSLETTER_SUBSCRIBE_URL = 'https://www.mozilla.org/en-US/newsletter/';

/**
 * Posts serialized data from the given form to the subscription endpoint,
 * return the JSON result
 *
 * @param {object} form // whether or not the survey should be shown
 * @returns {object} // JSON
 */
function submitNewsletterSubscription(form) {
  return fetch(NEWSLETTER_SUBSCRIBE_URL, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams(new FormData(form)).toString(),
  }).then((response) => response.json());
}

/** Single place to raise an alert()
 *
 * @param {string} message
 */
function complain(message) {
  // eslint-disable-next-line no-alert
  alert(message);
}

/**
 * Encapsulates newsletter-signup behaviour, which is done as an
 * AJAX POST to the newsletter backend service
 *
 * @class NewsletterSubscription
 */
module.exports = class NewsletterSubscription {
  /**
   * Constructs an instance of NewsletterSubscription class for the
   * matching element, if present
   *
   * @returns {NewsletterSubscription}
   */
  static init() {
    const element = document.getElementById('newsletter-form');
    if (element) {
      return new this(element);
    }
    return null; // just to keep linter happy
  }

  constructor(form) {
    this.form = form;
    this.form.onsubmit = (event) => {
      event.preventDefault();
      submitNewsletterSubscription(this.form)
        .then(({ success, errors }) => {
          if (success) {
            const targetArea = this.form.getElementsByClassName(
              'js-newsletter-fields',
            )[0];
            targetArea.innerHTML = targetArea.getAttribute(
              'data-success-message',
            );
            return;
          }

          if (errors && errors.length) {
            complain(`There was a problem subscribing you: ${errors}`);
          }
        })
        .catch(() => {
          complain(`There was a problem subscribing you. Please try again.`);
          // TODO? ping monitoring with ([e.toString()]) ?
        });
    };
  }
};
