episode_prompt_tpl="""Summarize this AFL video transcript covering all the critical highlights in NOT more than 400 characters. Just return the synopsis. No need to mention this is the summary and these are the highlights
Transcript:
$ctext
Answer:
"""

headline_prompt_tpl="""For this AFL video transcript, generate 3 eye-catching and news worthy headlines
Transcript:
$ctext
The 3 most compelling headlines are:
"""

theme_prompt_tpl = """In this AFL video transcript, what are the qualitative descriptors? 
* Each of them should have a maximum length of 3 words only.
* Output the descriptors as a list
* No extra sentences in the output
AFL Video Transcript:
$ctext
The important qualitative descriptors discussed are:
- ...
- ..."""

player_prompt_tpl = """For the AFL Video transcript below, identify the Players (with their Official name) and the teams (with their Official name) they are playing for currently.
* Find out the official name of the player. e.g for a player named Travis Boak, official name is Travis Boak 
* Find out the official name of the team they are playing currently. e.g for Bulldogs team, official name is Western Bulldogs Football Club
* Output format
(correct_official_player_name, correct_official_team_name)
(correct_official_player_name, correct_official_team_name)
* Always check if you are responding in the format above and ensure that the person is a Player currently and not a Coach.

Transcript:
$ctext
Tuples:
"""

coach_prompt_tpl = """For the AFL Video transcript below, identify the Coaches (with their Official name) and the teams (with their Official name) they are Coaching to right now.
* Find out the official name of the Coach. e.g for a player named John Doe, official name is John Doe 
* Find out the official name of the team they are coaching currently. e.g for Bulldogs team, official name is Western Bulldogs Football Club
* Output format
(correct_official_coach_name, correct_official_team_name)
(correct_official_coach_name, correct_official_team_name)
* Always check if you are responding in the format above and ensure that the person is a Coach and not a Player currently.

Transcript:
$ctext
Tuples:
"""

predictions_prompt_tpl = """What futuristic predictions (NOT PAST EVENTS) can you extract from this Australian Football League Transcript below
1. Output should be a list of predictions in this format without any prefixes
- prediction
- prediction
2. Double check to see if you have included any past events. If so, discard them. Thats not a prediction.
Remember to understand the context fully, consider different references to predictions/predictors, avoid skipping or missing information, eliminate duplicates, include only relevant information, and adhere to the specified format.

Transcript:
$ctext
Tuples:
"""