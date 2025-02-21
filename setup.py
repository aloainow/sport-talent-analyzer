from setuptools import setup, find_packages

setup(
    name="sport-talent-analyzer",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit>=1.24.0',
        'streamlit-option-menu>=0.3.2',
        'plotly>=5.13.0',
        'numpy>=1.24.2',
        'pandas>=2.0.0',
    ],
)
