import tcp.FlagSet;

public class Serializer {
	private static final String DATA = "x";

	public static String concreteMessageToString(String flags, long seqNr,
												 long ackNr) {
		StringBuilder result = new StringBuilder();

		String[] flagArray = flags.split("\\+");
		for (String flag : flagArray) {
			result.append(Character.toUpperCase(flag.charAt(0)));
		}

		result.append(" ");
		result.append(seqNr);
		result.append(" ");
		result.append(ackNr);
		return result.toString();
	}

	public static String concreteMessageToString(invlang.types.FlagSet flags, long seqNr,
												 long ackNr, int payloadLength) {
		StringBuilder sb = new StringBuilder();
		FlagSet fs = new FlagSet(flags.toInitials());
		sb.append(fs.toString()).append("(").append(seqNr).append(",").append(ackNr).append(",").append(payloadLength).append(")");
		return sb.toString();
	}


	public static String concreteMessageToString(FlagSet flags, long seqNr,
												 long ackNr, int payloadLength) {
		StringBuilder sb = new StringBuilder();
		sb.append(flags.toString()).append("(").append(seqNr).append(",").append(ackNr).append(",").append(payloadLength).append(")");
		return sb.toString();
	}

	public static String abstractMessageToString(invlang.types.FlagSet flags,
												 String seqValidity, String ackValidity, int payloadLength) {
		StringBuilder sb = new StringBuilder();
		FlagSet fs = new FlagSet(flags.toInitials());
		sb.append(fs.toString()).append("(").append("?").append(",").append("?")
				.append(",").append(payloadLength).append(")");
		return sb.toString();
	}

	public static String abstractMessageToString(char[] flags,
												 String seqValidity, String ackValidity, int payloadLength) {
		StringBuilder sb = new StringBuilder();
		FlagSet fs = new FlagSet(flags);
		sb.append(fs.toString()).append("(").append("?").append(",").append("?")
				.append(",").append(payloadLength).append(")");
		return sb.toString();
	}
}
