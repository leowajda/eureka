package com.eureka
package string.recursive

object LetterCombinationsOfAPhoneNumber:

  private val phone = Map(
    '2' -> List("a", "b", "c"),
    '3' -> List("d", "e", "f"),
    '4' -> List("g", "h", "i"),
    '5' -> List("j", "k", "l"),
    '6' -> List("m", "n", "o"),
    '7' -> List("p", "q", "r", "s"),
    '8' -> List("t", "u", "v"),
    '9' -> List("w", "x", "y", "z")
  );

  def letterCombinations(digits: String): List[String] = digits match
    case digit if digit.length <= 1 => digit.headOption.fold(Nil)(phone)
    case digits                     =>
      for
        tailCombination <- letterCombinations(digits.tail)
        letter          <- phone(digits.head)
      yield s"$letter$tailCombination"
