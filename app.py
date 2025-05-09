#!/usr/bin/env python3
# Changed shebang for better portability
import shutil # Not used, but kept if you plan to use it. Consider removing if not.
import os
import time
from bs4 import BeautifulSoup
import requests
import csv
import copy # Potentially removable, see notes
from tabulate import tabulate
# import emojis # Not used, removed
from wcwidth import wcswidth # wcwidth itself wasn't directly used, only wcswidth

# --- Configuration ---
TRUNCATE_WIDTH = 48  # Standard Python naming convention (UPPER_CASE for constants)
TEAM_CUTOFF = 18
REFRESH_RATE = 10  # Seconds

# --- Helper Functions ---
def center_with_wide_chars(text, width, fillchar=' '):
    """Centers text within a given width, accounting for wide characters."""
    text_width = wcswidth(text)
    if text_width >= width:
        return text

    total_padding = width - text_width
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding

    return f"{fillchar * left_padding}{text}{fillchar * right_padding}"

def get_on_site_teams():
    """
    Reads team names from 'teams.csv'.
    Skips the header row and truncates team names.
    """
    on_site_teams = []
    try:
        with open('teams.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            try:
                next(reader)  # Skip header row
            except StopIteration:
                print("Warning: 'teams.csv' is empty or contains only a header.")
                return [] # CSV is empty or only has a header

            for row in reader:
                if len(row) > 1 and row[2].strip():  # Check if second column exists and is not empty
                    team_name = row[2].strip()[:TRUNCATE_WIDTH]
                    on_site_teams.append(team_name)
    except FileNotFoundError:
        print("Error: 'teams.csv' not found. No on-site teams will be filtered.")
        # Depending on requirements, you might want to exit or raise an error
    except Exception as e:
        print(f"Error reading 'teams.csv': {e}")
    # __import__('pprint').pprint(on_site_teams)
    # exit(0)
    return on_site_teams

def get_scoreboard():
    """
    Fetches and parses scoreboard data from the specified URL.
    Returns a list of [team_name, points] or None on error.
    Team names are cleaned and truncated.
    """
    url = "https://bts.wh.edu.pl/scoreboard"
    scoreboard_data = []
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4XX or 5XX)
        html_content = response.text # Use .text for requests to handle initial decoding
        # print(html_content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching scoreboard: {e}")
        return None # Indicate failure

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="table table-striped") # Correct class attribute for BeautifulSoup

    if not table:
        print("Warning: Scoreboard table not found on the page.")
        return None
    table_body = table.find('tbody')
    if not table_body:
        print("Warning: Scoreboard table body (tbody) not found.")
        return None

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2: # Expecting at least two columns (Team, Points)
            # Clean and truncate team name
            team_name_raw = cols[0].text
            # print(team_name_raw)
            
            team_name = team_name_raw.strip()[:TRUNCATE_WIDTH]
            # print(team_name_raw.strip())
            points = cols[1].text.strip()
            scoreboard_data.append([team_name, points])
            # print([team_name, points])

        # else:
            # print(f"Skipping row with insufficient columns: {[c.text.strip() for c in cols]}")
    # __import__('pprint').pprint(scoreboard_data)
    return scoreboard_data

# --- Main Application Logic ---
def run():
    """Main loop to fetch, process, and display the scoreboard."""
    on_site_teams_list = get_on_site_teams()
    if not on_site_teams_list:
        # This message is now more of a warning if the file was found but empty,
        # or an error if the file wasn't found (handled in get_on_site_teams)
        print("Continuing without on-site team filtering or with an empty list from CSV.")


    table_headers = ["PLACE", "TEAM", "POINTS"]
    display_title = "ON SITE SCOREBOARD"

    # State variables
    current_on_site_scoreboard_data = [] # Stores [['Team Name', 'Points'], ...]
    last_displayed_content_for_resize = "" # Stores "TITLE\nTABLE_STRING" for quick redraw on resize

    try:
        terminal_columns = os.get_terminal_size().columns
    except OSError: # Happens if not in a real terminal (e.g., piped output)
        print("Warning: Could not detect terminal size. Defaulting to 80 columns.")
        terminal_columns = 80  # Default width
    previous_terminal_columns = terminal_columns

    last_refresh_time = 0  # Force initial refresh

    while True:
        needs_redraw = False
        current_time = time.time()

        # 1. Check for terminal resize
        try:
            current_terminal_cols = os.get_terminal_size().columns
        except OSError:
            current_terminal_cols = terminal_columns # Use last known or default

        if current_terminal_cols != previous_terminal_columns:
            terminal_columns = current_terminal_cols
            previous_terminal_columns = current_terminal_cols
            if last_displayed_content_for_resize: # Only force redraw if there's something to redraw
                needs_redraw = True

        # 2. Fetch new data if refresh interval passed
        if current_time - last_refresh_time >= REFRESH_RATE:
            last_refresh_time = current_time
            all_teams_data = get_scoreboard() # Returns list of [name, points] or None

            if all_teams_data is not None:
                # Filter for on-site teams.
                # Team names in all_teams_data are already truncated by get_scoreboard().
                # Team names in on_site_teams_list are already truncated by get_on_site_teams().
                new_filtered_data = [
                    team_info for team_info in all_teams_data
                    if team_info[0] in on_site_teams_list
                ]

                if new_filtered_data != current_on_site_scoreboard_data:
                    current_on_site_scoreboard_data = new_filtered_data
                    # Data changed, so a redraw is needed.
                    # new_filtered_data is a new list from list comprehension, so direct assignment is fine.
                    # copy.deepcopy isn't strictly needed here unless sub-elements were complex mutable objects
                    # that were modified elsewhere. Strings are immutable.
                    needs_redraw = True
            else:
                # get_scoreboard() returned None (an error occurred)
                # We'll allow redraw if terminal resized, or if nothing ever shown.
                if not last_displayed_content_for_resize: # Nothing ever shown
                    # Clear screen and print a temporary message
                    error_message = "Fetching scoreboard data..." # Could also be "Error fetching..."
                    centered_error = center_with_wide_chars(error_message, terminal_columns)
                    # ANSI clear screen and move to home
                    print(f"{chr(27)}[2J{chr(27)}[H{centered_error}", end='', flush=True)
                    # No valid data to form last_displayed_content_for_resize yet
                # If there was previous data, a resize (needs_redraw=True) will redraw it.
                # Otherwise, if no resize and data fetch fails, we do nothing new.

        # 3. Redraw if data changed or terminal resized
        if needs_redraw:
            # Prepare data for tabulate: add place numbers
            # current_on_site_scoreboard_data is the source of truth now
            display_list_with_place = []
            for index, team_info in enumerate(current_on_site_scoreboard_data):
                # team_info is like ['Team Name', 'Points']
                # Create a new list for each row to avoid modifying original data
                display_list_with_place.append([index + 1] + team_info)

            final_table_data_for_display = display_list_with_place[:TEAM_CUTOFF]

            table_string = tabulate(final_table_data_for_display, table_headers, tablefmt="rounded_grid")

            # Store the uncentered logical content for potential future re-centering on resize
            last_displayed_content_for_resize = f"{display_title}\n{table_string}"

            # Build the output string for printing
            output_lines = [
                f"{chr(27)}[2J{chr(27)}[H"+ # ANSI clear screen and move cursor to home
                center_with_wide_chars(display_title, terminal_columns)
            ]
            # print(table_string)
            # exit(0)
            # print("gownp")
            # print("\n".join(output_lines), end='', flush=True)
            # # print(output_lines)
            # exit(0)
            
            for line in table_string.split("\n"):
                print(line)
                output_lines.append(center_with_wide_chars(line, terminal_columns))

            # print(output_lines)
            # __import__('pprint').pprint(output_lines)
            # exit(0)
            print("\n".join(output_lines), end='', flush=True)


        # Prevent tight loop if nothing happens, also allows Ctrl+C to interrupt
        time.sleep(0.1)

if __name__ == "__main__":
        run()
