\name{make_counter}
\alias{make_counter}
\title{Make a Counter Closure}
\usage{
make_counter()
}
\value{
A list with increment and get functions.
}
\description{
Creates a counter function that uses <<- inside a closure.
}
\examples{
counter <- make_counter()
counter$increment()
counter$get()
}
