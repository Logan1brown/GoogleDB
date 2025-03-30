// Constants and configuration shared across features
const DB_CONFIG = {
  sheetName: 'shows',
  showTeamSheet: 'show_team',
  roleTypeSheet: 'role_types',
  networkSheet: 'network_list',
  studioSheet: 'studio_list',
  genreSheet: 'genre_list',
  subgenreSheet: 'subgenre_list',
  sourceTypeSheet: 'source_types',
  statusSheet: 'status_types',
  orderTypeSheet: 'order_types',
  fields: [
    { name: 'showName', label: 'Show Name' },
    { name: 'keyCreatives', label: 'Key Creatives' },
    { name: 'network', label: 'Network' },
    { name: 'studios', label: 'Studio' },
    { name: 'announcementDate', label: 'Announcement Date' },
    { name: 'genre', label: 'Genre' },
    { name: 'subgenre', label: 'Subgenre' },
    { name: 'episodeCount', label: 'Episode Count' },
    { name: 'sourceType', label: 'Source Material' },
    { name: 'status', label: 'Status' },
    { name: 'orderType', label: 'Order Type' },
    { name: 'notes', label: 'Notes' }
  ]
};

// Create menu when spreadsheet opens
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  const menu = ui.createMenu('Show Database');
  
  // Register features
  AddShowFeature.registerMenuItems(menu);
  SearchEditFeature.registerMenuItems(menu);
  MigrateRoles.registerMenuItems(menu);
  SyncShowNames.registerMenuItems(menu);
  
  menu.addToUi();
}
