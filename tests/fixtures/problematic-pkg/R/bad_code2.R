# CODE-05: library/require in package code (this is detected by check_code as CODE-05 is about warn=-1)
# Actually library/require is not checked directly but let's add rm(list=ls())

cleanup <- function() {
    # CODE-09: rm(list = ls())
    rm(list = ls())
}

# NS-09: ::: into the package's own namespace
call_own_internal <- function(x) {
  badpkg:::internal_helper(x)
}
