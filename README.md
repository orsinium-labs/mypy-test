# mypy_test

Test [mypy](https://mypy.readthedocs.io/en/stable/) plugins, stubs, custom types.

Create a Python file, add comments to lines where you expect mypy to produce an error, run `mypy_test`, and it will check if actual errors are the same as you expect.

Features:

+ **Flexible**: supports every feature supported by mypy, does not enforce a project structure.
+ **Fast**: mypy gets run only once for all files at once. Also, no patching, no config generation.
+ **Easy to learn**: run `mypy_test` with the same arguments as you would run mypy, and it just works.
+ **Lightweight**: no dependencies except mypy.

```bash
python3 -m pip install mypy-test
```

## Usage

1. Write a file you want to test, add comments to the lines you expect to fail:

    ```python
    a = 1
    reveal_type(a)  # R: builtins.int
    ```

2. Run the tool:

    ```bash
    python3 -m mypy_test example.py
    ```

## Writing the comments

+ The comments have the following format: `SEVERITY: MESSAGE`.
+ Severity is a one-letter violation severity as reported by mypy.
  + `F` for "fatal"
  + `E` for "error"
  + `W` for "warning"
  + `N` for "note"
  + `R` is a shorthand for `N: Revealed type is "..."`
+ Comment can be on the same line as the violation or on the line before.

Example:

```python
var = 1.1
reveal_type(var)  # R: builtins.float

# E: Incompatible types in assignment (expression has type "str", variable has type "float")
var = ""
```

Tips:

+ The fastest way to know the severity and the message is to run `mypy_test` on the code and then copy-paste the resulting message.
+ Make separate functions for every test case, so it can have a nice description and a clean namespace.
+ Place all test files into one directory. For example, `/types/` or `/tests/types/`.

## Alternatives

+ [pytest-mypy-plugins](https://github.com/typeddjango/pytest-mypy-plugins) - pytest plugin, test cases described in a YAML file.
+ [pytest-mypy-testing](https://github.com/davidfritzsche/pytest-mypy-testing) - pytest plugin, tests are described like pytest test cases (but they actually don't get run).
