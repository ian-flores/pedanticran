# edgepkg:::helper() in a comment is fine
get_rcpp_flags <- function() {
  msg <- "do not call edgepkg:::helper() from package code"
  stats::setNames(Rcpp:::CxxFlags, msg)
}

# Backtick-quoted names that contain ::: are names, not calls
group_info <- list(`edgepkg:::current_group_id` = 0L)
