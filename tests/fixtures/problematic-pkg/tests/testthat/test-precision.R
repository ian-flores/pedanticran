test_that("sums are exact", {
  expect_equal(sum(c(0.1, 0.2)), 0.3,
               tolerance = 0)
  stopifnot(isTRUE(all.equal(mean(x), 1 / 3, tolerance = 0)))
})

ncores <- function() {
  if (grepl("darwin", R.version$os)) {
    system("sysctl -n hw.ncpu", intern = TRUE)
  } else {
    system("/usr/sbin/psrinfo -p", intern = TRUE)
  }
}
