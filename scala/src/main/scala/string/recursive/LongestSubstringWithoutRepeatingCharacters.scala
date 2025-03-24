package com.eureka
package string.recursive

import scala.annotation.tailrec
import scala.collection.mutable

object LongestSubstringWithoutRepeatingCharacters:

  def lengthOfLongestSubstring(s: String): Int =

    @tailrec def loop(left: Int, right: Int, longestSubstring: Int, slidingWindow: mutable.Set[Char]): Int =
      if right >= s.length then return longestSubstring
      val leftChar  = s(left)
      val rightChar = s(right)

      if !slidingWindow(rightChar) then
        loop(left, right + 1, scala.math.max(longestSubstring, right - left + 1), slidingWindow += rightChar)
      else
        loop(left + 1, right, longestSubstring, slidingWindow -= leftChar)

    loop(0, 0, 0, mutable.Set.empty)
