# FyreWatch
A simple tool that returns a fire weather report for the CA South Ops region.

Dependencies:
pip install bs4 // Beautiful soup 4 -  HTML Parser
pip install requests // Python URL encoding, response handling, and session maintenance for scraper component.

After running dependencies, scrapes NIFC database to gather preparedness levels. Correlates local fire department info with local fire danger in a whimsical GUI. Prints out fire weather report in the shell. To toggle the shell print-out and see only the GUI, reassign _DEBUG_OUTPUT.



