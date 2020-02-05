const { getCookieValue, setCookieValue } = require('./utils');

const SURVEY_COOKIE_NAME = 'devportal_show_task_completion_survey';
const SURVEY_COOKIE_EXPIRY = 60 * 60 * 24 * 7 * 6; // six weeks in seconds
const USE_SECURE_COOKIE = window.location.protocol === 'https:';
const percentageOfShowing =
  window.DevPortal.TaskCompletionSurvey.displayPercentage;

/**
 * Builds and sets an appropriate cookie concerned with whether or not the survey
 * should be shown.
 *
 * @param {boolean} value // whether or not the survey should be shown
 */

const setSurveyCookie = function setSurveyCookie(value) {
  let cookieVal = `${value};path=/;max-age=${SURVEY_COOKIE_EXPIRY}`;
  if (USE_SECURE_COOKIE) {
    cookieVal = `${cookieVal};secure=true;`;
  }
  setCookieValue(SURVEY_COOKIE_NAME, cookieVal);
};

/**
 * Handler method to ensure the survey-triggering cookie gets set to False,
 * which means the survey won't be shown again. Deleting the cookie would mean
 * the user has chance of being asked again, but setting it to False means they
 * won't until the cookie expires – which we original set to being six weeks' time'.
 */
const setSurveyCookieToFalse = function setSurveyCookieToFalse() {
  setSurveyCookie(false);
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
 * Determines whether or not to show the survey.
 * It will look for a cookie and check its value, and if there is no cookie it will
 * psuedorandomly decide (based on a configured percentage) whether to show the prompt
 * (and set a cookie to remember this decision).
 *
 * @returns {boolean}  // cookie value
 */
const showSurvey = function showSurvey() {
  let showSurveyVal = false;
  const surveyCookieVal = getCookieValue(SURVEY_COOKIE_NAME); // a string
  /* surveyCookieVal is ternary and can mean 'Show survey'
   * or 'Do not show it' or 'Unknown' */
  switch (surveyCookieVal) {
    case 'false':
      showSurveyVal = false;
      break;
    case 'true':
      showSurveyVal = true;
      break;
    default:
      // no cookie was set, so let's 'roll the dice'
      showSurveyVal = Math.random() >= 1 - percentageOfShowing / 100;
      setSurveyCookie(showSurveyVal);
  }
  return showSurveyVal;
};

/**
 * Reveals the task-completion survey prompt, as required
 *
 * @class TaskCompletionPrompt
 */

module.exports = class TaskCompletionPrompt {
  static init() {
    if (showSurvey()) {
      const elements = document.getElementsByClassName(
        'js-task-completion-survey',
      );
      // There should be 0 or 1 to reveal, but let's not assume
      Array.from(elements).map(target => setupListeners(target));
      Array.from(elements).map(target => target.removeAttribute('hidden'));
    }
  }
};
