/* eslint-disable import/no-extraneous-dependencies */
const FilterForm = require('./organisms/filter-form');
const MapEmbed = require('./atoms/map-embed');
const TabbedPanels = require('./organisms/tabbed-panels');
const Toggle = require('./atoms/toggle');

require('@mozilla-protocol/core/protocol/js/protocol-base');
require('@mozilla-protocol/core/protocol/js/protocol-utils');
require('@mozilla-protocol/core/protocol/js/protocol-supports');
require('@mozilla-protocol/core/protocol/js/protocol-menu');
require('@mozilla-protocol/core/protocol/js/protocol-navigation');
require('@mozilla-protocol/core/protocol/js/protocol-details');

require('../css/index.scss');

window.addEventListener('DOMContentLoaded', () => {
  Mzp.Navigation.init();
  Mzp.Menu.init();
  FilterForm.init();
  MapEmbed.init();
  TabbedPanels.init();
  Toggle.init();
});
