/* Light test for the newsletter-subscription code. */

/** The following adds the 'fetchMock' global variable and rewires 'fetch'
 * global to call 'fetchMock' instead of the real implementation
 */

/* global fetchMock */

// eslint-disable-next-line import/no-unresolved
require('jest-fetch-mock').enableMocks();

Object.defineProperty(global.window, 'alert', function fakeAlert(val) {
  // eslint-disable-next-line no-console
  console.log(val);
});

const NewsletterSubscription = require('../newsletter-subscription');

const exampleFormHTML = `
<form id="newsletter-form" class="mzp-c-newsletter-form" name="newsletter-form">
  <div class="js-newsletter-fields" data-success-message="<b>Thank you. Please check your email to confirm your subscription.</b>">
    <input type="hidden" name="newsletters" value="app-dev">
    <input type="hidden" name="fmt" value="H">
    <p>
      <label for="newsletter-email">Your email address</label>
      <input type="email" name="email" class="newsletter-email" id="newsletter-email" placeholder="you@example.com" required aria-required="true">
    </p>
    <p>
      <label for="newsletter-privacy" class="mzp-u-inline">
        <input type="checkbox" name="privacy" id="newsletter-privacy" required aria-required="true">
        I'm okay with Mozilla handling my info as explained in this <a class="privacy-link" href="https://www.mozilla.org/privacy/websites/" target="_blank" rel="noopener noreferrer">Privacy Notice</a>.
      </label>
    </p>
    <p>
      <button type="submit" class="mzp-c-button mzp-t-small">Sign up now</button>
    </p>
  </div>
</form>`;

/**
 * Helper to boostrap form with test data
 *
 *  @param {document} document
 *  @param {object} data
 */
function populateFormData(document, data) {
  const emailField = document.getElementsByName('email')[0];
  const privacyField = document.getElementsByName('privacy')[0];
  emailField.value = data.email;
  privacyField.value = data.privacy;
}

beforeEach(() => {
  fetch.resetMocks();
});

test('Happy path', async () => {
  fetchMock.mockResponseOnce(JSON.stringify({ success: true }));
  document.body.innerHTML = exampleFormHTML;
  NewsletterSubscription.init(); // this is how it's invoked in index.js
  const form = document.getElementById('newsletter-form');

  populateFormData(document, {
    email: 'test@example.com',
    privacy: 'checked',
  });
  form.submit();

  expect(fetch.mock.calls.length).toEqual(1);

  expect(fetch.mock.calls[0][1].headers).toEqual({
    'X-Requested-With': 'XMLHttpRequest',
    'Content-type': 'application/x-www-form-urlencoded',
  });
  expect(fetch.mock.calls[0][1].method).toEqual('POST');
  expect(fetch.mock.calls[0][1].body).toEqual(
    'newsletters=app-dev&fmt=H&email=test%40example.com',
  );
  expect(fetch.mock.calls[0][0]).toEqual(
    'https://www.mozilla.org/en-US/newsletter/',
  );

  // Show the content in js-newsletter-fields has been updated after a successful POST,
  // but to do that we need to pause a moment
  await new Promise((resolve) => setTimeout(resolve));

  const newsletterFieldsDivContent = form.getElementsByClassName(
    'js-newsletter-fields',
  )[0].innerHTML;
  expect(newsletterFieldsDivContent).toBe(
    '<b>Thank you. Please check your email to confirm your subscription.</b>',
  );
});
