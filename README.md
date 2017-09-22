# LearnPDF
Download files off Learn from the command line. 

---

Learn is a website that University of Canterbury lecturers can share resources with students. It hosts 

* Homework
* Lecture Notes

and other helpful resources. 

The problem is that the design sucks. PDF's are opened in small boxes on the webpage, meaning students have to download files to view them in full screen. Download folders get very cluttered this way, causing files to be downloaded multiple times. 

LearnPDF says 'hell no' to the Learn website, instead downloading every file on learn to a local folder. This means students can browse all the resources of learn in the comfort of their own file browser.


## Requirements

* Python 3
* Requests

## Installation

1. Clone 

```
git clone https://github.com/liamdiprose/LearnPDF.git
```

## Usage
LearnPDF is simple, most people will only have to type `./main.py` to get started. If you have other requirements, they might be listed below (and if they aren't, post an issue!)

### Running normally

```
./main.py <directoy>
```

LearnPDF will prompt you for your login details and download all files to `<directory>`. If you don't specify one, it will default to `learn/`.

### Only one filetype
```
./main.py --only pdf,doc,txt
```

Will only download `*.pdf`, `.doc`, and `.txt` files.

### Ignore certain filetypes
Sometimes lecturers will post videos on Learn, which are huge. Here's how you would ignore them
```
./main.py --ignore mp4,avi,mkv
```

Will skip `.mp4`, `.avi` and `.mkv` files.

 
