# MTG Card Search
### Authors:
Noah Scarbrough, Samuel Dunn


## Overview
This project contains our submission for CS483-Web Data's final project.

## Local Files
The project is located in the `mtg_qe` folder, which also serves as a packageable python module.
Within the `mtg_qe/` folder are subfolders that define specific components of the project.

- `mtg_qe/scraper` contains code specific to the data scraper
- `mtg_qe/data` contains code specific to preparing and - interfacing with the scraped data.
- `mtg_qe/site` contains code specific to hosting the website and interfacing with the backend (`mtg_qe/data`)
- `mtg_qe/model` contains code that defines how we interface with card data.
- `mtg_qe/utils` contains utiltiy code that was usesful in multiple points around the project.

### Helper scripts

In the top level directory there are three helper scripts.

The first is `run_scrape.py` which, true to its name, initiates a scraping sequence. It will be a go-to script in most developer environments.
This script has a command line interface help option to better describe its functionality.
After running it will output a scrape data archive (specified by the user), this can then be used with the next script.

`transform_data.py` will take the scraper output and build the indexes out of it.
Again, this script has commandline help options for a better description.

There is also `launch_site.py`, which will start the cherrypy session to host the website.
Once invoked, our website will be hosted on localhost, port 8080 (currently only serving to itself, not on `0.0.0.0` or any other network interface).

Once up, use a browser to navigate to `localhost:8080` or `127.0.0.1:8080`

### Other files
Here in the top level directory there are two other files of note.

There is an additional python file here, `setup.py`.
This file is used to build redistributable packages.
To use this script merely invoke it with the correct python interpreter and supply the argument `bdist_wheel`.

ex: `python3 setup.py bdist_wheel`

This will bundle everything into a `.whl` which `pip` can use to install the package.

Additionally, there is a file `corpus_v4.5_lite.tar.gz`.
This archive contains our indexes. To use it, it needs to be moved to `mtg_qe/data/`, where it will be automatically unpacked and used.

Note: you will need to move the corpus archive to `mtg_qe/data/` before using setup.py, otherwise the generated `.whl` will be incomplete and will have issues at destination.


`requirements.txt` defines the packages needed to run all components of the project.
Before attempting to use anything, we recommend setting up a virtual environment and installing its contents:
`pip install -r requirements.txt`
