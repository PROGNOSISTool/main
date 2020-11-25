package util;

/**
 * Calculator class used for generating random numbers and generating random numbers within a given interval. It can apply a bias to 
 * its selection, so numbers near the borders are chosen more frequently.
 */
public class Calculator {
	public static final long MAX_NUM = (long) (Math.pow(2, 32) - 1);
	public static long newValue() {
		return (long) (Math.random() * MAX_NUM);
	}

	public static long newOtherThan(long value) {
		long newValue = 0;
		do {
			newValue = newValue();
		} while (newValue == value);
		return newValue;
	}
	
	public static long nth(long regValue, long n) {
		return sum(regValue, n);
	}

	public static long next(long regValue) {
		return sum(regValue,1);
	}
	
	public static long prev(long regValue) {
		return sub(regValue,1);
	}
	
	public static long sum(long op1, long op2) {
		long rez = (op1 + op2) % (MAX_NUM + 1);
		if ( rez < 0) {
			rez = MAX_NUM + 1 - Math.abs(rez);
		}
		return rez;
	}
	
	public static long sub(long op1, long op2) {
		return sum(op1, (-1) * op2);
	}

	/**
	 * Gen. random number within a set of intervals
	 */
	public static long randWithinRanges(long [] ... ranges) { 
		long rand;
		int randIndex;
		long [] rands = new long [ranges.length];
		for (int i = 0; i < ranges.length; i ++) {
			rands[i] = randWithinRange(ranges[i][0], ranges[i][1]);
		}
		randIndex = (int)randWithinRange(0, ranges.length/2);
		rand = rands[randIndex];
		return rand;
	}
	
	public static long randWithinRanges(long boundaryProximity, long nearBoundaryBias, long [] ... ranges) { 
		long rand;
		int randIndex;
		long [] rands = new long [ranges.length];
		for (int i = 0; i < ranges.length; i ++) {
			rands[i] = randWithinRange(ranges[i][0], ranges[i][1], boundaryProximity, nearBoundaryBias);
		}
		randIndex = (int)randWithinRange(0, ranges.length/2);
		rand = rands[randIndex];
		return rand;
	}
	
	/**
	 * Gen. 
	 * @param rangeMin
	 * @param rangeMax
	 * @param boundaryProximity
	 * @param nearBoundaryBias chance that a value near a boundary is picked instead of the randomly selected value
	 * @return
	 */
	public static long randWithinRange(long rangeMin, long rangeMax, long boundaryProximity, long nearBoundaryBias) {
		//System.out.println("[" + rangeMin + "-"+ rangeMax + "]");
		long rand;
		if(rangeMax > rangeMin) {
			long span = rangeMax - rangeMin;
			rand = sum((long)  (Math.random() * span + 0.5), rangeMin);
			double chance = Math.random(); 
			rand = 	(chance < 1 - nearBoundaryBias) ? rand : 
					(chance < 1 - nearBoundaryBias/2) ? rangeMin + ((long) ((boundaryProximity + 1) * Math.random())%span) :
						rangeMax - ((long) ((boundaryProximity + 1) * Math.random())%span);
		} else {
			if(rangeMin == rangeMax) {
				rand = rangeMin;
			} else {
				rand = randWithinRanges(boundaryProximity, nearBoundaryBias, new long [] {rangeMin, MAX_NUM}, new long[] {0, rangeMax});
			}
		}
		return rand;
	}
	
	/**
	 * Gen. random number within one interval 
	 */
	public static long randWithinRange(long rangeMin, long rangeMax) {
		return randWithinRange(rangeMin, rangeMax, 0, 0);
	}
	
	public static void main(String[] args) {
		System.out.println(randWithinRange(100000,10));	 
		for(int i = 0; i < 100; i ++)
			System.out.println(randWithinRanges(new long [] {0, 100},new long [] {100, 200}));;
	}
	
}
