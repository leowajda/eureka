package tree.recursive;

import tree.TreeNode;

public class InvertBinaryTree {

    public TreeNode invertTree(TreeNode root) {
        if (root == null) return null;
        var leftTree = invertTree(root.left);
        root.left    = invertTree(root.right);
        root.right   = leftTree;
        return root;
    }

}
