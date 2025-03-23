package com.eureka
package array.recursive

import scala.annotation.tailrec

object MoveZeroes:

  extension [T](array: Array[T])

    def swap(from: Int, to: Int): Unit =
      val tmp = array(from)
      array(from) = array(to)
      array(to) = tmp

  def moveZeroes(nums: Array[Int]): Unit =

    @tailrec def loop(left: Int, right: Int): Unit =
      if right == nums.length then ()
      else if nums(right) == 0 then loop(left, right + 1)
      else
        nums.swap(left, right)
        loop(left + 1, right + 1)

    loop(0, 0)
