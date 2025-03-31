package tree.recursive;

import tree.TreeNode;

public class SubtreeOfAnotherTree {

    private boolean isSame(TreeNode a, TreeNode b) {
        return (a == null || b == null) ? a == b : a.val == b.val && isSame(a.left, b.left) && isSame(a.right, b.right);
    }

    public boolean isSubtree(TreeNode root, TreeNode subRoot) {
        return root != null && (isSame(root, subRoot) || isSubtree(root.left, subRoot) || isSubtree(root.right, subRoot));
    }

}
