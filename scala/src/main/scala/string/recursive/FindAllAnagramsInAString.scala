package com.eureka
package string.recursive

import scala.annotation.tailrec

object FindAllAnagramsInAString:

  extension (s: String)

    def characterCount: Array[Int] =
      val counter = new Array[Int](26)
      s.foreach(ch => counter(ch - 'a') += 1)
      counter

  def findAnagrams(s: String, p: String): List[Int] =

    val anagramCount  = p.characterCount
    val anagramSize   = p.length
    val slidingWindow = new Array[Int](26)

    @tailrec def loop(left: Int, right: Int, anagrams: List[Int]): List[Int] =
      if right >= s.length then return anagrams
      slidingWindow(s(right) - 'a') += 1
      if right < anagramSize - 1 then return loop(left, right + 1, anagrams)
      val isValidAnagram = java.util.Arrays.equals(slidingWindow, anagramCount)
      slidingWindow(s(left) - 'a') -= 1
      loop(left + 1, right + 1, if isValidAnagram then left :: anagrams else anagrams)

    loop(0, 0, Nil)
