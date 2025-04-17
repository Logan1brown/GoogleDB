const AddShowFeature = {
  // Menu registration
  registerMenuItems: function(menu) {
    menu.addItem('Add New Show', 'showAddForm');
  },

  // Show the add form
  showForm: function() {
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
    
    const html = HtmlService.createTemplateFromFile('AddShow')
      .evaluate()
      .setWidth(600)
      .setHeight(800);
    SpreadsheetApp.getUi().showModalDialog(html, 'Add New Show');
  },

  // Get form configuration and data
  getFormData: function() {
    try {
      // First, validate that all required sheets exist
      const requiredSheets = [
        { name: DB_CONFIG.roleTypeSheet, label: 'role_types' },
        { name: DB_CONFIG.networkSheet, label: 'network_list' },
        { name: DB_CONFIG.studioSheet, label: 'studio_list' },
        { name: DB_CONFIG.genreSheet, label: 'genre_list' },
        { name: DB_CONFIG.subgenreSheet, label: 'subgenre_list' },
        { name: DB_CONFIG.sourceTypeSheet, label: 'source_types' },
        { name: DB_CONFIG.statusSheet, label: 'status_types' },
        { name: DB_CONFIG.orderTypeSheet, label: 'order_types' }
      ];

      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const missingSheets = requiredSheets.filter(sheet => !ss.getSheetByName(sheet.name));
      
      if (missingSheets.length > 0) {
        throw new Error(`Missing required sheets: ${missingSheets.map(s => s.label).join(', ')}`);
      }

      // Get roles first since they're critical for team member UI
      const roles = this.getRoleTypes();
      if (!roles || roles.length === 0) {
        throw new Error('No roles available. Please check the role_types sheet.');
      }

      // Get dynamic data for dropdowns
      const dynamicData = {
        roles: roles,
        networks: this.getUniqueValues(DB_CONFIG.networkSheet, 'A'),
        studios: this.getUniqueValues(DB_CONFIG.studioSheet, 'A'),
        genres: this.getUniqueValues(DB_CONFIG.genreSheet, 'A'),
        subgenres: this.getUniqueValues(DB_CONFIG.subgenreSheet, 'A'),
        sourceTypes: this.getUniqueValues(DB_CONFIG.sourceTypeSheet, 'A'),
        statuses: this.getUniqueValues(DB_CONFIG.statusSheet, 'A'),
        orderTypes: this.getUniqueValues(DB_CONFIG.orderTypeSheet, 'A')
      };

      // Validate all data is loaded
      Object.entries(dynamicData).forEach(([key, value]) => {
        if (!Array.isArray(value)) {
          throw new Error(`Failed to load ${key} data`);
        }
        Logger.log(`Loaded ${value.length} ${key}`);
      });

      return {
        config: DB_CONFIG,
        data: dynamicData
      };
    } catch (error) {
      Logger.log('Error in getFormData:', error);
      throw error;
    }
  },

  // Get unique values from a column
  getUniqueValues: function(sheetName, column) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(sheetName);
    
    if (!sheet) {
      throw new Error(`Sheet ${sheetName} not found`);
    }
    
    const data = sheet.getRange(column + '2:' + column)
      .getValues()
      .map(row => row[0])
      .filter(value => value !== '');
      
    return [...new Set(data)].sort();
  },

  // Get role types
  getRoleTypes: function() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(DB_CONFIG.roleTypeSheet);
    
    if (!sheet) {
      throw new Error('Role types sheet not found');
    }
    
    const data = sheet.getRange('A2:A')
      .getValues()
      .map(row => row[0])
      .filter(value => value !== '');
      
    return [...new Set(data)].sort();
  },

  // Update key creatives in shows sheet based on show_team data
  updateKeyCreatives: function(showName) {
    Logger.log('Updating key creatives for show:', showName);
    
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const showTeamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    
    Logger.log('Got sheets:', {
      showTeamSheet: showTeamSheet ? 'found' : 'not found',
      showsSheet: showsSheet ? 'found' : 'not found'
    });
    
    // Get all data from both sheets
    const showTeamData = showTeamSheet.getDataRange().getValues();
    const showsData = showsSheet.getDataRange().getValues();
    
    // Find column indices
    const showTeamHeaders = showTeamData[0];
    const showsHeaders = showsData[0];
    
    Logger.log('Headers:', {
      showTeam: showTeamHeaders,
      shows: showsHeaders
    });
    
    // Get column indices for show_team sheet (uses 'show_name' in first column)
    const showNameColTeam = 0;  // First column
    const nameColTeam = 1;      // Second column
    const rolesColTeam = 2;     // Third column
    const orderColTeam = 3;     // Fourth column
    
    // Get column indices for shows sheet (uses 'shows' column for show names)
    const showNameColShows = showsHeaders.indexOf('shows');
    const keyCreativesCol = showsHeaders.indexOf('key_creatives');
    
    Logger.log('Column indices:', {
      showNameColShows,
      keyCreativesCol
    });
    
    if (keyCreativesCol === -1) {
      throw new Error('Could not find key_creatives column in shows sheet');
    }
    
    // Create a map of show names to their team members
    const showTeamMap = new Map();
    
    // Skip header row
    for (let i = 1; i < showTeamData.length; i++) {
      const row = showTeamData[i];
      const currentShowName = row[showNameColTeam];
      if (currentShowName !== showName) continue; // Only process the show we just added
      
      const name = row[nameColTeam];
      const roles = row[rolesColTeam];
      const order = row[orderColTeam];
      
      if (!showTeamMap.has(currentShowName)) {
        showTeamMap.set(currentShowName, []);
      }
      showTeamMap.get(currentShowName).push({
        name: name,
        roles: roles,
        order: order
      });
    }
    
    // Update shows sheet
    const updatedShowsData = showsData.map((row, index) => {
      if (index === 0) return row; // Skip header row
      
      const currentShowName = row[showNameColShows];
      if (currentShowName !== showName) return row; // Only update the show we just added
      
      const teamMembers = showTeamMap.get(currentShowName) || [];
      
      // Sort team members by order if available
      teamMembers.sort((a, b) => {
        if (a.order && b.order) return a.order - b.order;
        if (a.order) return -1;
        if (b.order) return 1;
        return 0;
      });
      
      // Format key creatives string
      const keyCreatives = teamMembers
        .map(member => {
          return member.roles ? `${member.name} (${member.roles})` : member.name;
        })
        .join(', ') || 'No team members announced';
      
      row[keyCreativesCol] = keyCreatives;
      return row;
    });
    
    // Update the shows sheet with new data
    showsSheet.getRange(1, 1, updatedShowsData.length, updatedShowsData[0].length)
      .setValues(updatedShowsData);
  },

  // Add a new show
  addNewShow: function(formData) {
    try {
      Logger.log('Received form data:', JSON.stringify(formData));
      
      const ss = SpreadsheetApp.getActiveSpreadsheet();
      const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
      const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
      
      if (!showsSheet || !teamSheet) {
        throw new Error('Required sheets not found');
      }
      
      // Start transaction
      Logger.log('Starting transaction...');
      
      // 1. First add the show with empty key_creatives
      const rowData = DB_CONFIG.fields.map(field => {
        const value = formData[field.name] || '';
        Logger.log('Processing field ' + field.name + ':', value);
        
        switch (field.name) {
          case 'keyCreatives':
            return ''; // Will be updated after team members are added
            
          case 'announcementDate':
            // Value should already be in YYYY/MM/DD format from the form
            // Just validate it's a proper date string
            if (value) {
              const parts = value.trim().split('/');
              if (parts.length === 3) {
                const year = parseInt(parts[0]);
                const month = parseInt(parts[1]);
                const day = parseInt(parts[2]);
                if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
                  return value.trim();
                }
              }
              Logger.log('Invalid date format received:', value);
            }
            return '';
            
          case 'episodeCount':
            return value ? parseInt(value) : '';
            
          default:
            return value ? value.trim() : '';
        }
      });
      
      // Add show to shows sheet
      Logger.log('Adding show to shows sheet...');
      const lastRow = showsSheet.getLastRow();
      const targetRange = showsSheet.getRange(lastRow + 1, 1, 1, rowData.length);
      targetRange.setValues([rowData]);
      
      // 2. Then add team members if present
      if (formData.teamMembers && formData.teamMembers.length > 0) {
        Logger.log('Processing team members...');
        const showName = formData.showName;
        
        const teamMembers = formData.teamMembers
          .filter(member => member.name && member.roles) // Only add if both name and role are present
          .map((member, index) => ({
            show_name: showName,
            name: member.name,
            roles: member.roles,
            order: index + 1 // Ensure sequential order
          }));
        
        if (teamMembers.length > 0) {
          this.addToShowTeam(teamMembers);
          Logger.log(`Added ${teamMembers.length} team members`);
          
          // 3. Update key_creatives in shows sheet
          this.updateKeyCreatives(showName);
        }
      }
      
      Logger.log('Transaction complete');
      return true;
    } catch (error) {
      Logger.log('Error in addNewShow:', error.toString());
      throw new Error('Failed to add show: ' + error.message);
    }
  },

  // Add team members
  addToShowTeam: function(teamMembers) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    
    if (!sheet) {
      throw new Error('Show team sheet not found');
    }
    
    const rows = teamMembers.map(member => [
      member.show_name,
      member.name,
      member.roles || '',
      member.order || ''
    ]);
    
    if (rows.length > 0) {
      const lastRow = sheet.getLastRow();
      const targetRange = sheet.getRange(lastRow + 1, 1, rows.length, 4);
      targetRange.setValues(rows);
    }
  }
};

// Global functions to be called from the menu and HTML
function showAddForm() {
  AddShowFeature.showForm();
}

function getFormData() {
  return AddShowFeature.getFormData();
}

function addNewShow(formData) {
  return AddShowFeature.addNewShow(formData);
}
