const SearchEditFeature = {
  // Menu registration
  registerMenuItems: function(menu) {
    menu.addItem('Search/Edit Shows', 'showSearchSidebar');
  },

  // Show the search sidebar
  showSearchSidebar: function() {
    const html = HtmlService.createHtmlOutputFromFile('SearchSidebar')
      .setTitle('Search Shows')
      .setWidth(400);
    SpreadsheetApp.getUi().showSidebar(html);
  },

  // Search for shows
  searchShows: function(query) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    
    if (!showsSheet) {
      throw new Error('Shows sheet not found');
    }

    // Get all data including headers
    const data = showsSheet.getDataRange().getValues();
    const headers = data[0];
    
    // Find relevant column indices
    const showNameCol = headers.indexOf('show_name');
    const networkCol = headers.indexOf('network');
    const studioCol = headers.indexOf('studio');
    const genreCol = headers.indexOf('genre');
    const statusCol = headers.indexOf('status');
    
    if (showNameCol === -1) {
      throw new Error('Required column "show_name" not found');
    }

    // Skip header row and filter results
    const results = data.slice(1)
      .map((row, index) => ({
        rowIndex: index + 2, // +2 because we sliced off header and sheets are 1-indexed
        show_name: String(row[showNameCol] || ''),
        network: String(row[networkCol] || ''),
        studio: String(row[studioCol] || ''),
        genre: String(row[genreCol] || ''),
        status: String(row[statusCol] || '')
      }))
      .filter(show => {
        const searchStr = String(query || '').toLowerCase();
        return show.show_name.toLowerCase().includes(searchStr) ||
               show.network.toLowerCase().includes(searchStr) ||
               show.studio.toLowerCase().includes(searchStr) ||
               show.genre.toLowerCase().includes(searchStr) ||
               show.status.toLowerCase().includes(searchStr);
      });

    return results;
  },

  // Get studio list with aliases
  getStudioList: function() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const studioSheet = ss.getSheetByName(DB_CONFIG.studioSheet);
    
    if (!studioSheet) {
      throw new Error('Studio list sheet not found');
    }
    
    const data = studioSheet.getDataRange().getValues();
    const studios = new Map();
    
    // Skip header row
    data.slice(1).forEach(row => {
      const mainName = row[0];
      const aliases = row[1] ? String(row[1]).split(',').map(s => s.trim()) : [];
      
      if (mainName) {
        studios.set(mainName.toLowerCase(), mainName);
        aliases.forEach(alias => {
          if (alias) studios.set(alias.toLowerCase(), mainName);
        });
      }
    });
    
    return studios;
  },

  // Get show data for editing
  getShowData: function(rowIndex) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    const studioSheet = ss.getSheetByName(DB_CONFIG.studioSheet);
    
    if (!showsSheet || !teamSheet || !studioSheet) {
      throw new Error('Required sheets not found');
    }

    // Get show data
    const showData = showsSheet.getRange(rowIndex, 1, 1, showsSheet.getLastColumn()).getValues()[0];
    const headers = showsSheet.getRange(1, 1, 1, showsSheet.getLastColumn()).getValues()[0];
    
    // Create show object with normalized field names
    const show = {};
    const fieldMap = {
      'show_name': 'showName',
      'key_creatives': 'keyCreatives',
      'announcement_date': 'announcementDate',
      'episode_count': 'episodeCount',
      'source_type': 'sourceType',
      'order_type': 'orderType'
    };
    
    headers.forEach((header, index) => {
      const value = showData[index];
      const normalizedHeader = fieldMap[header] || header;
      
      // Handle date fields specially
      if ((header === 'announcement_date' || header === 'date') && value) {
        Logger.log('Processing date field:', header, 'with value:', value);
        if (value instanceof Date) {
          show.announcementDate = value.toISOString();
          Logger.log('Date from sheet:', value, 'converted to:', show.announcementDate);
        } else {
          show.announcementDate = String(value || '');
          Logger.log('Non-date value in date field:', value);
        }
      } else {
        show[normalizedHeader] = String(value || '');
      }
    });
    
    // Handle studio aliases
    if (show.studio) {
      const studios = show.studio.split(',').map(s => s.trim());
      const normalizedStudios = [];
      
      // Get all studios and their aliases
      const studioData = studioSheet.getDataRange().getValues();
      
      studios.forEach(studio => {
        // Try to find a match in the studio list
        for (let i = 1; i < studioData.length; i++) {
          const mainName = studioData[i][0];
          const aliases = studioData[i][3] ? String(studioData[i][3]).split(',').map(s => s.trim()) : [];
          
          // Check if studio matches main name or any alias
          const normalizedStudio = studio.toLowerCase().replace(/\./g, '');
          const normalizedMain = mainName.toLowerCase().replace(/\./g, '');
          if (normalizedStudio === normalizedMain ||
              aliases.some(alias => normalizedStudio === alias.toLowerCase().replace(/\./g, ''))) {
            // Only add if not already in the list (avoid duplicates)
            if (!normalizedStudios.includes(mainName)) {
              normalizedStudios.push(mainName);
            }
            break;
          }
        }
      });
      
      // Update show.studio with normalized, comma-separated list
      show.studio = normalizedStudios.join(', ');
    }

    // Get team members
    const teamData = teamSheet.getDataRange().getValues();
    const teamHeaders = teamData[0];
    const showNameColTeam = teamHeaders.indexOf('show_name');
    
    // Use original show name from data, not normalized version
    const showName = showData[headers.indexOf('show_name')];
    
    const teamMembers = teamData.slice(1)
      .filter(row => row[showNameColTeam] === showName)
      .map(row => ({
        name: row[teamHeaders.indexOf('name')] || '',
        roles: row[teamHeaders.indexOf('roles')] || '',
        order: row[teamHeaders.indexOf('order')] || ''
      }))
      .sort((a, b) => (a.order || 0) - (b.order || 0));

    show.teamMembers = teamMembers;
    return show;
  },

  // Update show data
  updateShow: function(rowIndex, formData) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const showsSheet = ss.getSheetByName(DB_CONFIG.sheetName);
    
    if (!showsSheet) {
      throw new Error('Shows sheet not found');
    }

    try {
      // 1. Update show in shows sheet
      const headers = showsSheet.getRange(1, 1, 1, showsSheet.getLastColumn()).getValues()[0];
      const rowData = headers.map(header => {
        const value = formData[header] || '';
        return header === 'key_creatives' ? '' : value; // key_creatives will be updated from show_team
      });
      
      showsSheet.getRange(rowIndex, 1, 1, rowData.length).setValues([rowData]);
      
      // 2. Update team members
      if (formData.teamMembers && formData.teamMembers.length > 0) {
        // First remove existing team members for this show
        const teamSheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
        const teamData = teamSheet.getDataRange().getValues();
        const showNameCol = teamData[0].indexOf('show_name');
        
        const showName = formData.show_name;
        const rowsToDelete = [];
        
        teamData.forEach((row, index) => {
          if (index > 0 && row[showNameCol] === showName) {
            rowsToDelete.unshift(index + 1); // Add to front so we delete from bottom up
          }
        });
        
        rowsToDelete.forEach(row => {
          teamSheet.deleteRow(row);
        });
        
        // Then add new team members
        const teamMembers = formData.teamMembers
          .filter(member => member.name && member.roles)
          .map((member, index) => ({
            show_name: showName,
            name: member.name,
            roles: member.roles,
            order: index + 1
          }));
        
        if (teamMembers.length > 0) {
          AddShowFeature.addToShowTeam(teamMembers);
          AddShowFeature.updateKeyCreatives(showName);
        }
      }
      
      return true;
    } catch (error) {
      // Keep error logging for debugging purposes
      Logger.log('Error in updateShow:', error.toString());
      throw new Error('Failed to update show: ' + error.message);
    }
  }
};

// Global functions to be called from the HTML
function showSearchSidebar() {
  return SearchEditFeature.showSearchSidebar();
}

function searchShows(query) {
  return SearchEditFeature.searchShows(query);
}

function getShowDataAndShowDialog(rowIndex) {
  const show = SearchEditFeature.getShowData(rowIndex);
  const template = HtmlService.createTemplateFromFile('ShowEditForm');
  template.show = show;
  template.rowIndex = rowIndex;
  template.config = {
    networks: getOptionsFromSheet(DB_CONFIG.networkSheet),
    studios: getOptionsFromSheet(DB_CONFIG.studioSheet),
    genres: getOptionsFromSheet(DB_CONFIG.genreSheet),
    subgenres: getOptionsFromSheet(DB_CONFIG.subgenreSheet),
    sourceTypes: getOptionsFromSheet(DB_CONFIG.sourceTypeSheet),
    statusTypes: getOptionsFromSheet(DB_CONFIG.statusSheet),
    orderTypes: getOptionsFromSheet(DB_CONFIG.orderTypeSheet),
    roleTypes: getOptionsFromSheet(DB_CONFIG.roleTypeSheet)
  };
  const html = template.evaluate()
    .setWidth(800)
    .setHeight(600);
  SpreadsheetApp.getUi().showModalDialog(html, 'Edit Show: ' + show.show_name);
  return true;
}

function getOptionsFromSheet(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) return [];
  
  // Special handling for studio sheet to include aliases
  if (sheetName === DB_CONFIG.studioSheet) {
    // Headers: studio, type, parent_company, aliases
    const data = sheet.getDataRange().getValues();
    Logger.log('Studio sheet data:', JSON.stringify(data));
    
    return data
      .slice(1) // Skip header
      .filter(row => row[0]) // Only rows with studio names
      .map(row => row[0]) // Get studio names
      .sort(); // Sort alphabetically
  }
  
  // Default handling for other sheets
  return sheet.getDataRange().getValues().slice(1).map(row => row[0]);
}

function updateShow(rowIndex, formData) {
  return SearchEditFeature.updateShow(rowIndex, formData);
}
