# Functions with verbose/interactive guards - should not trigger CODE-02

safe_print <- function(x, verbose = FALSE) {
    if (verbose) cat("Processing...\n")
    if (interactive()) print("Interactive mode")
    x
}
