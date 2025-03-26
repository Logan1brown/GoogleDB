"""Test multiple connection attempts to verify stability."""
import time
from pathlib import Path

from dashboard.utils.sheets_client import sheets_client
from config.logging_config import setup_logging

logger = setup_logging(__name__)

def test_connection(attempt: int) -> bool:
    """Test a single connection attempt."""
    try:
        logger.info(f"\nAttempt {attempt}: Starting connection test...")
        
        # Test shows data
        shows = sheets_client.get_shows_data()
        logger.info(f"✓ Successfully got {len(shows)} rows of show data")
        
        # Test team data
        team = sheets_client.get_team_data()
        logger.info(f"✓ Successfully got {len(team)} rows of team data")
        
        # Small delay to avoid rate limits
        time.sleep(2)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Attempt {attempt} failed: {str(e)}")
        return False

def main():
    """Run three connection tests."""
    logger.info("\n=== Starting Connection Stability Test ===\n")
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    successes = 0
    attempts = 3
    
    for i in range(1, attempts + 1):
        if test_connection(i):
            successes += 1
    
    logger.info(f"\nResults: {successes}/{attempts} successful connections")
    
    if successes == attempts:
        logger.info("✅ All connection attempts successful!")
        return 0
    else:
        logger.error("❌ Some connection attempts failed. Check logs/sheets_api.log for details")
        return 1

if __name__ == "__main__":
    exit(main())
