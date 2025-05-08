
from setuptools import setup, find_packages

setup(
    name="django-deep",  # Le nom du package
    version="0.1",  # La version du package
    packages=find_packages(),  # Détecte tous les modules dans django_deep/
    include_package_data=True,  # Inclut des fichiers supplémentaires définis dans MANIFEST.in
    install_requires=[  # Les dépendances nécessaires
        "Django>=3.2",  # Exemple: dépendance à une version de Django
    ],
    author="Ton Nom",
    author_email="ton.email@example.com",
    description="Django Enhanced Expression Parser for SQL filtering.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    url="https://github.com/toncompte/django-deep",  # Lien vers ton repo GitHub
)
