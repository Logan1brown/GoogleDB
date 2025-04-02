// Automatically update show names in show_team when they change in shows
function onEdit(e) {
  Logger.log('onEdit triggered');
  Logger.log('Event object:', e);

  // Only run if editing the shows sheet
  const sheetName = e.source.getActiveSheet().getName();
  Logger.log('Sheet name:', sheetName);
  if (sheetName !== 'shows') return;
  
  // Only run if editing column A (show names)
  const column = e.range.getColumn();
  Logger.log('Column edited:', column);
  if (column !== 1) return;
  
  // Only run if editing below the header row
  const row = e.range.getRow();
  Logger.log('Row edited:', row);
  if (row <= 1) return;
  
  // Get the old and new values
  const oldValue = e.oldValue;
  const newValue = e.value;
  
  // If no old value, this is a new show
  if (!oldValue) return;
  
  // Get the show_team sheet
  const ss = e.source;
  const teamSheet = ss.getSheetByName('show_team');
  if (!teamSheet) return;
  
  // Find all instances of the old show name in show_team
  const teamData = teamSheet.getRange('A2:A' + teamSheet.getLastRow()).getValues();
  const rowsToUpdate = [];
  
  teamData.forEach((row, index) => {
    if (row[0] === oldValue) {
      rowsToUpdate.push(index + 2); // +2 because we started at row 2
    }
  });
  
  // Update all instances to the new show name
  rowsToUpdate.forEach(row => {
    teamSheet.getRange('A' + row).setValue(newValue);
  });
  
  // If any rows were updated, show a notification
  if (rowsToUpdate.length > 0) {
    const ui = SpreadsheetApp.getUi();
    ui.alert(
      'Show Name Updated',
      `Updated ${rowsToUpdate.length} team member${rowsToUpdate.length === 1 ? '' : 's'} from "${oldValue}" to "${newValue}"`,
      ui.ButtonSet.OK
    );
  }
}
