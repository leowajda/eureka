package tree.recursive;

import tree.TreeNode;

public class LowestCommonAncestorOfABinarySearchTree {

    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode a, TreeNode b) {
        return helper(root, Math.min(a.val, b.val) , Math.max(a.val, b.val));
    }

    private TreeNode helper(TreeNode root, int low, int high) {
        if (root == null || root.val == low || root.val == high) return root;
        if (low < root.val && root.val < high)                   return root;
        return helper(root.val > high ? root.left : root.right, low, high);
    }

}
