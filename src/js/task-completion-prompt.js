/* eslint-disable prefer-template */
const { getCookie } = require('./utils');

/**
 * Reveals the task-completion survey prompt, as required
 *
 * @class TaskCompletionPrompt
 */

module.exports = class TaskCompletionPrompt {
  static init() {
    const showSurvey = getCookie('dwf_show_task_completion_survey');

    if (showSurvey === 'True') {
      const target = document.getElementsByClassName(
        'js-task-completion-survey',
      );

      // There should be 0 or 1 to reveal, but let's not assume
      if (target) {
        for (let i = 0; i < target.length; i += 1) {
          target[i].removeAttribute('hidden');
        }
      }
    }
  }
};
