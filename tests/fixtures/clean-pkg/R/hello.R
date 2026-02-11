#' Greet the User
#'
#' @param name Character string with the name to greet.
#' @return A character string with the greeting.
#' @export
#' @examples
#' hello("World")
hello <- function(name = "World") {
    paste("Hello,", name)
}
