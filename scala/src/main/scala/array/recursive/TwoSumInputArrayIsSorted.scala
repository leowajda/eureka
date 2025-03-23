package com.eureka
package array.recursive

import scala.annotation.tailrec

object TwoSumInputArrayIsSorted:

  def twoSum(nums: Array[Int], target: Int): Array[Int] =

    @tailrec def loop(left: Int, right: Int): Array[Int] =
      if left >= right then return Array(-1, -1)
      val sum = nums(left) + nums(right)
      if sum == target then Array(left + 1, right + 1)
      else if sum > target then loop(left, right - 1)
      else loop(left + 1, right)

    loop(0, nums.length - 1)
