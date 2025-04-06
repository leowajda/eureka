package tree.recursive;

import tree.TreeNode;

public class LowestCommonAncestorOfABinaryTree {

    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode a, TreeNode b) {
        if (root == null || root.val == a.val || root.val == b.val) return root;
        var left  = lowestCommonAncestor(root.left, a, b);
        var right = lowestCommonAncestor(root.right, a, b);
        return (left != null && right != null) ? root : (left != null ? left : right);
    }

}
