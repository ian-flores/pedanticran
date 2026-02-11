# This file has problematic patterns in comments only
# They should NOT trigger findings

# T and F are fine in comments
# print("this is a comment")
# library(foo)
# set.seed(42)
# options(warn = -1)
# browser()
# q()

safe_function <- function(x) {
    # <<- in a comment
    x + 1
}
