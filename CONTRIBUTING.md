# Points of Contact:
Jason Walter - Electronics and Testing Subteam lead

Asher Anand - Data visualization task lead

# Issue tracking and version control
Issues (aka tickets) should be tracked via the spreadsheet in the google drive.
Version control is critical, and contributors should NOT be directly working on
the main branch. A separate, well named, branch should be created for each
issue. While working, be sure to merge in main regularly. Finally, make certain
to make a pull request when the issue is complete to have code reviewed by Jason
and/or Asher (put them down as reviewers). Again, contributors should NOT be
merging their branches back into main without pull request. 

# Code style
Code style is critical for readability. As a general rule, code is read more than written. Everything should have meaningful comments. Meaningful does not mean explaining what the code does. Contributors are expected to be able to parse the source code for anything they choose to work on. Rather, the comments should explain *why* code was written in a particular way. 

With regard to formatting, it is far simpler to rely on opinionated formatters than to require manual formatting by each contributor. The following should be used:

Python -> Black

Javascript/Typescript (in the context of Vue) -> Prettier

Note that these all have readily available VSCode extensions. 
