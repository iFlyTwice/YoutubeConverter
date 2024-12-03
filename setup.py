from setuptools import setup, find_packages

setup(
    name="YoutubeConverter",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'customtkinter',
        'yt-dlp',
        'Pillow',
        'selenium',
        'webdriver_manager',
        'requests',
        'pycryptodome'
    ]
)
