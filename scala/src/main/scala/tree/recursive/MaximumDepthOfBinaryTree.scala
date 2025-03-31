package com.eureka
package tree.recursive

import tree.TreeNode

object MaximumDepthOfBinaryTree:

  def maxDepth(root: TreeNode): Int =
    if root == null then 0 else java.lang.Math.max(maxDepth(root.left), maxDepth(root.right)) + 1