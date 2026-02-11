#' Do Something Bad
#'
#' @export
do_bad <- function(x) {
    # CODE-01: T/F instead of TRUE/FALSE
    result <- ifelse(x > 0, T, F)

    # CODE-02: print/cat instead of message
    print("Starting computation")
    cat("Processing...\n")

    # CODE-03: set.seed in function
    set.seed(42)

    # CODE-04: options without on.exit
    options(warn = 2)

    # CODE-05: options(warn = -1)
    options(warn = -1)

    # CODE-06: getwd() usage
    path <- getwd()

    # CODE-08: installed.packages()
    pkgs <- installed.packages()

    # CODE-09: <<- global assignment
    global_var <<- 42

    # CODE-11: q()/quit()
    if (FALSE) q()

    # CODE-13: install.packages
    if (FALSE) install.packages("foo")

    # CODE-15: browser()
    browser()

    result
}

# CODE-12: ::: to base package
get_internal <- function() {
    base:::some_internal_fn()
}
