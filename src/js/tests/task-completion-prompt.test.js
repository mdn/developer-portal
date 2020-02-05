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

test('running the code with no cookie sets a cookie', () => {
  expect(global.document.cookie).toBe('');

  TaskCompletionPrompt.init(); // this is how it's invoked in index.js

  expect(global.document.cookie).toBe(
    'devportal_show_task_completion_survey=true',
  );
});

describe('show that existing cookies are not altered', () => {
  test('running the code with the cookie set to true', () => {
    global.document.cookie = 'devportal_show_task_completion_survey=true';

    TaskCompletionPrompt.init();

    expect(global.document.cookie).toBe(
      'devportal_show_task_completion_survey=true',
    );
  });

  test('running the code with the cookie set to false', () => {
    global.document.cookie = 'devportal_show_task_completion_survey=false';

    TaskCompletionPrompt.init();

    expect(global.document.cookie).toBe(
      'devportal_show_task_completion_survey=false',
    );
  });
});
