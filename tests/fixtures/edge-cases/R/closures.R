#' Make a Counter Closure
#'
#' Creates a counter function that uses <<- inside a closure.
#' This is valid R because <<- modifies the enclosing function scope,
#' not the global environment.
#'
#' @return A list with increment and get functions.
#' @export
#' @examples
#' counter <- make_counter()
#' counter$increment()
#' counter$get()
make_counter <- function() {
    count <- 0
    increment <- function() {
        count <<- count + 1
    }
    get <- function() {
        count
    }
    list(increment = increment, get = get)
}
