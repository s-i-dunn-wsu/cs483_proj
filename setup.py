from setuptools import find_packages, setup
import os

if __name__ == "__main__":

    setup(
        name="mtg_qe",
        version="0.1.0",
        author="Noah Scarbrough, Samuel Dunn",
        author_email="samuel.i.dunn@wsu.edu",
        description="magic the gathering card search, for CS483",
        packages=find_packages(),
        install_requires=['whoosh', 'cherrypy', 'jinja2'],
        entry_points={
            'console_scripts': [
                'mtg_qe = mtg_qe.site.main:main',
                'mtg_qe_setup_index = mtg_qe.data.index_setup:cli_entry',
                'mtg_qe_scrape = mtg_qe.scraper:cli_entry',
                'mtg_qe_unpack = mtg_qe.data:unpack_archive'
            ]
        },
        package_data={
            'mtg_qe.data': ['corpus_files/*']
        },
        setup_requires=['wheel']
    )