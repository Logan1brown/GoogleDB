const MigrateRoles = {
  // Menu registration
  registerMenuItems: function(menu) {
    menu.addItem('Migrate Roles to Full Names', 'migrateRolesToFullNames');
  },

  // Get role mapping from role_types sheet
  getRoleMapping: function() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const roleSheet = ss.getSheetByName(DB_CONFIG.roleTypeSheet);
    
    if (!roleSheet) {
      throw new Error('Role types sheet not found');
    }
    
    // Get all role data
    const roleData = roleSheet.getDataRange().getValues();
    const roleMapping = new Map();
    
    // Skip header row
    for (let i = 1; i < roleData.length; i++) {
      const [fullName, category, aliases] = roleData[i];
      if (!fullName || !aliases) continue;
      
      // Split aliases by comma and clean up
      const aliasArray = aliases.split(',').map(a => a.trim().toLowerCase());
      
      // Add each alias to the mapping
      aliasArray.forEach(alias => {
        roleMapping.set(alias, fullName);
      });
      
      // Also map the full name to itself (case-insensitive)
      roleMapping.set(fullName.toLowerCase(), fullName);
    }
    
    return roleMapping;
  },

  // Convert abbreviated roles to full names
  expandRoles: function(roleString, roleMapping) {
    if (!roleString) return roleString;
    
    // Split roles by comma and clean up
    const roles = roleString.split(',').map(r => r.trim());
    
    // Convert each role
    const expandedRoles = roles.map(role => {
      const mappedRole = roleMapping.get(role.toLowerCase());
      return mappedRole || role; // Keep original if no mapping found
    });
    
    return expandedRoles.join(', ');
  },

  // Migrate all roles in show_team sheet
  migrateRoles: function() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(DB_CONFIG.showTeamSheet);
    
    if (!sheet) {
      throw new Error('Show team sheet not found');
    }
    
    // Get role mapping
    const roleMapping = this.getRoleMapping();
    
    // Get all data
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    
    // Find roles column
    const rolesCol = headers.indexOf('roles');
    if (rolesCol === -1) {
      throw new Error('Roles column not found');
    }
    
    // Track changes
    let changesCount = 0;
    const changes = [];
    
    // Update roles
    const updatedData = data.map((row, rowIndex) => {
      if (rowIndex === 0) return row; // Skip header
      
      const originalRoles = row[rolesCol];
      const expandedRoles = this.expandRoles(originalRoles, roleMapping);
      
      if (originalRoles !== expandedRoles) {
        changesCount++;
        changes.push({
          show: row[0], // show_name is first column
          name: row[1], // name is second column
          from: originalRoles,
          to: expandedRoles
        });
      }
      
      row[rolesCol] = expandedRoles;
      return row;
    });
    
    // Update sheet
    sheet.getRange(1, 1, updatedData.length, updatedData[0].length)
      .setValues(updatedData);
    
    // Show summary
    const ui = SpreadsheetApp.getUi();
    const message = `Migration complete!\n\nUpdated ${changesCount} roles.\n\nExample changes:\n${
      changes.slice(0, 5).map(c => 
        `${c.show} - ${c.name}:\n  From: ${c.from}\n  To: ${c.to}`
      ).join('\n\n')
    }${changes.length > 5 ? '\n\n...and more' : ''}`;
    
    ui.alert('Role Migration Complete', message, ui.ButtonSet.OK);
    
    // Return stats for logging
    return {
      totalUpdated: changesCount,
      changes: changes
    };
  }
};

// Global function to be called from menu
function migrateRolesToFullNames() {
  try {
    MigrateRoles.migrateRoles();
  } catch (error) {
    SpreadsheetApp.getUi().alert(
      'Error',
      'Failed to migrate roles: ' + error.message,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    console.error('Error in migrateRolesToFullNames:', error);
  }
}
