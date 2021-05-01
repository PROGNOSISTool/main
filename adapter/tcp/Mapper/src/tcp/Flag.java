package tcp;

import java.util.LinkedHashSet;
import java.util.Set;

public enum Flag {
	SYN,
	ACK,
	RST,
	FIN,
	PSH,
	UNKNOWN;

	public char initial() {
		return name().charAt(0);
	}

	public static Set<Flag> parseFlags(String flags) {
		Set<Flag> flagSet = new LinkedHashSet<Flag>();
		if(flags != null) {
			String uppedFlags = flags.toUpperCase();
			String[] flagStrings = uppedFlags.split("\\+");
			for (String flagString : flagStrings) {
				if(flagString.equals("_")) {
					flagSet.add(Flag.UNKNOWN);
				} else {
					flagSet.add(Flag.valueOf(flagString));
				}
			}
		}
		return flagSet;
	}

	public static Flag getFlagWithInitial(char flagInitial) {
		Flag searchedFlag = null;
		for(Flag flag : Flag.values()) {
			if(flag.name().startsWith(Character.toString(flagInitial))) {
				searchedFlag = flag;
				break;
			}
		}
		return searchedFlag;
	}

	public boolean matches(Flag flag) {
		return this.equals(flag) || flag == Flag.UNKNOWN;
	}

	public boolean matches(String flag) {
		return this.equals(flag) || Flag.UNKNOWN.equals(flag);
	}
}
