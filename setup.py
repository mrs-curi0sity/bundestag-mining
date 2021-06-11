import setuptools
setuptools.setup(
    name="Bundestag_Mining",
    version="1.0",
    author="Magdalena Aretz",
    author_email="aretzlena@gmail.com",
    description="",
    long_description_content_type="text/markdown",
    #package_dir={'':'src'},
    packages=['src'],
    install_requires=['numpy', 'pandas', 'dash', 'dash_html_components', 'dash-bootstrap-components']
)