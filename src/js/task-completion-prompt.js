/* eslint-disable prefer-template */
const { getCookieValue, setCookieValue } = require('./utils');

const SURVEY_COOKIE_NAME = 'dwf_show_task_completion_survey';
const SURVEY_COOKIE_NEW_EXPIRY = 60 * 60 * 24 * 7 * 6; // six weeks in seconds
const USE_SECURE_COOKIE = window.location.protocol === 'https:';

/**
 * Helper function to display the task-completion survey prompt.
 * For now, it's revealing a pre-rendered, hidden, div in the template.
 * In the future (once https://github.com/mozilla/protocol/pull/460 is
 * resolved) we'll switch to an entirely client-side-rendered solution.
 */

const displaySurvey = function displaySurvey() {
  // reveal the survey prompt, if appropriate
  const showSurvey = getCookieValue(SURVEY_COOKIE_NAME);
  // eslint-disable-next-line no-unused-expressions
  if (showSurvey === 'True') {
    const elements = document.getElementsByClassName(
      'js-task-completion-survey',
    );
    // There should be 0 or 1 to reveal, but let's not assume
    Array.from(elements).map(target => target.removeAttribute('hidden'));
  }
};

/**
 * Handler function to ensure the survey-triggering cookie gets set to False,
 * which means the survey won't be shown again. Deleting the cookie means the
 * user has chance of being asked again, but setting it to False means they
 * won't until the cookie expires – which we set to being six weeks from here.
 */

const setSurveyCookieToFalse = function surveyCookieToFalse() {
  let cookieString = `False;max-age=${SURVEY_COOKIE_NEW_EXPIRY}`;

  if (USE_SECURE_COOKIE) {
    cookieString = `${cookieString};secure=true;`;
  }

  setCookieValue(SURVEY_COOKIE_NAME, cookieString);
};

/**
 * Bind a handler to the given target (a link or button) that triggers
 * code to set the survey cookie to False upon click.
 *
 * @param {Element} target
 */
const bindCookieUpdate = function bindCookieUpdate(target) {
  target.addEventListener('click', setSurveyCookieToFalse);
};

/**
 * Bind handlers to the 'trigger points' in the given notification panel so that
 * the cookie update is done when they are clicked
 *
 * @param {Element} notificationPanel
 */

const setupListeners = function setupListeners(notificationPanel) {
  // eslint-disable-next-line no-debugger
  const closeTriggers = notificationPanel.querySelectorAll(
    '.mzp-js-notification-trigger',
  );

  // There should be 0 or 1 of each, but let's not assume
  Array.from(closeTriggers).map(closeTrigger => bindCookieUpdate(closeTrigger));

  // DISABLED FOR NOW: also set the cookie to False after visiting the survey link
  // const surveyLinks = notificationPanel.querySelectorAll('.js-survey-link');
  // Array.from(surveyLinks).map(surveyLink => bindCookieUpdate(surveyLink));
};

/**
 * Reveals the task-completion survey prompt, as required, and configures
 * event handling
 *
 * @class TaskCompletionPrompt
 */
module.exports = class TaskCompletionPrompt {
  static init() {
    const elements = document.querySelectorAll('.js-task-completion-survey');
    return Array.from(elements).map(element => new this(element));
  }

  constructor(notificationPanel) {
    displaySurvey();
    setupListeners(notificationPanel);
  }
};
