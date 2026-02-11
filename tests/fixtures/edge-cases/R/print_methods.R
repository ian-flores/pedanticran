#' Print Method for myclass
#'
#' @param x An object of class myclass.
#' @param ... Additional arguments.
#' @return Invisibly returns x.
#' @export
print.myclass <- function(x, ...) {
    cat("My Class Object:\n")
    print(x$data)
    invisible(x)
}

#' Format Method for myclass
#'
#' @param x An object of class myclass.
#' @param ... Additional arguments.
#' @return A character string.
#' @export
format.myclass <- function(x, ...) {
    paste("myclass:", x$data)
}
