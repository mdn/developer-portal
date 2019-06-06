/* eslint-disable import/no-extraneous-dependencies */
import '../css/index.scss';
import '@mozilla-protocol/core/protocol/js/protocol-base';
import '@mozilla-protocol/core/protocol/js/protocol-utils';
import '@mozilla-protocol/core/protocol/js/protocol-supports';
import '@mozilla-protocol/core/protocol/js/protocol-menu';
import '@mozilla-protocol/core/protocol/js/protocol-navigation';
import '@mozilla-protocol/core/protocol/js/protocol-details';
import GetStarted from './organisms/get-started';

window.addEventListener('DOMContentLoaded', () => {
  Mzp.Navigation.init();
  Mzp.Menu.init();

  const getStarted = new GetStarted();
  getStarted.init();
});
