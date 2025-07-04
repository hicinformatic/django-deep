from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    author="hicinformatic",
    author_email="hicinformatic@gmail.com",
    name="django-deep",  # Le nom du package
    version="0.1",  # La version du package
    packages=find_packages(),  # Détecte tous les modules dans django_deep/
    include_package_data=True,  # Inclut des fichiers supplémentaires définis dans MANIFEST.in
    install_requires=[  # Les dépendances nécessaires
        "Django>=3.2",  # Exemple: dépendance à une version de Django
    ],
    description="Django Enhanced Expression Parser for SQL filtering.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU General Public License v3 (GPLv3)",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    url="https://github.com/hicinformatic/django-deep",  # Lien vers ton repo GitHub
)
