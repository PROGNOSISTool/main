import invlang.mapperReader.InvLangHandler;
import invlang.semantics.programTree.expressionTree.Expression;
import invlang.types.EnumValue;
import invlang.types.FlagSet;

import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import tcp.Flag;

public class Mapper implements MapperInterface {
	protected final class Inputs {
		protected static final String
				FLAGS = "flagsIn",
				CONC_SEQ = "concSeqIn",
				CONC_ACK = "concAckIn",
				ABS_SEQ = "absSeqIn",
				ABS_ACK = "absAckIn",
				CONC_DATA = "concDataIn",
				TMP = "tmp";
	}
	protected final class Outputs {
		protected static final String
				FLAGS_OUT = "flagsOut",
				FLAGS_OUT_2 = "flagsOut2",
				ABS_SEQ = "absSeqOut",
				ABS_ACK = "absAckOut",
				ABS_DATA = "absDataOut",
				CONC_SEQ = "concSeqOut",
				CONC_ACK = "concAckOut",
				CONC_DATA = "concDataOut",
				UNDEF = "undefined",
				TIMEOUT = "TIMEOUT";
	}
	protected final class Mappings{
		protected static final String
				INCOMING_RESPONSE = "incomingResponse",
				OUTGOING_REQUEST = "outgoingRequest",
				INCOMING_TIMEOUT = "incomingTimeout";
	}
	protected final class Enums {
		protected static final String
				IN = "absin";
	}
	protected static final String DEFAULT_MAPPER_PATH = "input/mappers/";

	public enum Validity {
		VALID("VALID", "V"), INVALID("INV", "INV");

		private final String invlangRepresentation, learnerInput;

		private Validity(String invlangRepresentation, String learnerInput) {
			this.invlangRepresentation = invlangRepresentation;
			this.learnerInput = learnerInput;
		}

		public static Validity getValidity(String learnerInput) {
			for (Validity v : Validity.values()) {
				if (v.learnerInput.equals(learnerInput)) {
					return v;
				}
			}
			throw new RuntimeException("Unknown input validity '" + learnerInput + "'");
		}

		public String toInvLang() {
			return this.invlangRepresentation;
		}
	}

	public static final int NOT_SET = -3;

	protected final InvLangHandler handler;
	private Expression lastConstraints; // for debugging purposes only

	public Mapper() throws IOException {
		try (InputStream is = this.getClass().getClassLoader().getResourceAsStream("linux.map")) {
			assert is != null;
			try (InputStreamReader isr = new InputStreamReader(is);
				 BufferedReader reader = new BufferedReader(isr)) {
				String mapper = reader.lines().collect(Collectors.joining(System.lineSeparator()));
				handler = new InvLangHandler(mapper, null);
			}
		}
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#getState()
	 */
	@Override
	public Map<String, Object> getState() {
		// create a new map, in which all (signed) integers are converted to unsigned, and unset integers are set to '?'
		Map<String, Object> state = new HashMap<>(this.handler.getState());
		for (Entry<String, Object> entry : this.handler.getState().entrySet()) {
			if (entry.getValue() instanceof Integer) {
				int value = (Integer) entry.getValue();
				if (value == Mapper.NOT_SET) {
					state.put(entry.getKey(), "?");
				} else {
					state.put(entry.getKey(), Mapper.getUnsignedInt(value));
				}
			}
		}
		return state;
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#processIncomingResponse(invlang.types.FlagSet, int, int, int)
	 */
	@Override
	public String processIncomingResponse(FlagSet flags, long seqNr, long ackNr, int payloadLength) {
		handler.setFlags(Inputs.FLAGS, flags);
		handler.setInt(Inputs.CONC_DATA, payloadLength);
		handler.setInt(Inputs.CONC_SEQ, (int) seqNr);
		handler.setInt(Inputs.CONC_ACK, (int) ackNr);
		handler.execute(Mappings.INCOMING_RESPONSE);
		EnumValue absSeq = handler.getEnumResult(Inputs.ABS_SEQ);
		EnumValue absAck = handler.getEnumResult(Inputs.ABS_ACK);
		return Serializer.abstractMessageToString(flags, absSeq.getValue(), absAck.getValue(), payloadLength);
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#processIncomingTimeout()
	 */
	@Override
	public String processIncomingTimeout() {
		handler.setInt(Inputs.TMP, 0); // invlang-thing: functions need at least 1 argument
		handler.execute(Mappings.INCOMING_TIMEOUT);
		return Outputs.TIMEOUT;
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#processOutgoingRequest(invlang.types.FlagSet, java.lang.String, java.lang.String, int)
	 */
	@Override
	public String processOutgoingRequest(FlagSet flags, String absSeq, String absAck, int payloadLength) {
		return processOutgoingRequest(flags, Validity.getValidity(absSeq), Validity.getValidity(absAck), payloadLength);
	}

	private String processOutgoingRequest(FlagSet flags, Validity absSeq, Validity absAck, int payloadLength) {
		handler.setFlags(Outputs.FLAGS_OUT_2, flags);
		handler.setEnum(Outputs.ABS_SEQ, Enums.IN, absSeq.toInvLang());
		handler.setEnum(Outputs.ABS_ACK, Enums.IN, absAck.toInvLang());
		handler.setInt(Outputs.ABS_DATA, payloadLength);

		this.lastConstraints = handler.executeInverted(Mappings.OUTGOING_REQUEST);
		if (handler.hasResult()) {
			int concSeq = handler.getIntResult(Outputs.CONC_SEQ);
			int concAck = handler.getIntResult(Outputs.CONC_ACK);
			long lConcSeq = getUnsignedInt(concSeq), lConcAck = getUnsignedInt(concAck);
			return Serializer.concreteMessageToString(flags, lConcSeq, lConcAck, payloadLength);
		} else {
			return Outputs.UNDEF;
		}
	}

	private Expression getLastConstraints() {
		return this.lastConstraints;
	}

	/**
	 * Reads an int (which is always signed in java) as unsigned,
	 * stored in a long
	 * @param x
	 * @return
	 */
	protected static long getUnsignedInt(int x) {
		return x & 0x00000000ffffffffL;
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#processOutgoingAction(java.lang.String)
	 */
	@Override
	public String processOutgoingAction(String action) {
		return action.toLowerCase();
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#sendReset()
	 */
	@Override
	public void sendReset() {
		this.handler.reset();
		this.handler.reset();
	}

	/* (non-Javadoc)
	 * @see sutInterface.tcp.MapperInterface#processOutgoingReset()
	 */
	@Override
	public String processOutgoingReset() {
		long learnerSeq = getUnsignedInt((int)this.handler.getState().get("learnerSeq"));
		return (learnerSeq == NOT_SET)? null : Serializer.concreteMessageToString(new tcp.FlagSet(Flag.RST), learnerSeq, 0, 0);
	}

	public static void main(String[] args) throws IOException {
		Mapper mapper = new Mapper();
		while (true) {
			Scanner scanner = new Scanner(System.in);
			String command = scanner.nextLine();

			if (command.equals("RESET")) {
				System.out.println(mapper.processOutgoingReset());
				mapper.sendReset();
			} else if (command.equals("STOP")) {
				return;
			}else {
				String[] request = command.split(" ");
				String patternString = "([A-Z+]+)\\(([0-9?]+),([0-9?]+),([0-9?]+)\\)";
				Pattern pattern = Pattern.compile(patternString);
				Matcher matcher = pattern.matcher(command);
				while(matcher.find()) {
					if (request[0].equals("ABSTRACT")) {
						int payloadLength = 0;
						if (!matcher.group(4).equals("?")) {
							payloadLength = Integer.parseInt(matcher.group(4));
						}
						System.out.println(mapper.processOutgoingRequest(new FlagSet(matcher.group(1)), Validity.VALID, Validity.VALID, payloadLength));
					} else if (request[0].equals("CONCRETE")) {
						System.out.println(mapper.processIncomingResponse(new FlagSet(matcher.group(1)), Long.parseLong(matcher.group(2)), Long.parseLong(matcher.group(3)), Integer.parseInt(matcher.group(4))));
					} else {
						System.err.println("Got invalid request type: " + request[0]);
						return;
					}
				}
			}
		}
	}
}
