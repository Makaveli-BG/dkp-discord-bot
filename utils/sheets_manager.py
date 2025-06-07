# utils/sheets_manager.py
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger("dkp_bot.sheets")

class SheetsManager:
    def __init__(self, credentials_file, sheet_id, worksheet_name="Discord-Bot"):
        """Initialize the Sheets Manager with Google Sheets API credentials"""
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name
        self._connect()
        
    def _connect(self):
        """Establish connection to Google Sheets API"""
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(self.sheet_id).worksheet(self.worksheet_name)
            logger.info("Successfully connected to Google Sheets")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
            
    def _refresh_connection(self):
        """Refresh connection to avoid timeout issues"""
        try:
            self._connect()
        except Exception as e:
            logger.error(f"Failed to refresh connection: {e}")
            
    def link_user(self, user_id, discord_user):
        """Link a user ID to a Discord user"""
        try:
            self._refresh_connection()
            records = self.sheet.get_all_records()
            
            # Get the header row to find column indices
            header_row = self.sheet.row_values(1)
            id_col = None
            discord_id_col = None
            
            # Find the ID and Discord ID columns
            for i, header in enumerate(header_row):
                if header == 'ID':
                    id_col = i + 1  # +1 for 1-indexing in gspread
                elif header == 'Discord ID':
                    discord_id_col = i + 1  # +1 for 1-indexing in gspread
            
            if id_col is None or discord_id_col is None:
                logger.error("Required columns not found in sheet")
                return {'status': 'columns_not_found'}
            
            # Check if this Discord user is already linked
            for record in records:
                if record.get('Discord ID', '') == discord_user:
                    return {
                        'status': 'already_linked',
                        'id': record.get('ID', '')
                    }
            
            # Check if the provided user ID exists and is not already linked
            for i, record in enumerate(records):
                if str(record.get('ID', '')) == user_id:
                    if record.get('Discord ID', ''):
                        return {'status': 'id_in_use'}
                    
                    # Link the user
                    self.sheet.update_cell(i + 2, discord_id_col, discord_user)  # +2 because of header and 1-indexing
                    return {'status': 'success'}
                    
            return {'status': 'not_found'}
        except Exception as e:
            logger.error(f"Error linking user: {e}")
            raise
            
    def unlink_user(self, discord_user):
        """Unlink a Discord user from their ID"""
        try:
            self._refresh_connection()
            records = self.sheet.get_all_records()
            
            # Get the header row to find the Discord ID column index
            header_row = self.sheet.row_values(1)
            discord_id_col = None
            
            # Find the Discord ID column
            for i, header in enumerate(header_row):
                if header == 'Discord ID':
                    discord_id_col = i + 1  # +1 for 1-indexing in gspread
                    break
            
            if discord_id_col is None:
                logger.error("Discord ID column not found in sheet")
                return {'status': 'column_not_found'}
            
            for i, record in enumerate(records):
                if record.get('Discord ID', '') == discord_user:
                    self.sheet.update_cell(i + 2, discord_id_col, "")  # +2 because of header and 1-indexing
                    return {'status': 'success'}
                    
            return {'status': 'not_found'}
        except Exception as e:
            logger.error(f"Error unlinking user: {e}")
            raise
            
    def get_user_stats(self, discord_user):
        """Get statistics for a Discord user"""
        try:
            self._refresh_connection()
            records = self.sheet.get_all_records()
            
            for record in records:
                if record.get('Discord ID', '') == discord_user:
                    return record
                    
            return None
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise
            
    def get_top_players(self, limit=10):
        """Get the top players by DKP score"""
        try:
            self._refresh_connection()
            records = self.sheet.get_all_records()
            
            # Convert DKP scores to integers for proper sorting
            for record in records:
                try:
                    dkp_score = record.get('DKP SCORE', '0')
                    if isinstance(dkp_score, str):
                        record['DKP SCORE'] = int(dkp_score.replace(',', ''))
                except (ValueError, TypeError):
                    record['DKP SCORE'] = 0
            
            # Sort by DKP score in descending order
            sorted_records = sorted(records, key=lambda x: x.get('DKP SCORE', 0), reverse=True)
            
            # Return the top N players
            return sorted_records[:limit]
        except Exception as e:
            logger.error(f"Error getting top players: {e}")
            raise
            
    def get_all_players(self):
        """Get all players data"""
        try:
            self._refresh_connection()
            return self.sheet.get_all_records()
        except Exception as e:
            logger.error(f"Error getting all players: {e}")
            raise