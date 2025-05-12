package linked_list.iterative;

import linked_list.ListNode;

import java.util.*;

public class MergeKSortedLists {

    public ListNode mergeKLists(ListNode[] lists) {
        Queue<ListNode> queue = new PriorityQueue<>(Comparator.comparingInt(node -> node.val));
        Arrays.stream(lists).filter(Objects::nonNull).forEach(queue::add);

        ListNode head = new ListNode(-1);
        ListNode ptr  = head;

        while (!queue.isEmpty()) {
            var node     = queue.remove();
            var nextList = node.next;
            node.next    = null;
            ptr.next     = node;
            ptr          = ptr.next;
            if (nextList != null) queue.add(nextList);
        }

        return head.next;
    }

}
