# Display helper functions where cat() is legitimate

cat_line <- function(x, ...) {
    cat(x, "\n", sep = "")
}

show_results <- function(results) {
    cat("Results:\n")
    for (r in results) {
        cat(" -", r, "\n")
    }
}
