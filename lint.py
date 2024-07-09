import subprocess


def run_black():
    print("Running black formatter...")
    result = subprocess.run(["black", "."], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)


def run_flake8():
    print("Running flake8 linter...")
    result = subprocess.run(
        ["flakeheaven", "lint", "src/"], capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)


if __name__ == "__main__":
    run_black()
    run_flake8()
    print("Done!")
