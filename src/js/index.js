/* eslint-disable import/no-extraneous-dependencies */

require('./polyfills');

/**
 * Custom-to-project JS
 */

const FilterForm = require('./organisms/filter-form');
const MapEmbed = require('./atoms/map-embed');
const Modal = require('./atoms/modal');
const TabbedPanels = require('./organisms/tabbed-panels');
const Toggle = require('./atoms/toggle');
const NotificationBar = require('./organisms/notification-bar');

/**
 * JS from Mozilla's Protocol design system
 */
require('@mozilla-protocol/core/protocol/js/protocol-base');
require('@mozilla-protocol/core/protocol/js/protocol-utils');
require('@mozilla-protocol/core/protocol/js/protocol-supports');
require('@mozilla-protocol/core/protocol/js/protocol-menu');
require('@mozilla-protocol/core/protocol/js/protocol-modal');
require('@mozilla-protocol/core/protocol/js/protocol-navigation');
require('@mozilla-protocol/core/protocol/js/protocol-details');
require('@mozilla-protocol/core/protocol/js/protocol-notification-bar');

/**
 * Pull in the CSS
 */
require('../css/index.scss');

/**
 * Initialize components on DOM load.
 */
window.addEventListener('DOMContentLoaded', () => {
  Mzp.Navigation.init();
  Mzp.Menu.init();
  FilterForm.init();
  MapEmbed.init();
  Modal.init();
  TabbedPanels.init();
  Toggle.init();
  NotificationBar.init();
});
