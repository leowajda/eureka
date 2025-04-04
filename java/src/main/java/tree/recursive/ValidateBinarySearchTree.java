package tree.recursive;

import tree.TreeNode;

public class ValidateBinarySearchTree {

    private boolean isValidBST(long min, TreeNode curr, long max) {
        return curr == null || ((min < curr.val && curr.val < max) && isValidBST(min, curr.left, curr.val) && isValidBST(curr.val, curr.right, max));
    }

    public boolean isValidBST(TreeNode root) {
        return isValidBST(Long.MIN_VALUE, root, Long.MAX_VALUE);
    }

}
