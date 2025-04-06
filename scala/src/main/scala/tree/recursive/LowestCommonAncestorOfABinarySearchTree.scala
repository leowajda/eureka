package com.eureka
package tree.recursive

import tree.TreeNode

import scala.annotation.tailrec

object LowestCommonAncestorOfABinarySearchTree:

  def lowestCommonAncestor(_root: TreeNode, p: TreeNode, q: TreeNode): TreeNode =

    @tailrec def go(root: TreeNode, min: Int, max: Int): TreeNode =
      if root == null || root.value == min || root.value == max then root
      else if min < root.value && root.value < max then root
      else go(if root.value > max then root.left else root.right, min, max)

    go(_root, math.min(p.value, q.value), math.max(p.value, q.value))
