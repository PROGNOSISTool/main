package tcp;

public enum Symbol {
	SNCLIENT,
	SNCLIENTP1,
	SNCLIENTP2,
	SNCLIENTPD,
	SNSERVER,
	SNSERVERP1,
	SNSERVERP2,
	SNSERVERPD,
	ANSENT,
	SNSENT,
	SNPSENT,
	FRESH,
	ZERO,
	RAND,
	V,
	INV,
	IWIN,
	OWIN,
	WIN,
	UNDEFINED,
	P1,
	M1,
	P2,
	M2,
	SIMULTANEOUS,
	UNKNOWN;

	public String toString(){
		return this.name().replace('P', '+');
	}

	public boolean is(Symbol symbol) {
		return this.equals(symbol);
	}

	public boolean equals(String str) {
		return this.toString().compareToIgnoreCase(str) == 0;
	}

	public boolean matches(Symbol symbol) {
		return this.equals(symbol) || symbol == Symbol.UNKNOWN;
	}

	public boolean matches(String symbol) {
		return this.equals(symbol) || Symbol.UNKNOWN.equals(symbol);
	}

	public static Symbol toSymbol(String str) {
		String newStr = str.toUpperCase().trim();
		newStr = newStr.replace('+', 'P');
		return Symbol.valueOf(newStr);
	}
}
