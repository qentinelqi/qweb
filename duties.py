"""Run dev tasks locally"""
import sys
from platform import system
from duty import duty

python_exe = sys.executable

@duty
def typing(ctx, path="QWeb"):
    """
    Check code typing
    Arguments:
        ctx: The context instance (passed automatically)
        path: path of folder/file to check
    """
    ctx.run(f"{python_exe} -m mypy --show-error-codes {path}", title="Checking code typing", capture=False)

@duty
def lint(ctx, path="QWeb"):
    """
    Check code quality
    Arguments:
        ctx: The context instance (passed automatically)
        path: path of folder/file to check
    """
    ctx.run(f"{python_exe} -m flake8 {path}", title="Checking code quality: flake8", capture=False)
    ctx.run(f"{python_exe} -m pylint {path}", title="Checking code quality: pylint", capture=False)


@duty
def unit_tests(ctx):
    """
    Runs unit tests
    Args:
        ctx: The context instance (passed automatically)
    """
    ctx.run([f"{python_exe}", "-m", "pytest", "-v", "--junit-xml", "unittests.xml","--cov", "QWeb"], title="Unit tests", capture=False)

@duty
def acceptance_tests(ctx,
                     browser="chrome",
                     excludes="jailed, FLASK, RESOLUTION_DEPENDENCY, WITH_DEBUGFILE",
                     other_options="--exitonfailure"):
    """
    Runs robot Acceptance tests
    Args:
        ctx: The context instance (passed automatically)
        browser: Browser name (use fullname instead of shorthand), [chrome, firefox, edge, safari]
                    Default: chrome
        excludes: CSV-list of tags to exclude. PROBLEM_IN_[OS, BROWSER] tagged tests are always excluded
                    Default: "jailed, FLASK, RESOLUTION_DEPENDENCY, WITH_DEBUGFILE"
        other_options: Any combination of Robot Framework command line options.
                          Example: "-v MYVAR:value -d custon/output/dir/ -t run_this_test -t also_run_this"
                          Default: "--exitonfailure"
                          
    """
    def remove_extra_whitespaces(string: str) -> str:
        return " ".join(string.split())

    cmd_excludes = f'-e {excludes.replace(",", " -e ")}'

    os = system().upper()
    if os == "DARWIN":
        os = "MACOS"

    cmd_str = remove_extra_whitespaces(
               f"{python_exe} -m robot "
               f"-v BROWSER:{browser} "
               f"-e PROBLEM_IN_{os} -e PROBLEM_IN_{browser} {cmd_excludes} "
               f"{other_options} "
               f"test/Acceptance"
            )

    ctx.run(cmd_str, title="Acceptance tests", capture=False)

@duty
def kw_docs(ctx):
    """
    Generates updated keyword docs
    Args:
        ctx: The context instance (passed automatically)
    """
    ctx.run([f"{python_exe}", "-m", "robot.libdoc", "-F", "REST", "QWeb", "./docs/QWeb.html"], title="Generating keyword documentation")

@duty
def create_dist(ctx):
    """
    Creates distribution packages
    Args:
        ctx: The context instance (passed automatically)
    """
    ctx.run(f"{python_exe} setup.py sdist bdist_wheel", title="Creating packages to ./dist", capture=False)
