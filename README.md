# LearnPDF
### Download PDF files off the UC Learn webpage.

Now with 20% less leaked passwords!

## Why?
Learn is a great resource, but it often clumbersome to download PDF files. The amount of seperate pages you need to wade through is far to many.

And thats why this script exists; to download all the PDFs for you. 

## How?
[Windows Instructions](https://github.com/liamdiprose/LearnPDF/blob/master/WindowsInstallation.md)

Python 3 is used in this project, which means you'll need Python 3 installed on your system, along with these modules:

* Requests
* BeauitfulSoup4  

Finally, youll need to download this project, 

`git clone https://github.com/liamdiprose/LearnPDF.git`

[ZIP File](https://github.com/liamdiprose/LearnPDF/archive/master.zip)

## Usage
Once you have downloaded the project, move into the root directory, and run the `main.py` script

`python3 main.py`

It will prompt you for a username and password, and then will slowly download all the PDF files avaible to you.

Your username and password is never stored on the disk, however, a authentication cookie will be saved.

## It Broke...
Yep, itll do that. This is still early in development, and theres alot of cases where the program still breaks. You could be nice and add the problem to the error tracker [here](https://github.com/liamdiprose/LearnPDF/issues).

## Suggestions
Suggestions and Improvements are appreciated, you can suggest in the issue tracker. Or even better, add the improvements yourself, and send a pull request.
