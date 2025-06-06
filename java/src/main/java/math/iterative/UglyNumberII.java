package math.iterative;

public class UglyNumberII {

    public int nthUglyNumber(int n) {

        int[] uglyNums     = new int[n];
        int[] indices      = new int[]{ 0, 0, 0 };
        int[] primeFactors = new int[]{ 2, 3, 5 };

        uglyNums[0] = 1;
        for (int i = 1; i < n; i++) {

            int min = Integer.MAX_VALUE;
            for (int j = 0; j < primeFactors.length; j++)
                min = Math.min(min, primeFactors[j] * uglyNums[indices[j]]);

            for (int j = 0; j < indices.length; j++)
                if ((primeFactors[j] * uglyNums[indices[j]]) == min)
                    indices[j]++;

            uglyNums[i] = min;
        }

        return uglyNums[n - 1];
    }

}
