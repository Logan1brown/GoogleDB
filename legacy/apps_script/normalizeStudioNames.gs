function previewStudioNames() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const showsSheet = ss.getSheetByName('shows');
  const studiosRange = showsSheet.getRange('D2:D');
  const previewRange = showsSheet.getRange('N2:N');  // Write to column N instead
  const studios = studiosRange.getValues();
  
  const studioListSheet = ss.getSheetByName('studio_list');
  const studioData = studioListSheet.getDataRange().getValues();
  const canonicalNames = new Set();
  const aliasMap = new Map();
  
  // Skip header, build maps of valid names
  for (let i = 1; i < studioData.length; i++) {
    const [studio, type] = studioData[i];
    if (type === 'Studio') {
      canonicalNames.add(studio);
      
      // Process aliases if they exist
      const aliases = studioData[i][5]; // Column F (0-based)
      if (aliases) {
        aliases.split(',').forEach(alias => {
          aliasMap.set(alias.trim(), studio);
        });
      }
    }
  }
  
  const newValues = studios.map(row => {
    const input = row[0];
    if (!input) return [''];
    
    const normalizedStudios = input.split(',').map(studio => {
      const trimmed = studio.trim();
      
      // Check if canonical
      if (canonicalNames.has(trimmed)) {
        return trimmed;
      }
      
      // Check if alias
      if (aliasMap.has(trimmed)) {
        return aliasMap.get(trimmed);
      }
      
      // Not found
      return 'Other: ' + trimmed;
    });
    
    return [normalizedStudios.join(', ')];
  });
  
  previewRange.setValues(newValues);  // Write to column N for preview
}

function updateStudioNames() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const showsSheet = ss.getSheetByName('shows');
  const previewRange = showsSheet.getRange('N2:N');  // Read from column N
  const targetRange = showsSheet.getRange('D2:D');   // Write to column D
  
  // Copy values from preview to target
  const previewValues = previewRange.getValues();
  targetRange.setValues(previewValues);
  
  // Optional: Clear the preview column
  // previewRange.clearContent();
}
