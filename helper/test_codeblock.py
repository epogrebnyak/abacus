from codeblock import codeblock

assert """print("line with offset")""" in codeblock(
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
