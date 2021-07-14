a = 1
reveal_type(a)  # R: builtins.int

b = 1.1
reveal_type(b)  # R: builtins.float

# E: Incompatible types in assignment (expression has type "str", variable has type "float")
b = ""
