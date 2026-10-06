text
Started: 2026-10-06 21:03 CEST
Stopped: 2026-10-06 23:03 CEST


- **What I built**
I created a server that can accept an HTTP GET request and return the desired portfolio data. I also created a Panel interface so a non-technical user can interact with it. The data is loaded into a pandas DataFrame when the server starts, which is more efficient than reading the CSV files on every request. I used Claude sonnet 5.5. I am new to AI so I do not have an "AI-Config" file. I tried to verify most of the code. Especially the loss_experience file since it includes the most important functionality.

- **What I deliberately did not build, and why**
I wanted to do it all but because of the timeconstraints I was not able to. Ideally I should have focused on point 2 (comparing the portfolios) since this is what I see as the most valuable information that is provided when presenting the data in this way. That is you would be able to know how you should structure or restructure your portfolio given the data from the others. I should also add some tests so that I can be certain that everything is correct.

- **What I would do first with another day**
Point 2 for reasons described above. 
