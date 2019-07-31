/* eslint-disable import/no-extraneous-dependencies */
import '../css/index.scss';
import '@mozilla-protocol/core/protocol/js/protocol-base';
import '@mozilla-protocol/core/protocol/js/protocol-utils';
import '@mozilla-protocol/core/protocol/js/protocol-supports';
import '@mozilla-protocol/core/protocol/js/protocol-menu';
import '@mozilla-protocol/core/protocol/js/protocol-navigation';
import '@mozilla-protocol/core/protocol/js/protocol-details';
import FilterForm from './organisms/filter-form';
import TabbedPanels from './organisms/tabbed-panels';
import MapEmbed from './atoms/map';

window.addEventListener('DOMContentLoaded', () => {
  Mzp.Navigation.init();
  Mzp.Menu.init();

  FilterForm.init();
  TabbedPanels.init();
  MapEmbed.init();
});
