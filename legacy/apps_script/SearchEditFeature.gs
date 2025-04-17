const SearchEditFeature = {
  // Menu registration
  registerMenuItems: function(menu) {
    menu.addItem('Search Shows', 'showSearchSidebar')
      .addItem('Edit Team Members', 'showTeamEditSidebar');
  },

  // Show the search sidebar
  showSearchSidebar: function() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getActiveSheet();
    
    if (sheet.getName() !== DB_CONFIG.sheetName) {
      SpreadsheetApp.getUi().alert(
        'Wrong Sheet',
        `Please switch to the "${DB_CONFIG.sheetName}" sheet to use this feature.`,
        SpreadsheetApp.getUi().ButtonSet.OK
      );
      return;
    }
    
    const html = HtmlService.createTemplateFromFile('SearchSidebar')
      .evaluate()
      .setTitle('Search Shows');
    SpreadsheetApp.getUi().showSidebar(html);
  },

  // Search shows using DB_CONFIG fields
  searchShows: function(query) {
    try {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
      const data = sheet.getDataRange().getValues();
      const headers = data[0];

      // Get column indices for snake_case sheet headers
      const columnIndices = {
        showName: headers.indexOf('shows'),
        network: headers.indexOf('network'),
        studios: headers.indexOf('studios'),
        genre: headers.indexOf('genre'),
        status: headers.indexOf('status')
      };
      
      // Log column indices for debugging
      Logger.log('Column indices:', columnIndices);

      // Search through data
      const results = [];
      const queryLower = query.toLowerCase();

      for (let i = 1; i < data.length; i++) {
        const row = data[i];
        const searchableValues = Object.values(columnIndices).map(colIndex => 
          colIndex !== -1 ? (row[colIndex] || '').toString().toLowerCase() : ''
        );

        if (searchableValues.some(value => value.includes(queryLower))) {
          const result = {};
          // Map snake_case sheet values to camelCase for UI
          Object.entries(columnIndices).forEach(([fieldName, colIndex]) => {
            result[fieldName] = colIndex !== -1 ? row[colIndex] : '';
          });
          result.rowIndex = i + 1;
          results.push(result);
        }
      }

      return results;

    } catch (error) {
      Logger.log('Error searching shows:', error);
      throw error;
    }
  },

  // Focus on the row to edit
  showEditForm: function(rowIndex) {
    try {
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
      
      if (!sheet) {
        throw new Error('Shows sheet not found');
      }

      // Select and activate the target row
      const targetRange = sheet.getRange(rowIndex, 1, 1, sheet.getLastColumn());
      sheet.activate();
      targetRange.activate();
      
      // Show a subtle toast message
      SpreadsheetApp.getActive().toast('Row selected', '', 1);
    } catch (error) {
      Logger.log('Error focusing on row:', error);
    }
  }
};

// Global functions to be called from the menu and HTML
function showSearchSidebar() {
  return SearchEditFeature.showSearchSidebar();
}



// Get role types for dropdown
function getRoleTypes() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const roleSheet = ss.getSheetByName(DB_CONFIG.roleTypeSheet);
  
  if (!roleSheet) {
    throw new Error('Role types sheet not found');
  }
  
  const roles = roleSheet.getRange(2, 1, roleSheet.getLastRow() - 1, 1)
    .getValues()
    .map(row => row[0])
    .filter(role => role);
  
  // Sort roles alphabetically
  roles.sort();
  
  return roles;
}

function searchShows(query) {
  return SearchEditFeature.searchShows(query);
}

function showEditForm(rowIndex) {
  return SearchEditFeature.showEditForm(rowIndex);
}

// Show the team edit sidebar
function showTeamEditSidebar() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  
  if (sheet.getName() !== DB_CONFIG.sheetName) {
    SpreadsheetApp.getUi().alert(
      'Wrong Sheet',
      `Please switch to the "${DB_CONFIG.sheetName}" sheet to use this feature.`,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    return;
  }
  
  const html = HtmlService.createTemplateFromFile('TeamEditSidebar')
    .evaluate()
    .setTitle('Edit Team Members')
    .setWidth(300);
  SpreadsheetApp.getUi().showSidebar(html);
}

// Get data for the currently selected show
function getCurrentShowData() {
  const sheet = SpreadsheetApp.getActiveSheet();
  if (sheet.getName() !== DB_CONFIG.sheetName) return null;
  
  const range = sheet.getActiveRange();
  if (!range) return null;
  
  const row = range.getRow();
  if (row < 2) return null; // Skip header row
  
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const showNameCol = headers.indexOf('shows');
  if (showNameCol === -1) {
    throw new Error('Show Name column not found in shows sheet. Headers: ' + headers.join(', '));
  }
  
  const showName = sheet.getRange(row, showNameCol + 1).getValue();
  if (!showName) {
    throw new Error('No show name found in selected row');
  }
  
  return { showName: showName };
}

// Get team members for a show
function getTeamMembers(showName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  const roleSheet = ss.getSheetByName(DB_CONFIG.roleTypeSheet);
  
  if (!teamSheet || !roleSheet) {
    throw new Error('Required sheets not found');
  }
  
  // Get available roles
  const roles = roleSheet.getRange(2, 1, roleSheet.getLastRow() - 1, 1)
    .getValues()
    .map(row => row[0])
    .filter(role => role);
    
  // Sort roles alphabetically
  roles.sort();
  
  // Get team members for this show
  const teamData = teamSheet.getDataRange().getValues();
  const headers = teamData[0];
  
  const showNameCol = headers.indexOf('show_name');
  const nameCol = headers.indexOf('name');
  const roleCol = headers.indexOf('roles');
  
  if (showNameCol === -1 || nameCol === -1 || roleCol === -1) {
    throw new Error('Required columns not found in show_team sheet. Need: show_name, name, roles. Found: ' + headers.join(', '));
  }
  
  // Get team members with their comma-separated roles
  const teamMembers = [];
  const memberMap = new Map();
  
  for (let i = 1; i < teamData.length; i++) {
    const row = teamData[i];
    if (row[showNameCol] !== showName) continue;
    
    const name = row[nameCol];
    const rolesStr = row[roleCol];
    
    if (!name) continue;
    
    // Split roles by comma and trim whitespace
    const roles = rolesStr ? rolesStr.split(',').map(r => r.trim()).filter(r => r) : [];
    
    if (!memberMap.has(name)) {
      const member = { name: name, roles: roles };
      teamMembers.push(member);
      memberMap.set(name, member);
    }
  }
  
  return { teamMembers: teamMembers, roles: roles };
}

// Add a new team member
function addTeamMember(name, role) {
  Logger.log('addTeamMember called with:', { name, role });
  
  const showData = getCurrentShowData();
  Logger.log('Current show data:', showData);
  if (!showData) throw new Error('No show selected');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  Logger.log('Got team sheet:', teamSheet ? 'found' : 'not found');
  if (!teamSheet) throw new Error('Team sheet not found');
  
  Logger.log('Adding team member:', {
    show: showData.showName,
    name: name,
    role: role
  });

  // Add new row with show name, member name, and role
  teamSheet.appendRow([showData.showName, name, role]);
  
  Logger.log('Calling updateKeyCreatives for show:', showData.showName);
  // Update key_creatives in shows sheet
  try {
    AddShowFeature.updateKeyCreatives(showData.showName);
    Logger.log('Successfully updated key_creatives');
  } catch (error) {
    Logger.log('Error updating key_creatives:', error);
    throw error;
  }
  
  return getTeamMembers(showData.showName);
}

// Update a team member
function updateTeamMember(index, field, value) {
  const showData = getCurrentShowData();
  if (!showData) throw new Error('No show selected');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  if (!teamSheet) throw new Error('Team sheet not found');
  
  const teamData = teamSheet.getDataRange().getValues();
  const headers = teamData[0];
  const showNameCol = headers.indexOf('show_name');
  const nameCol = headers.indexOf('name');
  
  if (showNameCol === -1 || nameCol === -1) {
    throw new Error('Required columns not found');
  }
  
  // Find all rows for this member and update them
  let found = false;
  for (let i = 1; i < teamData.length; i++) {
    if (teamData[i][showNameCol] === showData.showName && 
        teamData[i][nameCol] === value) {
      teamSheet.getRange(i + 1, nameCol + 1).setValue(value);
      found = true;
    }
  }
  
  if (!found) throw new Error('Team member not found');
  
  return getTeamMembers(showData.showName);
}

// Add a role to a team member
function addTeamMemberRole(memberIndex, role) {
  const showData = getCurrentShowData();
  if (!showData) throw new Error('No show selected');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  if (!teamSheet) throw new Error('Team sheet not found');
  
  const teamData = teamSheet.getDataRange().getValues();
  const headers = teamData[0];
  const showNameCol = headers.indexOf('show_name');
  const nameCol = headers.indexOf('name');
  const roleCol = headers.indexOf('roles');
  
  if (showNameCol === -1 || nameCol === -1 || roleCol === -1) {
    throw new Error('Required columns not found');
  }
  
  const members = getTeamMembers(showData.showName).teamMembers;
  if (memberIndex >= members.length) throw new Error('Invalid member index');
  
  const member = members[memberIndex];
  
  // Find the row for this member
  let memberRow = -1;
  for (let i = 1; i < teamData.length; i++) {
    if (teamData[i][showNameCol] === showData.showName && 
        teamData[i][nameCol] === member.name) {
      memberRow = i + 1;
      break;
    }
  }
  
  if (memberRow === -1) {
    // Member doesn't exist, create new row
    teamSheet.appendRow([showData.showName, member.name, role]);
  } else {
    // Add role to existing roles
    const currentRoles = teamData[memberRow - 1][roleCol];
    const roles = currentRoles ? currentRoles.split(',').map(r => r.trim()) : [];
    if (!roles.includes(role)) {
      roles.push(role);
      teamSheet.getRange(memberRow, roleCol + 1).setValue(roles.join(', '));
    }
  }
  
  // Update key_creatives in shows sheet
  AddShowFeature.updateKeyCreatives(showData.showName);
  
  return getTeamMembers(showData.showName);
}

// Remove a role from a team member
function removeTeamMemberRole(memberIndex, role) {
  const showData = getCurrentShowData();
  if (!showData) throw new Error('No show selected');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  if (!teamSheet) throw new Error('Team sheet not found');
  
  const teamData = teamSheet.getDataRange().getValues();
  const headers = teamData[0];
  const showNameCol = headers.indexOf('show_name');
  const nameCol = headers.indexOf('name');
  const roleCol = headers.indexOf('roles');
  
  if (showNameCol === -1 || nameCol === -1 || roleCol === -1) {
    throw new Error('Required columns not found');
  }
  
  const members = getTeamMembers(showData.showName).teamMembers;
  if (memberIndex >= members.length) throw new Error('Invalid member index');
  
  const member = members[memberIndex];
  
  // Find the row and update roles
  for (let i = 1; i < teamData.length; i++) {
    if (teamData[i][showNameCol] === showData.showName && 
        teamData[i][nameCol] === member.name) {
      const currentRoles = teamData[i][roleCol].split(',').map(r => r.trim());
      const newRoles = currentRoles.filter(r => r !== role);
      
      if (newRoles.length === 0) {
        // If no roles left, delete the row
        teamSheet.deleteRow(i + 1);
      } else {
        // Update with remaining roles
        teamSheet.getRange(i + 1, roleCol + 1).setValue(newRoles.join(', '));
      }
      break;
    }
  }
  
  // Update key_creatives in shows sheet
  AddShowFeature.updateKeyCreatives(showData.showName);
  
  return getTeamMembers(showData.showName);
}

// Remove a team member
function removeTeamMember(index) {
  const showData = getCurrentShowData();
  if (!showData) throw new Error('No show selected');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  if (!teamSheet) throw new Error('Team sheet not found');
  
  const members = getTeamMembers(showData.showName).teamMembers;
  if (index >= members.length) throw new Error('Invalid member index');
  
  const member = members[index];
  
  const teamData = teamSheet.getDataRange().getValues();
  const headers = teamData[0];
  const showNameCol = headers.indexOf('show_name');
  const nameCol = headers.indexOf('name');
  
  if (showNameCol === -1 || nameCol === -1) {
    throw new Error('Required columns not found');
  }
  
  // Delete all rows for this member
  for (let i = teamData.length - 1; i >= 1; i--) {
    if (teamData[i][showNameCol] === showData.showName && 
        teamData[i][nameCol] === member.name) {
      teamSheet.deleteRow(i + 1);
    }
  }
  
  // Update key_creatives in shows sheet
  AddShowFeature.updateKeyCreatives(showData.showName);
  
  return getTeamMembers(showData.showName);
}

// Test function to run directly in Apps Script editor
function testAddTeamMember() {
  Logger.log('Starting test');
  try {
    // Get the shows sheet
    Logger.log('Getting active spreadsheet...');
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    Logger.log('Looking for sheet:', DB_CONFIG.sheetName);
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    Logger.log('Shows sheet found:', showsSheet ? 'yes' : 'no');
    if (!showsSheet) throw new Error('Shows sheet not found');
    
    // Get headers
    const headers = showsSheet.getRange(1, 1, 1, showsSheet.getLastColumn()).getValues()[0];
    Logger.log('Found headers:', headers);
    const showNameCol = headers.indexOf('shows');
    if (showNameCol === -1) throw new Error('shows column not found');
    Logger.log('Found shows column at index:', showNameCol);
    
    // Get first show name from the sheet
    const data = showsSheet.getDataRange().getValues();
    let showName = null;
    for (let i = 1; i < data.length; i++) {
      if (data[i][showNameCol]) {
        showName = data[i][showNameCol];
        break;
      }
    }
    if (!showName) throw new Error('No shows found in sheet');
    
    Logger.log('Found show:', showName);
    
    // Override getCurrentShowData for this test
    const originalGetCurrentShowData = getCurrentShowData;
    getCurrentShowData = () => ({ showName: showName });
    
    // Add team member
    addTeamMember('Test Member', 'Producer');
    Logger.log('Test completed successfully');
    
    // Restore original function
    getCurrentShowData = originalGetCurrentShowData;
  } catch (error) {
    Logger.log('Test failed - Error message: ' + error.message);
    Logger.log('Error stack: ' + error.stack);
  }
}
