import '../css/index.scss';
import headerInit from './molecules/header';
import '@mozilla-protocol/core/protocol/js/protocol-base';
import '@mozilla-protocol/core/protocol/js/protocol-utils';
import '@mozilla-protocol/core/protocol/js/protocol-supports';
import '@mozilla-protocol/core/protocol/js/protocol-navigation';

window.addEventListener('DOMContentLoaded', () => {
  headerInit();
});
