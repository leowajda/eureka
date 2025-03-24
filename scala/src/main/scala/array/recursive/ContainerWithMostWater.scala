package com.eureka
package array.recursive

import scala.annotation.tailrec

object ContainerWithMostWater:

  extension (container: Array[Int])

    def area(from: Int, to: Int): Int =
      val min = if container(from) <= container(to) then from else to
      container(min) * (to - from)

  def maxArea(container: Array[Int]): Int =

    @tailrec def loop(left: Int, right: Int, maxArea: Int): Int =
      if left > right then return maxArea
      val currArea = container.area(left, right)
      if container(left) <= container(right) then loop(left + 1, right, maxArea max currArea)
      else loop(left, right - 1, maxArea max currArea)

    loop(0, container.length - 1, 0)
