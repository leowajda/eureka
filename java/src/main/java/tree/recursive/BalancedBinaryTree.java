package tree.recursive;

import tree.TreeNode;

public class BalancedBinaryTree {

    private static final int IMBALANCED_TREE = -1;

    private int helper(TreeNode root) {
        if (root == null)
            return 0;

        int leftDepth = helper(root.left);
        if (leftDepth == IMBALANCED_TREE)
            return IMBALANCED_TREE;

        int rightDepth = helper(root.right);
        if (rightDepth == IMBALANCED_TREE)
            return IMBALANCED_TREE;

        if (Math.abs(rightDepth - leftDepth) > 1)
            return IMBALANCED_TREE;

        return Math.max(rightDepth, leftDepth) + 1;
    }

    public boolean isBalanced(TreeNode root) {
        return helper(root) != IMBALANCED_TREE;
    }

}
