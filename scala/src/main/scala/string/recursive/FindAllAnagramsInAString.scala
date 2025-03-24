package com.eureka
package string.recursive

import scala.annotation.tailrec

object FindAllAnagramsInAString:

  extension (s: String)

    def characterCount(end: Int): Array[Int] =
      val counter = new Array[Int](26)
      (0 until end).foreach(idx => counter(s(idx) - 'a') += 1)
      counter

  def findAnagrams(s: String, p: String): List[Int] =

    if p.length > s.length then return Nil

    val anagramSize   = p.length
    val anagramCount  = p.characterCount(anagramSize)
    val slidingWindow = s.characterCount(anagramSize - 1)

    @tailrec def loop(left: Int, right: Int, anagrams: List[Int]): List[Int] =
      if right >= s.length then return anagrams
      slidingWindow(s(right) - 'a') += 1
      val isValidAnagram = java.util.Arrays.equals(slidingWindow, anagramCount)
      slidingWindow(s(left) - 'a') -= 1
      loop(left + 1, right + 1, if isValidAnagram then left :: anagrams else anagrams)

    loop(0, anagramSize - 1, Nil)