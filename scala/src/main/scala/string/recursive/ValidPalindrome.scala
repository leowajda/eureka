package com.eureka
package string.recursive

import scala.annotation.tailrec

object ValidPalindrome:

  def isPalindrome(s: String): Boolean =

    @tailrec def loop(left: Int, right: Int): Boolean =
      if left >= right then return true

      val lChar = s(left)
      val rChar = s(right)
      if !lChar.isLetterOrDigit then loop(left + 1, right)
      else if !rChar.isLetterOrDigit then loop(left, right - 1)
      else if lChar.toLower == rChar.toLower then loop(left + 1, right - 1)
      else false

    loop(0, s.length - 1)
