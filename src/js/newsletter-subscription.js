const NEWSLETTER_SUBSCRIBE_URL = 'https://www.mozilla.org/en-US/newsletter/';

function submitNewsletterSubscription(form) {
  return fetch(NEWSLETTER_SUBSCRIBE_URL, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams(new FormData(form)).toString(),
  }).then(response => response.json());
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
    // eslint-disable-next-line no-console
    console.log(this.form);
    this.form.onsubmit = event => {
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
            // eslint-disable-next-line no-alert
            alert(`There was a problem subscribing you: ${errors}`);
          }
        })
        .catch(() => {
          // eslint-disable-next-line no-alert
          alert(`There was a problem subscribing you. Please try again.`);
          // TODO? ping monitoring with ([e.toString()]) ?
        });

      return fetch(NEWSLETTER_SUBSCRIBE_URL, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(new FormData(this.form)).toString(),
      }).then(response => response.json());
    };
  }
};
