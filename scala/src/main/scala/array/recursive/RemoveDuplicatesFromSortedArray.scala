package com.eureka
package array.recursive

import scala.annotation.tailrec

object RemoveDuplicatesFromSortedArray:

  def removeDuplicates(nums: Array[Int]): Int =

    @tailrec def loop(left: Int, right: Int): Int =
      if right == nums.length then left + 1
      else if nums(left) == nums(right) then loop(left, right + 1)
      else
        nums(left + 1) = nums(right)
        loop(left + 1, right + 1)

    loop(0, 0)
