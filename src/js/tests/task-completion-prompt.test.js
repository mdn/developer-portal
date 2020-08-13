/* Light tests for the task-completion prompt.
 * (Note that coverage isn't total) */

/* Patch in objects that are placed on the DOM.window via HTML; We need this
 * to allow importing the module before we can test it
 */
Object.defineProperty(global.window, 'DevPortal', {
  writable: true,
  value: { TaskCompletionSurvey: { displayPercentage: 100 } },
});

const TaskCompletionPrompt = require('../task-completion-prompt');

const removeCookie = function removeCookie(name) {
  document.cookie = `${name}=true; expires=1 Jan 1970 00:00:00 GMT;`;
};

afterEach(() => {
  removeCookie('devportal_show_task_completion_survey');
});

const promptHTMLInHiddenState = `<aside class="mzp-c-notification-bar mzp-t-click js-task-completion-survey" hidden="">
  <button class="mzp-c-notification-bar-button mzp-js-notification-trigger" type="button"></button>
  <p>
      Your feedback is important. Would you
        <a target="_blank" rel="nofollow noopener noreferrer" href="https://example.com/task-completion-survey" class="mzp-c-notification-bar-cta">
          complete a short survey
        </a>
      after visiting?
  </p>
</aside>`;

test('running the code with no cookie sets a cookie', () => {
  expect(document.cookie).toBe('');

  TaskCompletionPrompt.init(); // this is how it's invoked in index.js

  expect(document.cookie).toBe('devportal_show_task_completion_survey=true');
});

describe('show that existing cookies are not altered', () => {
  test('running the code with the cookie set to true', () => {
    document.cookie = 'devportal_show_task_completion_survey=true';

    TaskCompletionPrompt.init();

    expect(document.cookie).toBe('devportal_show_task_completion_survey=true');
  });

  test('running the code with the cookie set to false', () => {
    document.cookie = 'devportal_show_task_completion_survey=false';

    TaskCompletionPrompt.init();

    expect(document.cookie).toBe('devportal_show_task_completion_survey=false');
  });
});

describe('testing the effect of cookies on the UI', () => {
  test('running the code with no cookie sets a cookie and reveals panel', () => {
    // set up the hidden HTML snippet, no cookie
    expect(document.cookie).toBe('');
    document.body.innerHTML = promptHTMLInHiddenState;

    const panelBefore = document.getElementsByClassName(
      'js-task-completion-survey',
    )[0];
    expect(panelBefore.hasAttribute('hidden')).toBe(true);

    TaskCompletionPrompt.init();

    // cookie should be set, and panel revealed
    expect(document.cookie).toBe('devportal_show_task_completion_survey=true');

    const panelAfter = document.getElementsByClassName(
      'js-task-completion-survey',
    )[0];
    expect(panelAfter.hasAttribute('hidden')).toBe(false);
  });

  test('running the code with cookie set to true reveals panel', () => {
    // set up the hidden HTML snippet, no cookie
    document.cookie = 'devportal_show_task_completion_survey=true';
    document.body.innerHTML = promptHTMLInHiddenState;

    expect(document.cookie).toBe('devportal_show_task_completion_survey=true');

    const panelBefore = document.getElementsByClassName(
      'js-task-completion-survey',
    )[0];
    expect(panelBefore.hasAttribute('hidden')).toBe(true);

    TaskCompletionPrompt.init();

    // cookie should still be set, and panel revealed
    expect(document.cookie).toBe('devportal_show_task_completion_survey=true');

    const panelAfter = document.getElementsByClassName(
      'js-task-completion-survey',
    )[0];
    expect(panelAfter.hasAttribute('hidden')).toBe(false);
  });

  test('running the code with cookie set to false leaves panel hidden', () => {
    // set up the hidden HTML snippet, no cookie
    document.cookie = 'devportal_show_task_completion_survey=false';
    document.body.innerHTML = promptHTMLInHiddenState;

    expect(document.cookie).toBe('devportal_show_task_completion_survey=false');

    const panelBefore = document.getElementsByClassName(
      'js-task-completion-survey',
    )[0];
    expect(panelBefore.hasAttribute('hidden')).toBe(true);

    TaskCompletionPrompt.init();

    // cookie should still be set to false, and panel remains hidden
    expect(document.cookie).toBe('devportal_show_task_completion_survey=false');

    const panelAfter = document.getElementsByClassName(
      'js-task-completion-survey',
    )[0];
    expect(panelAfter.hasAttribute('hidden')).toBe(true);
  });
});

test('clicking the close trigger on the notification sets the cookie to false', () => {
  // set up the hidden HTML snippet, no cookie
  document.body.innerHTML = promptHTMLInHiddenState;

  TaskCompletionPrompt.init();

  expect(document.cookie).toBe('devportal_show_task_completion_survey=true');
  const panelAfter = document.getElementsByClassName(
    'js-task-completion-survey',
  )[0];
  expect(panelAfter.hasAttribute('hidden')).toBe(false);

  const closeTrigger = document.getElementsByClassName(
    'mzp-js-notification-trigger',
  )[0];
  closeTrigger.click();

  expect(document.cookie).toBe('devportal_show_task_completion_survey=false');
});
