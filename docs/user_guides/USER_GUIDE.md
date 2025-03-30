# TV Series Database User Guide

## Getting Started

### Accessing the Database
1. Open the Google Sheet containing the TV Series Database
2. Make sure you're on the "shows" sheet to use any of the features
3. The menu bar will contain three main options:
   - Add New Show
   - Search Shows
   - Edit Team Members

## Adding a New Show

1. Navigate to the "shows" sheet
2. Click "Add New Show" in the menu
3. Fill out the form with the show's details:
   - Show Name (required - but can use placeholder)
   - Network (required)
   - Studios (required)
   - Genre/Subgenre (optional)
   - Status (optional)
   - Order Type (optional)
   - Episode Count (optional)
   - Dates (optional)
4. Add team members (optional):
   - Enter the team member's name
   - Select their role from the dropdown
   - Click "Add" to add them to the show
5. Click "Save" to add the show to the database

## Searching Shows

1. Navigate to the "shows" sheet
2. Click "Search Shows" in the menu
3. Use the search bar to find shows by:
   - Show name
   - Network
   - Studios
   - Genre
   - Status
4. The results will update as you type
5. Click on a show in the results to view its full details

## Managing Team Members

1. Navigate to the "shows" sheet
2. Click "Edit Team Members" in the menu
3. The sidebar will show team members for the currently selected show
4. To add a team member:
   - Click "Add Team Member"
   - Enter their name
   - Select their role from the dropdown
   - Click "Save"
5. To edit a team member:
   - Change their name directly in the text field
   - Add additional roles using the role dropdown
   - Remove roles by clicking the "×" next to each role
6. To remove a team member:
   - Click the "Remove" button next to their name
   - Confirm the removal when prompted

## Important Notes

### Data Entry
- Always use the provided forms and sidebars to add or edit data
- Don't modify the `key_creatives` column directly; it updates automatically
- Use the dropdown menus to ensure consistent data entry

### Sheet Navigation
- All features (Add, Search, Edit) only work when you're on the "shows" sheet
- If you try to use a feature on the wrong sheet, you'll be prompted to switch
- The database uses multiple sheets for different purposes:
  - `shows`: Main data table
  - `show_team`: Team member data
  - Various lookup tables for networks, studios, genres, etc.

### Loading States
- When performing operations, you'll see a loading indicator
- The interface will be temporarily disabled while changes are being processed
- Wait for the operation to complete before making additional changes

## Troubleshooting

### Common Issues
1. **Feature not working**
   - Make sure you're on the "shows" sheet
   - Try refreshing the page

2. **Team members not showing**
   - Select a row in the shows sheet
   - Try closing and reopening the Edit Team Members sidebar

3. **Dropdowns empty**
   - Check that you're connected to the sheet
   - Refresh the page

## Tips & Tricks

### Keyboard Shortcuts
1. **Quick Navigation**
   - `Ctrl/Cmd + F`: Open search sidebar
   - `Esc`: Close any sidebar
   - Arrow keys: Navigate between cells
   - `Enter`: Select a row

2. **Efficient Data Entry**
   - `Tab`: Move to next field in forms
   - `Shift + Tab`: Move to previous field
   - `Enter`: Submit forms
   - `Esc`: Cancel/close forms

### Best Practices
1. **Working with Team Members**
   - Add team members right after creating a new show
   - Group similar roles together (e.g., all writers, then all producers)
   - Double-check roles before saving

2. **Searching Efficiently**
   - Use partial words to find matches (e.g., "com" for "comedy")
   - Search by studio name to find all shows from a studio
   - Search by network to find all shows on a network

3. **Data Organization**
   - Keep the shows sheet sorted by show name for easier browsing
   - Use filters to quickly find specific categories
   - Regularly check team member assignments for accuracy

## Permissions & Access

### First-Time Access
When you first use the database features, you'll need to:
1. Make sure you have Editor access to the sheet
2. Authorize the database script when prompted
3. Review and accept the permissions the script needs

### Permission Levels
- **Viewers**: Can only view the sheet data
- **Commenters**: Can view and comment on data
- **Editors**: Can use all features including:
  - Adding new shows
  - Searching the database
  - Managing team members

### Security Prompts
- You may see security warnings about the script
- This is normal for any Google Apps Script
- The script only needs access to:
  - Modify the current spreadsheet
  - Display dialogs and sidebars
  - Create custom menus

### Getting Help
If you encounter any issues not covered in this guide:
1. Check that you're following the steps exactly
2. Try refreshing the page
3. Contact your system administrator if you:
   - Don't see the custom menu
   - Can't authorize the script
   - Need different permission levels

Last updated: March 26, 2025
