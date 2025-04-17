const DateTestFeature = {
  registerMenuItems: function(menu) {
    menu.addItem('Test Date Saving', 'showDateTest');
  },

  showForm: function() {
    const html = HtmlService.createHtmlOutputFromFile('DateTest')
      .setWidth(300)
      .setHeight(200);
    SpreadsheetApp.getUi().showModalDialog(html, 'Test Date Save');
  },

  saveDate: function(dateStr) {
    Logger.log('Received date:', dateStr);
    
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(DB_CONFIG.sheetName);
    
    if (!sheet) {
      throw new Error('Shows sheet not found');
    }

    // Get the last row
    const lastRow = sheet.getLastRow();
    
    // Find the date field index in DB_CONFIG.fields
    const dateFieldIndex = DB_CONFIG.fields.findIndex(f => f.name === 'announcementDate');
    if (dateFieldIndex === -1) {
      Logger.log('Available fields:', DB_CONFIG.fields);
      throw new Error('Could not find announcementDate in DB_CONFIG.fields');
    }
    
    // Column index is field index + 1 (since sheet is 1-based)
    const dateColIndex = dateFieldIndex + 1;
    Logger.log('Using column index:', dateColIndex);

    if (dateColIndex === 0) {
      throw new Error(`Column '${dateField.label}' not found in headers`);
    }

    // Add a new row with just the date
    sheet.getRange(lastRow + 1, dateColIndex).setValue(dateStr);
    Logger.log('Saved date:', dateStr, 'to row:', lastRow + 1);
  }
};

// Global functions to be called from the menu and HTML
function showDateTest() {
  DateTestFeature.showForm();
}

function saveDateTest(dateStr) {
  DateTestFeature.saveDate(dateStr);
}
