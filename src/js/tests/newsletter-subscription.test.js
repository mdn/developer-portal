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

test('Happy path, for all but IE11', async () => {
  /* Set up a spy on something we know will NOT be called unless the IE11 the
   * fallback is running. This is a bit of a hack, but we can't spy on
   * URLSearchParams without it blowing up with: `TypeError: Class constructor
   * URLSearchParams cannot be invoked without 'new'`
   */
  const spy = jest.spyOn(global, 'encodeURIComponent');

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
  expect(fetch.mock.calls).toEqual([
    [
      'https://www.mozilla.org/en-US/newsletter/',
      {
        body: 'newsletters=app-dev&fmt=H&email=test%40example.com',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded',
          'X-Requested-With': 'XMLHttpRequest',
        },
        method: 'POST',
      },
    ],
  ]);

  // Show the content in js-newsletter-fields has been updated after a successful POST,
  // but to do that we need to pause a moment
  await new Promise((resolve) => setTimeout(resolve));

  const newsletterFieldsDivContent = form.getElementsByClassName(
    'js-newsletter-fields',
  )[0].innerHTML;
  expect(newsletterFieldsDivContent).toBe(
    '<b>Thank you. Please check your email to confirm your subscription.</b>',
  );

  expect(spy).not.toHaveBeenCalled();
});

/* Testing that the overall behaviour still works with IE11, which has
 * no URLSearchParams or complete FormData implementation
 */
test('IE11 fallback behaviour', async () => {
  // Store original implementation
  const originalURLSearchParams = URLSearchParams;

  // eslint-disable-next-line no-global-assign
  URLSearchParams = undefined;

  /* Set up a spy on something we know will be called if the fallback is running.
   * (True, this is a bit of a hack, but we can't spy on our now-undefined
   * URLSearchParams, because it's not a function)
   * */
  const spy = jest.spyOn(global, 'encodeURIComponent');

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
  expect(fetch.mock.calls).toEqual([
    [
      'https://www.mozilla.org/en-US/newsletter/',
      {
        body:
          /* The manual fallback also sends confirmation that the privacy checkbox was ticked,
           * because it assembles a payload from all fields
           */
          'newsletters=app-dev&fmt=H&email=test%40example.com&privacy=checked',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded',
          'X-Requested-With': 'XMLHttpRequest',
        },
        method: 'POST',
      },
    ],
  ]);

  // Show the content in js-newsletter-fields has been updated after a successful POST,
  // but to do that we need to pause a moment
  await new Promise((resolve) => setTimeout(resolve));

  const newsletterFieldsDivContent = form.getElementsByClassName(
    'js-newsletter-fields',
  )[0].innerHTML;
  expect(newsletterFieldsDivContent).toBe(
    '<b>Thank you. Please check your email to confirm your subscription.</b>',
  );

  // Confirm code that only gets run when URLSearchParams is not available is called
  expect(spy).toHaveBeenNthCalledWith(1, 'app-dev');
  expect(spy).toHaveBeenNthCalledWith(2, 'H');
  expect(spy).toHaveBeenNthCalledWith(3, 'test@example.com');
  expect(spy).toHaveBeenNthCalledWith(4, 'checked');

  // Restore original implementation
  // eslint-disable-next-line no-global-assign
  URLSearchParams = originalURLSearchParams;
});
