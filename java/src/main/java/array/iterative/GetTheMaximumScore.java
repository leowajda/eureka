package array.iterative;

public class GetTheMaximumScore {

    private static final int MODULO = 1_000_000_007;

    public int maxSum(int[] a, int[] b) {

        int aPtr    = 0;
        int bPtr    = 0;

        long bSum   = 0;
        long aSum   = 0;
        long maxSum = 0;

        while (aPtr < a.length && bPtr < b.length) {

            if (a[aPtr] == b[bPtr]) {
                maxSum += Math.max(aSum, bSum) + a[aPtr];

                aSum = bSum = 0;
                aPtr++;
                bPtr++;
                continue;
            }

            if (a[aPtr] < b[bPtr]) aSum += a[aPtr++];
            else                   bSum += b[bPtr++];
        }

        while (aPtr < a.length) aSum += a[aPtr++];
        while (bPtr < b.length) bSum += b[bPtr++];

        return (int) ((maxSum + Math.max(aSum, bSum)) % MODULO);
    }

}
