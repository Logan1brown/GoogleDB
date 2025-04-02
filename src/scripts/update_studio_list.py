"""Script to update the studio list CSV file."""
import pandas as pd
from pathlib import Path

def add_major_studios():
    """Add major studios to the lookup table."""
    sheets_dir = Path(__file__).parents[2] / "docs" / "sheets"
    csv_path = sheets_dir / "STS Sales Database - studio_list_2.csv"
    
    # Read existing data, preserving comments
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert new studios
    large_indies_end = -1
    for i, line in enumerate(lines):
        if line.strip() == "## Mid-Size Indies":
            large_indies_end = i
            break
    
    if large_indies_end == -1:
        print("Could not find Large Indies section")
        return
    
    # Add Sony Pictures Television
    sony_line = 'Sony Pictures Television,Studio,Sony,,,,"Sony TV,SPT,TriStar Television","Independent,Large",true\n'
    lines.insert(large_indies_end, sony_line)
    
    # Write back to file
    with open(csv_path, 'w') as f:
        f.writelines(lines)
    
    print("Added Sony Pictures Television to Large Indies section")

if __name__ == "__main__":
    add_major_studios()
