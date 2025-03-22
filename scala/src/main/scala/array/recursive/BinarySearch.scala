package com.eureka
package array.recursive

import scala.annotation.tailrec

object BinarySearch:

  def search(nums: Array[Int], target: Int): Int =

    @tailrec def loop(start: Int, end: Int): Int =
      val mid = start + (end - start) / 2
      if start > end then -1
      else if nums(mid) == target then mid
      else if nums(mid) < target then loop(mid + 1, end)
      else loop(start, mid - 1)

    loop(0, nums.length - 1)
