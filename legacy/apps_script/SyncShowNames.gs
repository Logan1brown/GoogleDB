// Find outdated show names in show_team
const SyncShowNames = {
  registerMenuItems: function(menu) {
    menu.addItem('Find Outdated Show Names', 'SyncShowNames.findOutdated');
  },

  findOutdated: function() {
    const ui = SpreadsheetApp.getUi();
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // Get both sheets
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    
    if (!showsSheet || !teamSheet) {
      ui.alert('Error', 'Could not find required sheets', ui.ButtonSet.OK);
      return;
    }

    // Get all show names from both sheets
    const showsData = showsSheet.getRange('A2:A' + showsSheet.getLastRow()).getValues();
    const teamData = teamSheet.getRange('A2:A' + teamSheet.getLastRow()).getValues();
    
    // Create set of valid show names from shows sheet
    const validShows = new Set(showsData.map(row => row[0]).filter(name => name));
    
    // Find rows in show_team that have outdated names
    const outdatedRows = [];
    teamData.forEach((row, index) => {
      const showName = row[0];
      if (showName && !validShows.has(showName)) {
        outdatedRows.push({
          row: index + 2, // +2 because we started at A2
          name: showName
        });
      }
    });

    if (outdatedRows.length === 0) {
      ui.alert('Shows are in Sync', 'All show names in show_team are up to date.', ui.ButtonSet.OK);
      return;
    }

    // Report outdated show names
    const message = `Found ${outdatedRows.length} outdated show names in show_team:\n\n` +
      outdatedRows.map(item => `${item.name} (Row ${item.row})`).join('\n') +
      '\n\nWould you like to highlight these rows for updating?';

    const response = ui.alert('Show Names Need Update', message, ui.ButtonSet.YES_NO);
    
    if (response === ui.Button.YES) {
      // Clear existing highlights
      teamSheet.getRange('A2:A' + teamSheet.getLastRow()).setBackground(null);
      
      // Highlight outdated rows
      outdatedRows.forEach(item => {
        teamSheet.getRange('A' + item.row).setBackground('#f4cccc'); // Light red
      });
      
      // Switch to show_team and select first outdated row
      ss.setActiveSheet(teamSheet);
      teamSheet.setActiveRange(teamSheet.getRange('A' + outdatedRows[0].row));
    }
  }
};
