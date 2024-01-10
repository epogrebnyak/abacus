from codeblock import codeblock

assert """\nprint("line with offset")""" in codeblock(
    "python",
    """ 

    ```python
    print("line with offset")
    ```

    ```python
    print("another offset")
    ```
""",
)
