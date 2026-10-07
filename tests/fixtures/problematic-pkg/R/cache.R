cache_dir <- function() {
  tools::R_user_dir("badpkg", which = "cache")
}

cache_download <- function(url) {
  dest <- file.path(cache_dir(), basename(url))
  if (!file.exists(dest)) utils::download.file(url, dest)
  dest
}
