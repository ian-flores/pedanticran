# expect_equal(x, y, tolerance = 0) would be fragile on arm64
test_that("sums are close", {
  expect_equal(sum(c(0.1, 0.2)), 0.3, tolerance = 1e-8)
  expect_identical(nchar("tolerance = 0"), 13L)
})

ncores <- function() {
  if (Sys.info()[["sysname"]] == "SunOS") {
    system("/usr/sbin/psrinfo -p", intern = TRUE)
  } else {
    parallel::detectCores()
  }
}
