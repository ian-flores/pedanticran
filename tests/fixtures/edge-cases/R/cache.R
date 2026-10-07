cache_dir <- function() {
  tools::R_user_dir("edgepkg", which = "cache")
}

config_file <- function() {
  file.path(tools::R_user_dir("edgepkg", "config"), "settings.dcf")
}

# Remove files older than max_age days
cache_prune <- function(max_age = 30) {
  files <- list.files(cache_dir(), full.names = TRUE)
  old <- difftime(Sys.time(), file.mtime(files), units = "days") > max_age
  unlink(files[old])
}
