/**
 * Updates the key_creatives column in the Shows sheet based on show_team data
 */
function updateKeyCreatives() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const showTeamSheet = ss.getSheetByName('show_team');
  const showsSheet = ss.getSheetByName('shows');
  
  // Get all data from both sheets
  const showTeamData = showTeamSheet.getDataRange().getValues();
  const showsData = showsSheet.getDataRange().getValues();
  
  // Find column indices
  const showTeamHeaders = showTeamData[0];
  const showsHeaders = showsData[0];
  
  // Get column indices for show_team sheet
  const showNameColTeam = 0;  // First column
  const nameColTeam = 1;      // Second column
  const rolesColTeam = 2;     // Third column
  const orderColTeam = 3;     // Fourth column
  const notesColTeam = 4;     // Fifth column
  
  // Get column indices for shows sheet
  const showNameColShows = showsHeaders.indexOf('show_name');
  const keyCreativesCol = showsHeaders.indexOf('key_creatives');
  
  if (keyCreativesCol === -1) {
    throw new Error('Could not find key_creatives column in shows sheet');
  }
  
  // Create a map of show names to their team members
  const showTeamMap = new Map();
  
  // Skip header row
  for (let i = 1; i < showTeamData.length; i++) {
    const row = showTeamData[i];
    const showName = row[showNameColTeam];
    const name = row[nameColTeam];
    const roles = row[rolesColTeam]; // Roles are already in the correct format
    const order = row[orderColTeam];
    
    if (!showTeamMap.has(showName)) {
      showTeamMap.set(showName, []);
    }
    showTeamMap.get(showName).push({
      name: name,
      roles: roles,
      order: order
    });
  }
  
  // Update shows sheet
  const updatedShowsData = showsData.map((row, index) => {
    if (index === 0) return row; // Skip header row
    
    const showName = row[showNameColShows];
    const teamMembers = showTeamMap.get(showName) || [];
    
    // Sort team members by order if available
    teamMembers.sort((a, b) => {
      if (a.order && b.order) return a.order - b.order;
      if (a.order) return -1;
      if (b.order) return 1;
      return 0;
    });
    
    // Format key creatives string - roles are already in the correct format
    const keyCreatives = teamMembers
      .map(member => {
        // Only add parentheses if there are roles
        return member.roles ? `${member.name} (${member.roles})` : member.name;
      })
      .join(', ');
    
    row[keyCreativesCol] = keyCreatives;
    return row;
  });
  
  // Update the shows sheet with new data
  showsSheet.getRange(1, 1, updatedShowsData.length, updatedShowsData[0].length)
    .setValues(updatedShowsData);
}

// This function will be called from Code.gs's onOpen()
function addKeyCreativesMenuItem(menu) {
  return menu.addSeparator()
    .addItem('Update Key Creatives', 'updateKeyCreatives');
}
