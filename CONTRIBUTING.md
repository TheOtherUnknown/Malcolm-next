# Malcom-next's Contributing Guidelines 
These guidelines give some guidance as to practices that should be followed when contributing to Malcolm-next. 

Overall, these practices are divided into 3 classes:
* Mandatory - Your PR will not be merged if you do not meet all of these requirements 
* Preferred - Be prepared to justify why any or all of these requirements were not met 
* Suggested - Meeting these requirements will overall be helpful, but may not be mentioned during review.

## Mandatory Practices 
* Your code must pass the flake8 linter with the following arguments: `flake8 --extend-ignore=E501,E401`
* All new commands must have a top level comment using triple quotes (`"""`) breifly explaining their use
* All new commands that accept paramaters must include the `usage=` argument in their decorator explaining the paramaters. See [an example here](https://github.com/TheOtherUnknown/Malcolm-next/blob/cb5583d4a355c68e490a0699ade3662543874b62/src/cogs/roles.py#L34)

## Preferred Practices 
* Your code should be formatted using the ypaf linter, ignoring options that violate flake8 linting 
* Variable names should be in snake_case unless they are constants
* The bot should never `bot.wait_for()` for more than 60 seconds
* If what your code does isn't immediately obvious, add a comment
* Helper methods (non-commands) should have a doc comment

## Suggested Practices 
* Command names should be as short as possible, and not shorter 
* Embeds are best used for complex output 