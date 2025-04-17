/**
 * Syncs success scores from tmdb_success_metrics to shows sheet
 */
function onTMDBMetricsUpdate(e) {
  // Skip check if running manually (no event)
  if (e && e.source.getActiveSheet().getName() !== 'tmdb_success_metrics') {
    return;
  }
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const metricsSheet = ss.getSheetByName('tmdb_success_metrics');
  const showsSheet = ss.getSheetByName('shows');

  // Get all data
  const metricsData = metricsSheet.getDataRange().getValues();
  const showsData = showsSheet.getDataRange().getValues();

  // Get column indices
  const metricsHeaders = metricsData[0];
  const showsHeaders = showsData[0];
  
  Logger.log('Metrics headers:', metricsHeaders);
  Logger.log('Shows headers:', showsHeaders);
  
  const metricsIdCol = metricsHeaders.indexOf('TMDB_ID');
  const metricsScoreCol = metricsHeaders.indexOf('success_score');
  const showsIdCol = showsHeaders.indexOf('TMDB_ID');
  const showsScoreCol = showsHeaders.indexOf('success_score');
  
  Logger.log(`Column indices - Metrics: ID=${metricsIdCol}, Score=${metricsScoreCol}`);
  Logger.log(`Column indices - Shows: ID=${showsIdCol}, Score=${showsScoreCol}`);

  if (metricsIdCol === -1 || metricsScoreCol === -1 || showsIdCol === -1 || showsScoreCol === -1) {
    Logger.log('Required columns not found');
    return;
  }

  // Create lookup of TMDB_ID to success_score
  const scoreMap = {};
  for (let i = 1; i < metricsData.length; i++) {
    const row = metricsData[i];
    const id = row[metricsIdCol];
    const score = row[metricsScoreCol];
    if (id && score !== undefined) {
      scoreMap[id] = score;
    }
  }

  // Update shows sheet
  let updates = 0;
  for (let i = 1; i < showsData.length; i++) {
    const row = showsData[i];
    const id = row[showsIdCol];
    if (id && scoreMap[id] !== undefined) {
      const newScore = scoreMap[id];
      const currentScore = row[showsScoreCol];
      Logger.log(`Row ${i+1}: ID ${id} - New Score: ${newScore} (${typeof newScore}), Current Score: ${currentScore} (${typeof currentScore})`);
      if (Number(newScore) !== Number(currentScore)) {
        showsSheet.getRange(i + 1, showsScoreCol + 1).setValue(Number(newScore));
        updates++;
      }
    }
  }

  Logger.log(`Updated ${updates} success scores`);
}

/**
 * Creates a trigger to run when the tmdb_success_metrics sheet is edited
 */
function createTrigger() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const metricsSheet = ss.getSheetByName('tmdb_success_metrics');
  
  // Remove any existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'onTMDBMetricsUpdate') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // Create new trigger
  ScriptApp.newTrigger('onTMDBMetricsUpdate')
    .forSpreadsheet(ss)
    .onEdit()
    .create();
  
  Logger.log('Trigger created successfully');
}
