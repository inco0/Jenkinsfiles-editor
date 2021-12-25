# Requirements: #

* Python 3
* `pip install GitPython`
              

# How to use: #

- Run the script and enter a directory with sub directories that contain a Jenkinsfile (strictly as of v1.0) and are git repositories.
- Enter two sed like regular expressions, an old and a new to automatically replace them in bulk while committing and pushing the changes to the corresponding repository.
