# How to contribute

## Introduction

First off, thank you for considering contributing to **QWeb**. We appreciate all kinds of contributions (reporting bugs/feature ideas, improving documentation, creating examples, fixing bugs). 

If you discover new issues or have ideas for improvements, please report them to the issue tracker of the repository. Follow the guidelines in [Issue reporting section](#Issue-reporting)

If you want to participate by improving keyword documentation, fixing bugs or creating new features, please follow the [other contributions](#other-contributions) section of the guideline.

Following these guidelines helps to make sure your contributions can be accepted and included to the project.

## Issue reporting

* Check that the issue has not already been reported.
* Be clear, concise and precise in your description of the problem.
* Open an issue using **Bug report** template. Include a descriptive title and a detailed summary
* Include your versions of:
    * Python (python --version)
    * Browser you used to reproduce the problem (i.e. Chrome/Firefox etc.)
    * Selenium webdriver version used (`chromedriver --version` or `geckodriver --version` etc.)
    * QWeb version you are using to reproduce the problem

In case of new feature/enhancement request, please open an issue using **Feature request** template. 

## Other contributions

We use GitHub flow, so all other contributions are handled by Pull Requests.

Note however, that new features (new keywords etc.) should be first discussed by opening an issue with **"Feature request"** template.

### Process overview

1. Fork the repo and create your branch from master.
2. Install dependencies
3. Make your changes. If you've changed keyword behavior, update keyword documentation (docstrings).
4. Ensure linting is run and does not give errors
5. Ensure the acceptance test suite passes on your platform.
6. Issue a pull request in GitHub.

New to GitHub or making open source contributions? There's an excellent [contributing to open source](http://www.contribution-guide.org/) guide which covers the basics in more detail.

#### Fork and create a branch

1. Click ‘Fork’ on Github, creating e.g. yourname/QWeb.
2. Clone your project to local machine: `git clone https://github.com/yourname/qweb.git`
3. Create a branch: `git checkout -b my_fix_for_foo`



#### Install dependencies

Install dependencies by issuing command:

```bash
pip install -r requirements.txt
```

...on repository root.

You should be all set up for making your changes now.

#### Before opening PR

Once you have made your changes, please validate the quality of your changes. Linting, unit tests and acceptance tests will be automatically run when you issue a new Pull Request, but to save everyone's time it is best to run these locally on your platform prior to issuing a PR.

#### Local development tasks

We use excellent [duty](https://github.com/pawamoy/duty) python package to run development tasks locally. You can see all defined development tasks with command:

```bash
duty --list
```

##### Linting
We use both *pylint* and *flake8* for linting. To run these locally, run:

```bash
duty lint
```

...on repo root.

##### Unit tests

We use **pytest** for unit tests. Unit tests are located in `/test/unit` folder. You can run unit test locally by running command:

```duty unit-tests```


##### Acceptance tests

We use **Robot Framework** for acceptance tests. Acceptance tests are located in `/test/acceptance` folder. You can run acceptance test locally by running command:

```duty acceptance-tests```

#### Commit, push and open a pull request

Once your contribution is final, commit your code and push it to your own repository. Then navigate back to https://github.com/yourname/QWeb and you should see a "Pull request" button. Create a new pull request.


### License

All contributions are under the same license as the rest of this project. See [LICENSE](./LICENSE)

