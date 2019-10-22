import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='InstaBot',
      version='0.1',
      description='Bot for https://instagram.com',
      author='dawa',
      author_email='dawa_@hotmail.fr',
      long_description = long_description,
      long_description_content_type="text/markdown",
      # url="my github project url",
      license='MIT',
      packages=setuptools.find_packages(),
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
      python_requires='>=3.7',
      entry_points={"console_scripts": ["instabot = instabot.__main__:main"]},
      )
