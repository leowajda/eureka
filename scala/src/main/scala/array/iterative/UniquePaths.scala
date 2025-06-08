package com.eureka
package array.iterative

object UniquePaths:

  def uniquePaths(rows: Int, cols: Int): Int =
    val memo = Array.fill(cols)(1)

    for
      _   <- 1 until rows
      col <- 1 until cols
    do memo(col) += memo(col - 1)

    memo(cols - 1)
