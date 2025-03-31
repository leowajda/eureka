package com.eureka
package tree.recursive

import tree.TreeNode

object BalancedBinaryTree:

  def isBalanced(_root: TreeNode): Boolean =

    def depth(root: TreeNode): Int =
      if root == null then return 0
      val leftDepth  = depth(root.left)
      val rightDepth = depth(root.right)

      if leftDepth == -1 || rightDepth == -1 then -1
      else if java.lang.Math.abs(leftDepth - rightDepth) > 1 then -1
      else java.lang.Math.max(leftDepth, rightDepth) + 1

    depth(_root) != -1
