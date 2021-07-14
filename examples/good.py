a = 1
reveal_type(a)  # R: int

b = 1.1
reveal_type(b)  # R: float

# E: Incompatible types in assignment (expression has type "str", variable has type "float")
b = ""
