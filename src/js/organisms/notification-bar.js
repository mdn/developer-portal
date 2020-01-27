/**
 * Handles events related to the notification bar*
 *
 * @class NotificationBar
 */

module.exports = class NotificationBar {
  static init() {
    const dissmissButtons = document.querySelectorAll(
      '.mzp-c-notification-bar-button',
    );
    for (let i = 0; i < dissmissButtons.length; i += 1) {
      dissmissButtons[i].addEventListener(
        'click',
        function handler(e) {
          e.currentTarget.parentNode.remove();
        },
        false,
      );
    }
  }
};
