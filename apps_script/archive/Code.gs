// Constants
const OTHER_STUDIO_OPTION = 'Other...';

// Configuration object for database fields
const DB_CONFIG = {
  OTHER_STUDIO_OPTION: OTHER_STUDIO_OPTION,
  fields: [
    { name: 'showName', label: 'Show Name', type: 'text', required: false },
    { name: 'keyCreatives', label: 'Key Creatives', type: 'computed', required: false, computedBy: 'show_team' },
    { name: 'network', label: 'Network', type: 'dropdown', required: true, source: 'networks' },
    { name: 'studios', label: 'Studio', type: 'dropdown', required: true, source: 'studios' },
    { name: 'announcementDate', label: 'Announcement Date', type: 'date', required: false },
    { name: 'genre', label: 'Genre', type: 'dropdown', required: false, source: 'genres' },
    { name: 'subgenre', label: 'Subgenre', type: 'dropdown', required: false, source: 'subgenres' },
    { name: 'episodeCount', label: 'Episode Count', type: 'number', required: false },
    { name: 'sourceType', label: 'Source Material', type: 'dropdown', required: false, source: 'sourceTypes' },
    { name: 'status', label: 'Status', type: 'dropdown', required: false, source: 'statuses' },
    { name: 'orderType', label: 'Order Type', type: 'dropdown', required: false, source: 'orderTypes' },
    { name: 'notes', label: 'Notes', type: 'textarea', required: false }
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
    "ABC Studios": ["ABC Studios", "ABC Signature", "ABC Signature Studios"],
    "CBS Studios": ["CBS Studios", "CBS TV Studios", "CBS Television Studios"],
    "Disney Television": ["Disney Branded Television", "Disney Television Animation"],
    "HBO": ["HBO", "HBO Max"],
    "Lionsgate Television": ["Lionsgate", "Lionsgate TV", "Lionsgate Television"],
    "MGM Television": ["MGM Television", "MGM", "MGM/UA Television"],
    "MTV Entertainment Studios": ["MTV Entertainment Studios"],
    "Paramount Television Studios": ["Paramount TV", "Paramount Television", "Paramount Television Studios"],
    "Sony Pictures Television": ["Sony Pictures TV", "Sony Pictures Television", "Sony Pictures Television Studios"],
    "Universal Television": ["Universal TV", "Universal Television", "Universal Studio Group", "UCP"],
    "Warner Bros. Television": ["Warner Bros TV", "Warner Bros Television", "Warner Bros. TV", "Warner Bros. Television", 
                              "Warner Bros. Studio", "Warner Horizon Scripted Television", "Warner Bros. Television.", 
                              "Warner Brothers Television", "WarnerMedia Entertainment"],
    
    // Production Companies
    "3 Arts Entertainment": ["3 Arts", "3 Arts Entertainment"],
    "6th & Idaho": ["6th & Idaho", "6th & Idaho Productions"],
    "Bad Robot": ["Bad Robot", "Bad Robot Productions"],
    "Berlanti Productions": ["Berlanti Productions"],
    "Warner Bros. Animation": ["Warner Bros Animation", "Warner Bros. Animation"],
    
    // Other Notable Studios
    "A+E Studios": ["A+E Studios"],
    "FX Productions": ["FX Productions"],
    "Hello Sunshine": ["Hello Sunshine"],
    "Marvel Studios": ["Marvel", "Marvel Studios", "Marvel Television"],
    "SISTER": ["Sister", "SISTER Proverbial Pictures"],
    "wiip": ["wiip"]
  }
};

// Create the custom menu
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  var menu = ui.createMenu('Show Database')
    .addItem('Search Shows', 'showSearchSidebar')
    .addItem('Add New Show', 'showAddForm')
    .addItem('Edit Show', 'showEditSidebar')
    .addSeparator()
    .addItem('Setup Validation Rules', 'setupValidationRules')
    .addItem('Fix Validation Gaps', 'fixValidationSourceRanges');

  // Add the key creatives menu item
  addKeyCreativesMenuItem(menu);

  menu.addToUi();
}

// Show the search sidebar
function showSearchSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('SearchSidebar')
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
    const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    
    // Use exact column names from the sheet
    const nameIdx = headers.indexOf('show_name');
    const networkIdx = headers.indexOf('network');
    const studioIdx = headers.indexOf('studio');
    
    Logger.log(`Column indices - name: ${nameIdx}, network: ${networkIdx}, studio: ${studioIdx}`);
    
    if (nameIdx === -1 || networkIdx === -1 || studioIdx === -1) {
      throw new Error('Could not find required columns. Found indices: ' +
        `name=${nameIdx}, network=${networkIdx}, studio=${studioIdx}`);
    }
    
    // Normalize query
    const queryLower = query.toLowerCase().trim();
    
    // Search and return formatted results
    return data.slice(1) // Skip header row
      .map((row, idx) => ({
        rowIndex: idx + 2, // +2 for 1-based index and header row
        showName: row[nameIdx]?.toString() || '',
        network: row[networkIdx]?.toString() || '',
        studio: row[studioIdx]?.toString() || ''
      }))
      .filter(show => 
        (show.showName.toLowerCase().includes(queryLower) ||
         show.network.toLowerCase().includes(queryLower) ||
         show.studio.toLowerCase().includes(queryLower))
      )
      .slice(0, 50); // Limit results to 50 shows
  } catch (error) {
    Logger.log('Error in searchShows: ' + error.toString());
    throw error;
  }
}

// Show the add form
function showAddForm() {
  var html = HtmlService.createTemplateFromFile('AddForm')
    .evaluate()
    .setWidth(600)
    .setHeight(800)
    .setSandboxMode(HtmlService.SandboxMode.NATIVE);
  SpreadsheetApp.getUi().showModalDialog(html, 'Add New Show');
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
      { name: DB_CONFIG.orderTypeSheet, label: 'Order Types' },
      { name: DB_CONFIG.showTeamSheet, label: 'Show Team' }
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
      { key: 'orderTypes', value: getUniqueValues(DB_CONFIG.orderTypeSheet, 'A') },
      { key: 'showTeam', value: getUniqueValues(DB_CONFIG.showTeamSheet, 'A') }
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

// Helper function to get standardized studio names
function getStandardizedStudios() {
  // Get the standardized names (keys) from the mapping
  var standardizedNames = Object.keys(DB_CONFIG.studioMapping);
  standardizedNames.sort();
  standardizedNames.push(DB_CONFIG.OTHER_STUDIO_OPTION);
  return standardizedNames;
}

// Helper function to standardize a studio name
function standardizeStudioName(studio) {
  // Check each standardized name's variations
  for (var standardName in DB_CONFIG.studioMapping) {
    if (DB_CONFIG.studioMapping[standardName].includes(studio.trim())) {
      return standardName;
    }
  }
  return studio; // Return original if no mapping found
}

// Parse key creatives string into show_team entries
function parseKeyCreatives(showName, keyCreatives) {
  if (!keyCreatives) return [];
  
  const teamMembers = [];
  
  // Split on commas, but not within parentheses
  const splitRegex = /,(?![^(]*\))/;
  const members = keyCreatives.split(splitRegex).map(m => m.trim());
  
  members.forEach((member, index) => {
    // Extract name and roles
    const match = member.match(/([^(]+)(?:\(([^)]+)\))?/);
    if (!match) return;
    
    const name = match[1].trim();
    const roles = match[2] ? match[2].split(',').map(r => r.trim()) : [];
    
    // Only add if we have a name
    if (name) {
      teamMembers.push({
        show_name: showName,
        name: name,
        roles: roles.join(', '),  // Store multiple roles comma-separated
        order: index + 1,
        notes: ''
      });
    }
  });
  
  return teamMembers;
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
      // Validate required fields
      if (!member.show_name) {
        throw new Error(`Show name is required for team member ${member.name}`);
      }
      if (!member.name) {
        throw new Error('Team member name is required');
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

// Test the parsing with a single show
function testKeyCreativesParser() {
  Logger.log('Starting key creatives parser test...');
  
  const testCases = [
    {
      name: "[TEST] Big Shot",
      keyCreatives: "David E. Kelley (w, ep), Dead Lorey (w, ep), Brad Garrett (ep), Bill D'Elia (d)"
    },
    {
      name: "[TEST] Doctor Odyssey",
      keyCreatives: "Ryan Murphy, Joshua Jackson"
    }
  ];
  
  // First check the show_team sheet
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const teamSheet = ss.getSheetByName('show_team');
  
  if (!teamSheet) {
    Logger.log('Error: show_team sheet not found!');
    return;
  }
  
  const lastRow = teamSheet.getLastRow();
  Logger.log(`Current show_team sheet has ${lastRow} rows`);
  
  // Process and add each test case
  let allTeamMembers = [];
  testCases.forEach(show => {
    Logger.log('\nProcessing show: ' + show.name);
    Logger.log('Input: ' + show.keyCreatives);
    
    const teamMembers = parseKeyCreatives(show.name, show.keyCreatives);
    Logger.log('Parsed result:');
    Logger.log(JSON.stringify(teamMembers, null, 2));
    
    allTeamMembers = allTeamMembers.concat(teamMembers);
  });
  
  // Add to sheet
  if (allTeamMembers.length > 0) {
    addToShowTeam(allTeamMembers);
    Logger.log('\nAdded test data to show_team sheet');
    Logger.log('To remove test data, run the removeTestData() function');
  }
  
  Logger.log('\nTest complete. Check show_team sheet for results.');
}

// Function to remove test data
function removeTestData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('show_team');
  
  if (!sheet) {
    Logger.log('Error: show_team sheet not found!');
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  const rowsToDelete = [];
  
  // Find rows with [TEST] prefix (in reverse order to handle deletion)
  for (let i = data.length - 1; i >= 0; i--) {
    if (data[i][0].toString().includes('[TEST]')) {
      rowsToDelete.push(i + 1); // +1 because rows are 1-indexed
    }
  }
  
  // Delete the rows
  rowsToDelete.forEach(row => {
    sheet.deleteRow(row);
  });
  
  Logger.log(`Removed ${rowsToDelete.length} test entries`);
}

// Function to migrate existing show data to show_team
function migrateShowTeamData() {
  Logger.log('Starting show team migration...');
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
  const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
  
  if (!showsSheet || !teamSheet) {
    Logger.log('Error: Required sheets not found');
    return;
  }
  
  // Get all shows data
  const showsData = showsSheet.getDataRange().getValues();
  const headers = showsData[0];
  
  // Find column indices
  const showNameCol = headers.indexOf('show_name');
  const keyCreativesCol = headers.indexOf('key_creatives');
  
  if (showNameCol === -1 || keyCreativesCol === -1) {
    Logger.log('Error: Required columns not found');
    return;
  }
  
  // Process each show
  let processedShows = 0;
  let totalTeamMembers = 0;
  let allTeamMembers = [];
  
  // Skip header row
  for (let i = 1; i < showsData.length; i++) {
    const row = showsData[i];
    const showName = row[showNameCol];
    const keyCreatives = row[keyCreativesCol];
    
    if (!showName || !keyCreatives) continue;
    
    Logger.log(`Processing show: ${showName}`);
    const teamMembers = parseKeyCreatives(showName, keyCreatives);
    
    if (teamMembers.length > 0) {
      allTeamMembers = allTeamMembers.concat(teamMembers);
      processedShows++;
      totalTeamMembers += teamMembers.length;
    }
  }
  
  // Add all team members in one batch
  if (allTeamMembers.length > 0) {
    addToShowTeam(allTeamMembers);
  }
  
  Logger.log(`Migration complete!`);
  Logger.log(`Processed ${processedShows} shows`);
  Logger.log(`Added ${totalTeamMembers} team members`);
}

// Note: All validation rules are now managed manually through the Google Sheets UI
// The following functions have been removed as they are no longer needed:
// - createValidationRule
// - setupLookupTableValidation
// - setupValidationRules
// - fixValidationSourceRanges
// - resetAllValidationRanges



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
          return value;
          
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
