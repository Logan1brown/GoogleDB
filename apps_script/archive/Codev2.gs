// Constants
const OTHER_STUDIO_OPTION = 'Other...';

// Configuration object for database fields
const DB_CONFIG = {
  // Sheet names match the actual Google Sheets names - removing duplicate sheetName
  OTHER_STUDIO_OPTION: OTHER_STUDIO_OPTION,
  fields: [
    { name: 'showName', label: 'Show Name', columnName: 'show_name', type: 'text', required: false },
    { name: 'keyCreatives', label: 'Key Creatives', columnName: 'key_creatives', type: 'computed', required: false, computedBy: 'show_team' },
    { name: 'network', label: 'Network', columnName: 'network', type: 'dropdown', required: true, source: 'networks' },
    { name: 'studios', label: 'Studio', columnName: 'studio', type: 'dropdown', required: true, source: 'studios' },
    { name: 'announcementDate', label: 'Announcement Date', columnName: 'date', type: 'date', required: false },
    { name: 'genre', label: 'Genre', columnName: 'genre', type: 'dropdown', required: false, source: 'genres' },
    { name: 'subgenre', label: 'Subgenre', columnName: 'subgenre', type: 'dropdown', required: false, source: 'subgenres' },
    { name: 'episodeCount', label: 'Episode Count', columnName: 'episode_count', type: 'number', required: false },
    { name: 'sourceType', label: 'Source Material', columnName: 'source_type', type: 'dropdown', required: false, source: 'sourceTypes' },
    { name: 'status', label: 'Status', columnName: 'status', type: 'dropdown', required: false, source: 'statuses' },
    { name: 'orderType', label: 'Order Type', columnName: 'order_type', type: 'dropdown', required: false, source: 'orderTypes' },
    { name: 'notes', label: 'Notes', columnName: 'notes', type: 'textarea', required: false }
  ],
  // Sheet names match the actual Google Sheets names
  sheetName: 'shows',
  studioSheet: 'studio_list',
  showTeamSheet: 'show_team',
  genreSheet: 'genre_list',
  subgenreSheet: 'subgenre_list',
  sourceTypeSheet: 'source_types',
  roleTypeSheet: 'role_types',
  networkSheet: 'network_list',
  orderTypeSheet: 'order_types',
  statusSheet: 'status_types',
  // Add standardized studio names mapping
  studioMapping: {
    // Major Studios
    "20th Television": ["20th Television", "20th Century Fox TV", "20th Century Fox Television", "20th Century Television", "20th TV Animation", "20th Television Animation"],
    "ABC Signature": ["ABC Signature", "ABC Studios", "ABC Signature Studios"],
    "Amazon Studios": ["Amazon Studios", "Amazon"],
    "AMC Studios": ["AMC Studios", "AMC"],
    "Apple Studios": ["Apple Studios", "Apple"],
    "CBS Studios": ["CBS Studios", "CBS Television Studios", "CBS TV Studios"],
    "Disney Television Studios": ["Disney Television Studios", "Disney"],
    "FX Productions": ["FX Productions", "FX"],
    "HBO": ["HBO", "HBO Max"],
    "Lionsgate Television": ["Lionsgate Television", "Lionsgate TV", "Lionsgate"],
    "MGM Television": ["MGM Television", "MGM"],
    "NBCUniversal": ["NBCUniversal", "Universal Television", "Universal Content Productions", "UCP"],
    "Netflix": ["Netflix"],
    "Paramount Television Studios": ["Paramount Television Studios", "Paramount TV Studios", "Paramount"],
    "Sony Pictures Television": ["Sony Pictures Television", "Sony Pictures TV", "Sony TV", "Sony"],
    "Warner Bros. Television": ["Warner Bros. Television", "Warner Bros. TV", "WBTV", "Warner Bros"],
    
    // Independent Studios
    "Entertainment One": ["Entertainment One", "eOne"],
    "MRC": ["MRC", "Media Rights Capital"],
    "Skydance Television": ["Skydance Television", "Skydance TV", "Skydance"],
    "Legendary Television": ["Legendary Television", "Legendary TV", "Legendary"],
    "Blumhouse Television": ["Blumhouse Television", "Blumhouse TV", "Blumhouse"],
    
    // International Studios
    "BBC Studios": ["BBC Studios", "BBC"],
    "ITV Studios": ["ITV Studios", "ITV"],
    
    // Other
    "Other": ["Other", "Independent", "TBD", "Various"]
  }
};

// Add the menu when the spreadsheet opens
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  var menu = ui.createMenu('Show Database');
  
  // Add menu items
  menu
    .addItem('Search & Edit Shows', 'showSearchSidebar')
    .addSeparator()
    .addItem('Add New Show', 'showAddForm')
    .addSeparator()
    .addItem('Setup Validation Rules', 'setupValidationRules')
    .addItem('Fix Validation Gaps', 'fixValidationSourceRanges');

  // Add the key creatives menu item
  addKeyCreativesMenuItem(menu);

  menu.addToUi();
}

// Show the search sidebar
function showSearchSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('SearchSidebarv2')
    .setTitle('Search Shows');
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Search for shows based on a query string.
 * Searches through show name, network, and studio fields.
 * @param {string} query - The search query
 * @return {Array} Array of matching show objects
 */
function searchShows(query) {
  try {
    if (!query || query.trim().length < 2) {
      return [];
    }

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    Logger.log('Available sheets:', ss.getSheets().map(s => s.getName()));
    
    const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
    if (!sheet) {
      throw new Error('Sheet "' + DB_CONFIG.sheetName + '" not found in searchShows. Available sheets: ' + 
        ss.getSheets().map(s => '"' + s.getName() + '"').join(', '));
    }
    
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    Logger.log('Headers in searchShows:', headers);
    
    // Get column names from DB_CONFIG
    const showNameField = DB_CONFIG.fields.find(f => f.name === 'showName');
    const networkField = DB_CONFIG.fields.find(f => f.name === 'network');
    const studiosField = DB_CONFIG.fields.find(f => f.name === 'studios');
    
    if (!showNameField || !networkField || !studiosField) {
      throw new Error('Required fields not found in DB_CONFIG');
    }
    
    // Use the actual column headers from the sheet
    const nameIdx = headers.indexOf(showNameField.columnName);
    const networkIdx = headers.indexOf(networkField.columnName);
    const studioIdx = headers.indexOf(studiosField.columnName);
    
    Logger.log(`Column indices - name: ${nameIdx}, network: ${networkIdx}, studio: ${studioIdx}`);
    
    if (nameIdx === -1 || networkIdx === -1 || studioIdx === -1) {
      throw new Error('Could not find required columns. Found indices: ' +
        `name=${nameIdx}, network=${networkIdx}, studio=${studioIdx}`);
    }
    
    // Normalize query
    const queryLower = query.toLowerCase().trim();
    
    // Search and return formatted results with row indices
    const results = data.slice(1) // Skip header row
      .map((row, idx) => {
        const result = {
          showName: row[nameIdx]?.toString() || '',
          network: row[networkIdx]?.toString() || '',
          studio: row[studioIdx]?.toString() || '',
          rowIndex: idx + 2 // +2 because we sliced off header row and sheet is 1-based
        };
        Logger.log('Mapped row ' + (idx + 2) + ':', result);
        return result;
      })
      .filter(show => {
        const matches = 
          show.showName.toLowerCase().includes(queryLower) ||
          show.network.toLowerCase().includes(queryLower) ||
          show.studio.toLowerCase().includes(queryLower);
        if (matches) {
          Logger.log('Found matching show:', show);
        }
        return matches;
      })
      .slice(0, 50); // Limit results to 50 shows

    Logger.log('Search results for "' + query + '":', results);
    return results;
  } catch (error) {
    Logger.log('Error in searchShows: ' + error.toString());
    throw error;
  }
}

/**
 * Show the edit form for a specific show
 * @param {string} showName - The name of the show to edit
 */
function initiateEdit(showName, rowIndex) {
  Logger.log('initiateEdit called with showName: "' + showName + '", rowIndex: ' + rowIndex);
  
  // Get team members for this show
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  // 1. Get role types and studios
  const roleTypes = getRoleTypes();
  const studios = getUniqueValues(DB_CONFIG.studioSheet, 'studio');
  Logger.log('Got role types:', roleTypes);
  Logger.log('Got studios:', studios);
  
  // 2. Get current studio
  const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
  let currentStudio = '';
  if (showsSheet) {
    const showsData = showsSheet.getDataRange().getValues();
    const showsHeaders = showsData[0];
    const studioIdx = showsHeaders.indexOf('studio');
    if (studioIdx !== -1) {
      const showRow = showsData.find(row => row[showsHeaders.indexOf('show_name')] === showName);
      if (showRow) {
        currentStudio = showRow[studioIdx];
      }
    }
  }
  Logger.log('Current studio:', currentStudio);

  // 3. Get team members
  let teamMembers = [];
  if (teamSheet) {
    const teamData = teamSheet.getDataRange().getValues();
    const headers = teamData[0];
    
    // Find column indices
    const showNameIdx = headers.indexOf('show_name');
    const nameIdx = headers.indexOf('name');
    const rolesIdx = headers.indexOf('roles');
    const orderIdx = headers.indexOf('order');
    const notesIdx = headers.indexOf('notes');
    
    if (showNameIdx !== -1 && nameIdx !== -1) {
      // Get all team members for this show
      teamMembers = teamData.slice(1) // Skip header row
        .filter(row => row[showNameIdx] === showName)
        .map(row => ({
          name: row[nameIdx],
          roles: rolesIdx !== -1 ? expandRoleAbbreviations(row[rolesIdx]) : '',
          order: orderIdx !== -1 ? row[orderIdx] : '',
          notes: notesIdx !== -1 ? row[notesIdx] : ''
        }));
    }
  }
  
  Logger.log('Found ' + teamMembers.length + ' team members for show: ' + showName);
  
  var template = HtmlService.createTemplateFromFile('EditFormv2');
  template.showName = showName;
  template.teamMembers = teamMembers;
  template.roleTypes = roleTypes;
  template.studios = studios;
  template.currentStudio = currentStudio;
  
  var html = template.evaluate()
    .setTitle('Edit Show')
    .setWidth(800)
    .setHeight(600);
  SpreadsheetApp.getUi().showModalDialog(html, 'Edit Show');
}

/**
 * Update show name and team members
 * @param {Object} data - Object containing show updates
 */
function updateShow(data) {
  try {
    Logger.log('Updating show with data:', data);
    
    // 1. First update the show name and studio if they changed
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    if (!showsSheet) {
      throw new Error('Shows sheet not found');
    }

    const showsData = showsSheet.getDataRange().getValues();
    const showsHeaders = showsData[0];
    const showsNameIdx = showsHeaders.indexOf('show_name');
    const studioIdx = showsHeaders.indexOf('studio');

    if (showsNameIdx === -1 || studioIdx === -1) {
      throw new Error('Required columns not found in shows sheet');
    }

    // Find the show's row
    const showRowIndex = showsData.findIndex(row => row[showsNameIdx] === data.oldShowName);
    if (showRowIndex === -1) {
      throw new Error('Show not found: ' + data.oldShowName);
    }

    // Update show name and studio
    const showRow = showsData[showRowIndex];
    if (data.oldShowName !== data.newShowName || showRow[studioIdx] !== data.studio) {
      showRow[showsNameIdx] = data.newShowName;
      showRow[studioIdx] = data.studio;
      showsSheet.getRange(showRowIndex + 1, 1, 1, showsHeaders.length).setValues([showRow]);
    }
    
    // 2. Then update team members
    const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    
    if (!teamSheet) {
      throw new Error('Show team sheet not found');
    }
    
    // Get all existing team members for this show
    const teamData = teamSheet.getDataRange().getValues();
    const headers = teamData[0];
    
    // Find column indices
    const teamNameIdx = headers.indexOf('show_name');
    const nameIdx = headers.indexOf('name');
    const rolesIdx = headers.indexOf('roles');
    const orderIdx = headers.indexOf('order');
    const notesIdx = headers.indexOf('notes');
    
    if (teamNameIdx === -1 || nameIdx === -1) {
      throw new Error('Required columns not found in show team sheet');
    }
    
    // Find rows for this show
    const showRows = teamData
      .map((row, index) => ({ row, index }))
      .filter(({ row }) => row[teamNameIdx] === data.oldShowName);
    
    // Delete all existing rows for this show
    if (showRows.length > 0) {
      const ranges = showRows
        .map(({ index }) => teamSheet.getRange(index + 1, 1, 1, headers.length))
        .reverse(); // Reverse so we delete from bottom to top
      
      ranges.forEach(range => teamSheet.deleteRow(range.getRow()));
    }
    
    // Add new team members
    if (data.teamMembers && data.teamMembers.length > 0) {
      const newRows = data.teamMembers.map(member => {
        const row = new Array(headers.length).fill('');
        row[teamNameIdx] = data.newShowName;
        row[nameIdx] = member.name;
        if (rolesIdx !== -1) row[rolesIdx] = abbreviateRoles(member.roles);
        if (orderIdx !== -1) row[orderIdx] = member.order;
        if (notesIdx !== -1) row[notesIdx] = member.notes;
        return row;
      });
      
      // After deleting rows, we need to get the last row again
      const lastRow = teamSheet.getLastRow();
      const insertRow = lastRow < 1 ? 2 : lastRow + 1;  // If sheet is empty (except header), start at row 2
      teamSheet.getRange(insertRow, 1, newRows.length, headers.length)
        .setValues(newRows);
        
      // Update key_creatives in shows sheet
      updateKeyCreatives();
    }
    
    Logger.log('Show and team members updated successfully');
    return true;
  } catch (error) {
    Logger.log('Error in updateShow: ' + error.toString());
    throw error;
  }
}

/**
 * Update just the show name in the shows sheet
 * @param {Object} data - Object containing oldShowName and newShowName
 */
function updateShowName(data) {
  try {
    Logger.log('Updating show name from "' + data.oldShowName + '" to "' + data.newShowName + '"');
    
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // 1. Update in shows sheet
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    if (!showsSheet) {
      throw new Error('Shows sheet not found');
    }
    
    // Find the show name column index
    const showNameField = DB_CONFIG.fields.find(f => f.name === 'showName');
    if (!showNameField) {
      throw new Error('Show name field not found in DB_CONFIG');
    }
    
    // Get all data from shows sheet
    const showsData = showsSheet.getDataRange().getValues();
    const showsHeaders = showsData[0];
    const showsNameIdx = showsHeaders.indexOf(showNameField.columnName);
    
    if (showsNameIdx === -1) {
      throw new Error('Show name column not found in shows sheet');
    }
    
    // Find and update in shows sheet
    const showsRowIdx = showsData.findIndex(row => row[showsNameIdx] === data.oldShowName);
    if (showsRowIdx === -1) {
      throw new Error('Show not found in shows sheet: ' + data.oldShowName);
    }
    showsSheet.getRange(showsRowIdx + 1, showsNameIdx + 1).setValue(data.newShowName);
    
    // 2. Update in show_team sheet
    const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    if (teamSheet) { // Only update if sheet exists
      const teamData = teamSheet.getDataRange().getValues();
      const headers = teamData[0];
      const teamNameIdx = headers.indexOf('show_name');
      
      if (teamNameIdx !== -1) { // Only update if column exists
        // Find all rows with the old show name
        const teamRows = teamData
          .map((row, index) => ({ row, index }))
          .filter(({ row }) => row[teamNameIdx] === data.oldShowName);
        
        // Update each row
        teamRows.forEach(({ index }) => {
          teamSheet.getRange(index + 1, teamNameIdx + 1).setValue(data.newShowName);
        });
        
        Logger.log('Updated ' + teamRows.length + ' rows in show_team sheet');
      }
    }
    
    Logger.log('Show name updated successfully in all sheets');
    return true;
  } catch (error) {
    Logger.log('Error in updateShowName: ' + error.toString());
    throw error;
  }
}

/**
 * Get show data directly using the same approach as searchShows
 */
function getShowDataDirect(showName, rowIndex) {
  try {
    Logger.log('Getting show data for:', { showName, rowIndex });
    
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
    if (!sheet) {
      throw new Error('Sheet not found: ' + DB_CONFIG.sheetName);
    }
    
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const row = data[rowIndex - 1]; // rowIndex is 1-based
    
    if (!row) {
      throw new Error('Row not found: ' + rowIndex);
    }
    
    // Just return show name for now
    const showNameIdx = headers.indexOf('show_name');
    if (showNameIdx === -1) {
      throw new Error('show_name column not found');
    }
    
    return {
      show_name: row[showNameIdx]
    };
    
  } catch (error) {
    Logger.log('Error getting show data:', error);
    throw error;
  }
}

/**
 * Update show data directly
 */
function updateShowDirect(data) {
  try {
    Logger.log('Updating show with data:', data);
    
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
    if (!sheet) {
      throw new Error('Sheet not found: ' + DB_CONFIG.sheetName);
    }
    
    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const values = headers.map(header => data[header] || '');
    
    // Update the row
    const range = sheet.getRange(data.rowIndex, 1, 1, headers.length);
    range.setValues([values]);
    
    // Handle team members if present
    if (data.teamMembers) {
      const showNameIndex = headers.indexOf('show_name');
      if (showNameIndex === -1) {
        throw new Error('show_name column not found');
      }
      const showName = values[showNameIndex];
      processTeamMembers(data.teamMembers, showName);
    }
    
    Logger.log('Successfully updated show at row:', data.rowIndex);
    
  } catch (error) {
    Logger.log('Error updating show:', error);
    throw error;
  }
}



// Show the edit sidebar
function showEditSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('EditSidebar')
    .setTitle('Edit Show');
  SpreadsheetApp.getUi().showSidebar(html);
}

// Get configuration and data for populating the form
function getFormData() {
  try {
    // First, validate that all required sheets exist
    const requiredSheets = [
      { name: DB_CONFIG.roleTypeSheet, label: 'Role Types' },
      { name: DB_CONFIG.networkSheet, label: 'Networks' },
      { name: DB_CONFIG.studioSheet, label: 'Studios' },
      { name: DB_CONFIG.genreSheet, label: 'Genres' },
      { name: DB_CONFIG.subgenreSheet, label: 'Subgenres' },
      { name: DB_CONFIG.sourceTypeSheet, label: 'Source Types' },
      { name: DB_CONFIG.statusSheet, label: 'Statuses' },
      { name: DB_CONFIG.orderTypeSheet, label: 'Order Types' }
    ];

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const missingSheets = requiredSheets.filter(sheet => !ss.getSheetByName(sheet.name));
    
    if (missingSheets.length > 0) {
      throw new Error(`Missing required sheets: ${missingSheets.map(s => s.label).join(', ')}`);
    }

    // Get roles first since they're critical for team member UI
    const roles = getRoleTypes();
    if (!roles || roles.length === 0) {
      throw new Error('No roles available. Please check the role_types sheet.');
    }

    // Get dynamic data for dropdowns and checkboxes
    var dynamicData = {};
    
    // Load all data with error handling for each
    const dataToLoad = [
      { key: 'roles', value: roles },
      { key: 'networks', value: getUniqueValues(DB_CONFIG.networkSheet, 'A') },
      { key: 'studios', value: getUniqueValues(DB_CONFIG.studioSheet, 'A') },
      { key: 'genres', value: getUniqueValues(DB_CONFIG.genreSheet, 'A') },
      { key: 'subgenres', value: getUniqueValues(DB_CONFIG.subgenreSheet, 'A') },
      { key: 'sourceTypes', value: getUniqueValues(DB_CONFIG.sourceTypeSheet, 'A') },
      { key: 'statuses', value: getUniqueValues(DB_CONFIG.statusSheet, 'A') },
      { key: 'orderTypes', value: getUniqueValues(DB_CONFIG.orderTypeSheet, 'A') }
    ];

    // Load each data type and validate
    dataToLoad.forEach(({ key, value }) => {
      if (!Array.isArray(value)) {
        throw new Error(`Failed to load ${key} data`);
      }
      dynamicData[key] = value;
      Logger.log(`Loaded ${value.length} ${key}`);
    });

    // Return both config and data
    return {
      config: DB_CONFIG,
      data: dynamicData
    };
  } catch (error) {
    Logger.log('Error in getFormData:', error);
    throw error; // Preserve the original error message
  }
}

// Convert role abbreviations to full names
function expandRoleAbbreviations(roleStr) {
  if (!roleStr) return '';
  
  const roleTypes = getRoleTypes();
  const roleMap = new Map();
  
  // Build map of abbreviations to full names
  roleTypes.forEach(roleObj => {
    roleObj.aliases.forEach(alias => {
      roleMap.set(alias.toLowerCase(), roleObj.role);
    });
    // Also map the full name to itself
    roleMap.set(roleObj.role.toLowerCase(), roleObj.role);
  });
  
  // Split input, expand each abbreviation, and rejoin
  return roleStr
    .split(',')
    .map(r => r.trim())
    .map(r => r.toLowerCase())
    .map(r => r.replace(/[()]/g, '')) // Remove parentheses
    .map(abbr => roleMap.get(abbr) || abbr) // Use original if no mapping found
    .join(', ');
}

// Convert full role names to abbreviations
function abbreviateRoles(roleStr) {
  if (!roleStr) return '';
  
  const roleTypes = getRoleTypes();
  const roleMap = new Map();
  
  // Build map of full names to preferred abbreviations
  roleTypes.forEach(roleObj => {
    if (roleObj.aliases && roleObj.aliases.length > 0) {
      roleMap.set(roleObj.role.toLowerCase(), roleObj.aliases[0]); // Use first alias as abbreviation
    }
  });
  
  // Split input, abbreviate each role, and rejoin
  return roleStr
    .split(',')
    .map(r => r.trim())
    .map(r => r.toLowerCase())
    .map(r => r.replace(/[()]/g, '')) // Remove parentheses
    .map(role => roleMap.get(role) || role) // Use original if no mapping found
    .join(', ');
}

// Get role types from the role_types sheet
function getRoleTypes() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(DB_CONFIG.roleTypeSheet);
    if (!sheet) {
      throw new Error('Role types sheet not found. Please check that the "role_types" sheet exists.');
    }

    const data = sheet.getDataRange().getValues();
    if (data.length < 2) {
      throw new Error('Role types sheet is empty. Please add some roles.');
    }

    const header = data[0];
    const roleCol = header.indexOf('role');
    const categoryCol = header.indexOf('category');
    const aliasesCol = header.indexOf('aliases');

    if (roleCol === -1 || categoryCol === -1 || aliasesCol === -1) {
      throw new Error('Required columns (role, category, aliases) not found in role_types sheet.');
    }

    const roles = [];
    const categories = new Set();
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      const role = (row[roleCol] || '').trim();
      const category = (row[categoryCol] || '').trim();
      const aliasesStr = (row[aliasesCol] || '').trim();
      const aliases = aliasesStr ? aliasesStr.split(',').map(a => a.trim()).filter(a => a) : [];

      // Skip empty roles or categories
      if (!role || !category) {
        Logger.log(`Skipping invalid row ${i + 1}: role="${role}", category="${category}"`);
        continue;
      }

      roles.push({
        role: role,
        category: category,
        aliases: aliases
      });
      categories.add(category);
    }

    if (roles.length === 0) {
      throw new Error('No valid roles found in role_types sheet. Please add some roles.');
    }

    Logger.log(`Loaded ${roles.length} roles across ${categories.size} categories`);
    return roles;
  } catch (error) {
    Logger.log('Error loading role types:', error);
    throw error; // Let the error propagate up
  }
}

// Helper function to get unique values from a column
function getUniqueValues(sheetName, column) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
    if (!sheet) {
      Logger.log('Sheet not found: ' + sheetName);
      return [];
    }
    
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      Logger.log('No data in sheet: ' + sheetName);
      return [];
    }
    
    const values = sheet.getRange(column + '2:' + column + lastRow)
      .getValues()
      .flat()
      .filter(function(value) { return value !== ''; })
      .filter(function(value, index, self) { return self.indexOf(value) === index; })
      .sort();
      
    Logger.log('Retrieved ' + values.length + ' values from ' + sheetName);
    return values;
  } catch (error) {
    Logger.log('Error in getUniqueValues for ' + sheetName + ': ' + error.toString());
    return [];
  }
}

// Add a new show to the spreadsheet
function addNewShow(formData) {
  try {
    Logger.log('Received form data:', JSON.stringify(formData));
    
    // Get both sheets
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    
    if (!showsSheet || !teamSheet) {
      throw new Error('Required sheets not found');
    }
    
    // Start transaction
    Logger.log('Starting transaction...');
    
    // 1. First add the show
    // Prepare row data in the same order as DB_CONFIG.fields
    var rowData = DB_CONFIG.fields.map(function(field) {
      var value = formData[field.name] || '';
      Logger.log('Processing field ' + field.name + ':', value);
      
      // Handle special field types
      switch (field.name) {
        case 'studios':
          return standardizeStudioName(value);
          
        case 'keyCreatives':
          // Handle team members data
          if (formData.teamMembers && formData.teamMembers.length > 0) {
            return formData.teamMembers
              .map(member => `${member.name}${member.roles ? ` (${member.roles})` : ''}`)
              .join(', ');
          }
          return 'No team members announced';
          
        case 'announcementDate':
          return value ? value.trim() : '';
          
        case 'episodeCount':
          return value ? parseInt(value) : '';
          
        default:
          return value ? value.trim() : '';
      }
    });
    
    Logger.log('Adding show to shows sheet...');
    // Get the last row and add new row directly after it
    const lastRow = showsSheet.getLastRow();
    const targetRange = showsSheet.getRange(lastRow + 1, 1, 1, rowData.length);
    targetRange.setValues([rowData]);
    
    // 2. Then add team members if present
    if (formData.teamMembers && formData.teamMembers.length > 0) {
      Logger.log('Processing team members...');
      const showName = formData.showName;
      
      // Convert team members to the correct format
      const teamMembers = formData.teamMembers.map(member => ({
        show_name: showName,
        name: member.name,
        roles: member.roles,
        order: member.order
      }));
      
      // Add team members
      addToShowTeam(teamMembers);
      Logger.log(`Added ${teamMembers.length} team members`);
    }
    
    Logger.log('Transaction complete');
    return true;
  } catch (error) {
    Logger.log('Error in addNewShow:', error.toString());
    throw new Error('Failed to add show: ' + error.message);
  }
}

// Add team members to show_team sheet
function addToShowTeam(teamMembers) {
  try {
    if (!teamMembers || teamMembers.length === 0) {
      Logger.log('No team members to add');
      return;
    }
    
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    
    if (!teamSheet) {
      throw new Error('Show team sheet not found');
    }
    
    // Get current data to check for duplicates
    const data = teamSheet.getDataRange().getValues();
    
    // Check for existing data - using show_name and name as unique key
    const existingEntries = new Set(
      data.slice(1).map(row => `${row[0]}|${row[1]}`)
    );
    
    // Filter out duplicates and prepare rows
    const newRows = teamMembers.filter(member => {
      // Skip team members without show names
      if (!member.show_name) {
        Logger.log(`Skipping team member ${member.name || 'unnamed'} - no show name provided`);
        return false;
      }
      // Validate name is required
      if (!member.name) {
        Logger.log('Skipping team member - no name provided');
        return false;
      }
      
      const key = `${member.show_name}|${member.name}`;
      const isDuplicate = existingEntries.has(key);
      
      if (isDuplicate) {
        Logger.log(`Skipping duplicate: ${member.name} for ${member.show_name}`);
      }
      
      return !isDuplicate;
    }).map(member => [
      member.show_name,
      member.name,
      member.roles || '',  // Allow empty roles
      member.order || '',  // Allow empty order
      member.notes || ''   // Allow empty notes
    ]);
    
    if (newRows.length === 0) {
      Logger.log('No new team members to add after filtering duplicates');
      return;
    }
    
    // Log what will be added
    Logger.log(`Adding ${newRows.length} team members...`);
    newRows.forEach(row => {
      Logger.log(`- ${row[1]} (${row[2] || 'No role'}) to ${row[0]}`);
    });
    
    // Append rows to sheet
    const lastRow = teamSheet.getLastRow();
    const range = teamSheet.getRange(lastRow + 1, 1, newRows.length, 5);
    range.setValues(newRows);
    
    Logger.log('Successfully added team members');
    
    // After adding new team members, update the key_creatives column
    updateKeyCreatives();
    
    return true;
  } catch (error) {
    Logger.log('Error in addToShowTeam:', error);
    throw error; // Re-throw to be handled by the caller
  }
}

// Validate a role against the role types list
function validateRole(role) {
  try {
    const roles = getRoleTypes();
    if (!role || typeof role !== 'string') return false;
    
    role = role.trim().toLowerCase();
    
    // Check if it matches any role or alias
    for (const roleType of roles) {
      if (roleType.role.toLowerCase() === role) return true;
      
      const aliases = roleType.aliases.map(a => a.toLowerCase());
      if (aliases.includes(role)) return true;
    }
    
    return false;
  } catch (error) {
    Logger.log('Error validating role:', error);
    return false;
  }
}

// Function to standardize studio names
function standardizeStudioName(studio) {
  if (!studio) return '';
  
  // Convert to string and trim
  studio = studio.toString().trim();
  
  // If it's already a main studio name, return as is
  if (Object.keys(DB_CONFIG.studioMapping).includes(studio)) {
    return studio;
  }
  
  // Look for matching aliases
  for (let [mainName, aliases] of Object.entries(DB_CONFIG.studioMapping)) {
    if (aliases.some(alias => 
        alias.toLowerCase() === studio.toLowerCase() ||
        studio.toLowerCase().includes(alias.toLowerCase()))) {
      return mainName;
    }
  }
  
  // If no match found, return original
  return studio;
}

// Setup data validation rules
function setupValidationRules() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
  
  if (!showsSheet) {
    throw new Error('Shows sheet not found');
  }
  
  // Get the last row and column
  var lastRow = Math.max(showsSheet.getLastRow(), 2);  // At least 2 for header
  var lastCol = showsSheet.getLastColumn();
  
  // Get headers
  var headers = showsSheet.getRange(1, 1, 1, lastCol).getValues()[0];
  
  // Setup validation for each field
  DB_CONFIG.fields.forEach(field => {
    if (field.type === 'dropdown' && field.source) {
      var colIndex = headers.indexOf(field.label) + 1;
      if (colIndex > 0) {  // If column found
        var sourceRange = `=${field.source}!A:A`;
        var rule = SpreadsheetApp.newDataValidation()
          .requireValueInRange(ss.getRange(sourceRange), true)
          .setAllowInvalid(false)
          .build();
        
        showsSheet.getRange(2, colIndex, lastRow - 1, 1)
          .setDataValidation(rule);
      }
    }
  });
}

// Fix validation source ranges
function fixValidationSourceRanges() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
  
  if (!showsSheet) {
    throw new Error('Shows sheet not found');
  }
  
  // Get the last row
  var lastRow = Math.max(showsSheet.getLastRow(), 2);
  
  // Get headers
  var headers = showsSheet.getRange(1, 1, 1, showsSheet.getLastColumn()).getValues()[0];
  
  // Update validation for each dropdown field
  DB_CONFIG.fields.forEach(field => {
    if (field.type === 'dropdown' && field.source) {
      var colIndex = headers.indexOf(field.label) + 1;
      if (colIndex > 0) {
        var sourceRange = `=${field.source}!A:A`;
        var rule = SpreadsheetApp.newDataValidation()
          .requireValueInRange(ss.getRange(sourceRange), true)
          .setAllowInvalid(false)
          .build();
        
        showsSheet.getRange(2, colIndex, lastRow - 1, 1)
          .setDataValidation(rule);
      }
    }
  });
}

/**
 * Show the add form for a new show
 */
function showAddForm() {
  var html = HtmlService.createTemplateFromFile('AddForm')
    .evaluate()
    .setWidth(600)
    .setHeight(800)
    .setSandboxMode(HtmlService.SandboxMode.NATIVE);
  SpreadsheetApp.getUi().showModalDialog(html, 'Add New Show');
}
