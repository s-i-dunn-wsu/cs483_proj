from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="mtg_qe",
        version="0.1.0",
        author="Noah Scarbrough, Samuel Dunn",
        author_email="samuel.i.dunn@wsu.edu",
        description="magic the gathering card search, for CS483",
        packages=find_packages(),
        install_requires=['whoosh'],
        entry_points={
            'console_scripts': [
                'mtg_qe_setup_index = mtg_qe.data.index_setup:cli_entry',
                'mtg_qe_scrape = mtg_qe.scraper.cli_entry'
            ]
        },
        package_data={
            'mtg_qe.data': ['*.tar.gz']
        },
        setup_requires=['wheel']
    )