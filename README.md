# Wikisource to LaTeX

Wikisource to LaTex is a Python program that I am writing to parse the [_Pentagon Papers_](http://en.wikisource.org/wiki/United_States_%E2%80%93_Vietnam_Relations,_1945%E2%80%931967:_A_Study_Prepared_by_the_Department_of_Defense) from Wikisource into a nicely-formatted LaTeX document.

Although you should feel free to reuse it as you like, this code will be pretty specific to the way the _Pentagon Papers_ document is being formatted on Wikisource.

__Author:__ Molly White<br />
__License:__ [MIT](http://opensource.org/licenses/MIT)

##Dependencies
Wikisource-to-LaTeX depends on [PLY](http://www.dabeaz.com/ply/) for the lexer. Download this and add it to the source path.

##Details

Given the first page of a Wikisource document (in this case, [United States – Vietnam Relations, 1945–1967: A Study Prepared by the Department of Defense/Front matter](http://en.wikisource.org/wiki/United_States_%E2%80%93_Vietnam_Relations,_1945%E2%80%931967:_A_Study_Prepared_by_the_Department_of_Defense/Front_matter)), this program traverses through the document, compiling for each page a list of the included source pages. Using these lists, it then queries the Wikisource API to pull in the content of these pages (in JSON format), which it compiles into text files in the `/raw` folder. It then strips the JSON-formatted text of extraneous information, saving these files in the `/text` folder. There are multiple source pages per text file, but this function verifies that they all come out in the correct order.

Once the text is pulled in, the parsing can begin! The program traverses through each text file and parses through it, saving the LaTeX-formatted files to the `/latex` folder. To perform the parsing, the program uses lex to generate a token stream. This is fed to a parser that I wrote by hand (as I find yacc is not particularly necessary for this.)
