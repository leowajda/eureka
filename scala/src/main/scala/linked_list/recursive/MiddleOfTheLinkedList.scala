package com.eureka
package linked_list.recursive

import linked_list.ListNode

import scala.annotation.tailrec

object MiddleOfTheLinkedList:

  def middleNode(head: ListNode): ListNode =
    @tailrec def loop(slow: ListNode, fast: ListNode): ListNode =
      if fast == null || fast.next == null then slow else loop(slow.next, fast.next.next)
    loop(head, head)
